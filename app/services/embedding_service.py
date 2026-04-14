from sentence_transformers import SentenceTransformer
from pinecone_text.sparse import BM25Encoder
from pinecone import Pinecone
from app.config.config import settings
from app.schemas.chunk_schemas import SubChunk
from app.schemas.vector_schemas import PineconeVector, VectorMetadata


# Module-level singletons — loaded once at startup, reused across all requests
_embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
_pc          = Pinecone(api_key=settings.PINECONE_API_KEY)
_index       = _pc.Index(settings.PINECONE_INDEX_NAME)
_bm25_encoder = BM25Encoder.default()


class EmbeddingService:

    def _get_dense_vectors(self, texts: list[str]) -> list[list[float]]:
        return _embed_model.encode(texts, batch_size=32).tolist()

    def _get_sparse_vector(self, text: str) -> dict:
        return _bm25_encoder.encode_documents([text])[0]

    def upsert_chunks(
        self,
        document_id: int,
        user_id: int,
        chunks: list[SubChunk]
    ) -> None:
        if not chunks:
            return

        all_texts    = [c.text for c in chunks]
        dense_vecs   = self._get_dense_vectors(all_texts)

        vectors = []
        for chunk, dense in zip(chunks, dense_vecs):
            sparse = self._get_sparse_vector(chunk.text)

            vector = PineconeVector(
                id=f"doc_{document_id}_chunk_{chunk.chunk_index}",
                values=dense,
                sparse_values=sparse,
                metadata=VectorMetadata(
                    document_id=document_id,
                    user_id=user_id,
                    chunk_index=chunk.chunk_index,
                    parent_index=chunk.parent_index,
                    text=chunk.text
                )
            )
            vectors.append(vector.to_dict())

        # Pinecone hard limit: 100 vectors per upsert request
        for i in range(0, len(vectors), 100):
            _index.upsert(
                vectors=vectors[i: i + 100],
                namespace=str(user_id)
            )

    def delete_document_vectors(self, document_id: int, user_id: int) -> None:
        """Called on document soft delete to remove orphan vectors from Pinecone."""
        _index.delete(
            filter={"document_id": document_id},
            namespace=str(user_id)
        )