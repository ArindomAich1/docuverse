from sqlalchemy.orm import Session

from app.services.embedding_service import _embed_model, _bm25_encoder, _index
from app.services.reranker_service import RerankerService
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.schemas.retrieval_schemas import SubChunkResult, RetrievedContext


class RetrievalService:

    def __init__(self, db: Session):
        self.db = db
        self.chunk_repository = DocumentChunkRepository(db)
        self.reranker = RerankerService()

    # -------------------------------------------------------------------------
    # Private helpers
    # -------------------------------------------------------------------------

    def _build_filter(self, user_id: int, document_id: int | None) -> dict:
        """
        Always scoped to user_id — prevents cross-user data leakage.
        Optionally narrow to a single document for document-specific Q&A.
        """
        f = {"user_id": {"$eq": user_id}}
        if document_id is not None:
            f["document_id"] = {"$eq": document_id}
        return f

    def _query_pinecone(
        self,
        query: str,
        user_id: int,
        document_id: int | None,
        top_k: int
    ) -> list[SubChunkResult]:
        """
        Hybrid search: dense (semantic) + sparse (BM25 keyword).
        alpha=0.5 weights both equally — tune toward 1.0 for semantic-heavy
        queries or toward 0.0 for keyword-heavy queries.
        """
        dense_vector = _embed_model.encode(query).tolist()
        sparse_vector = _bm25_encoder.encode_queries(query)

        response = _index.query(
            vector=dense_vector,
            sparse_vector=sparse_vector,
            alpha=0.5,
            top_k=top_k,
            filter=self._build_filter(user_id, document_id),
            namespace=str(user_id),
            include_metadata=True
        )

        results = []
        for match in response.matches:
            meta = match.metadata
            results.append(SubChunkResult(
                chunk_index=int(meta["chunk_index"]),
                parent_index=int(meta["parent_index"]),
                document_id=int(meta["document_id"]),
                text=meta["text"],
                score=float(match.score)
            ))

        return results

    def _deduplicate_parents(
        self,
        reranked: list
    ) -> dict[int, list[int]]:
        """
        Multiple top-ranked sub-chunks may share the same parent.
        Collapse them before hitting MySQL — avoids duplicate parent
        fetches and redundant context in the LLM prompt.

        Returns: { document_id: [unique parent_indices] }
        """
        seen: set[tuple[int, int]] = set()
        parent_map: dict[int, list[int]] = {}

        for result in reranked:
            key = (result.document_id, result.parent_index)
            if key not in seen:
                seen.add(key)
                parent_map.setdefault(result.document_id, []).append(result.parent_index)

        return parent_map

    # -------------------------------------------------------------------------
    # Public API — called by ChatService
    # -------------------------------------------------------------------------

    def get_context(
        self,
        query: str,
        user_id: int,
        document_id: int | None = None,
        top_k: int = 20,
        top_n: int = 5
    ) -> list[RetrievedContext]:
        """
        Full pipeline: Hybrid Pinecone search → Rerank → Deduplicate → Hydrate.

        Args:
            query:       Raw user question string.
            user_id:     Namespace + filter isolation. Never skipped.
            document_id: None = search all user docs (general Q&A).
                         Set = restrict to one document (focused Q&A).
            top_k:       Candidates pulled from Pinecone (default 20).
            top_n:       Sub-chunks kept after reranking (default 5).
                         Keep top_k at least 4× top_n.

        Returns:
            Hydrated parent chunks ordered by rerank score, ready for LLM.
        """
        # Step 1 — Hybrid retrieval from Pinecone
        sub_chunks = self._query_pinecone(query, user_id, document_id, top_k)
        if not sub_chunks:
            return []

        # Step 2 — Cross-encoder reranking on sub-chunks
        reranked = self.reranker.rerank(query=query, sub_chunks=sub_chunks, top_n=top_n)
        if not reranked:
            return []

        # Step 3 — Deduplicate: collapse sub-chunks sharing the same parent
        parent_map = self._deduplicate_parents(reranked)

        # Step 4 — Hydrate parent chunks from MySQL
        contexts: list[RetrievedContext] = []
        for doc_id, parent_indices in parent_map.items():
            parent_chunks = self.chunk_repository.get_parent_chunks_by_indices(
                document_id=doc_id,
                parent_indices=parent_indices
            )
            for chunk in parent_chunks:
                contexts.append(RetrievedContext(
                    document_id=chunk.document_id,
                    parent_index=chunk.parent_index,
                    text=chunk.text
                ))

        return contexts