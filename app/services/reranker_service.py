from flashrank import Ranker, RerankRequest
from app.schemas.retrieval_schemas import SubChunkResult
from app.schemas.rerank_schemas import RerankResult


# ~90MB cross-encoder, loaded once at startup
_ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2", cache_dir="/tmp/flashrank")


class RerankerService:

    def rerank(
        self,
        query: str,
        sub_chunks: list[SubChunkResult],
        top_n: int = 5
    ) -> list[RerankResult]:
        if not sub_chunks:
            return []

        passages = [
            {
                "id": f"doc_{c.document_id}_chunk_{c.chunk_index}",
                "text": c.text,
                "meta": {
                    "chunk_index": c.chunk_index,
                    "parent_index": c.parent_index,
                    "document_id": c.document_id
                }
            }
            for c in sub_chunks
        ]

        results = _ranker.rerank(RerankRequest(query=query, passages=passages))

        return [
            RerankResult(
                chunk_index=r["meta"]["chunk_index"],
                parent_index=r["meta"]["parent_index"],
                document_id=r["meta"]["document_id"],
                text=r["text"],
                rerank_score=r["score"]
            )
            for r in results[:top_n]
        ]