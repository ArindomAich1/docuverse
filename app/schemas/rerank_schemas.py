from dataclasses import dataclass

@dataclass(frozen=True)
class RerankResult:
    """A reranked sub-chunk, carries parent info through for hydration."""
    chunk_index: int
    parent_index: int
    document_id: int
    text: str
    rerank_score: float
