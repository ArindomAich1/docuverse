from app.schemas.base_schema import BaseSchema

class SubChunkResult(BaseSchema):
    """Raw result from Pinecone — a matched sub-chunk."""
    chunk_index: int
    parent_index: int
    document_id: int
    text: str
    score: float

class RetrievedContext(BaseSchema):
    """Hydrated parent chunk — final context fed to the LLM."""
    document_id: int
    parent_index: int
    text: str