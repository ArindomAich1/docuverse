from typing import List
from sqlalchemy.orm import Session
from app.models.document_chunk_model import DocumentChunk 

class DocumentChunkRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, document_chunk: DocumentChunk) -> DocumentChunk:
        self.db.add(document_chunk)
        self.db.flush()
        self.db.refresh(document_chunk)
        return document_chunk

    def save_all(self, document_chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        self.db.add_all(document_chunks)
        self.db.flush()
        for document_chunk in document_chunks:
            self.db.refresh(document_chunk)
        return document_chunks

    def get_parent_chunks_by_indices(
        self,
        document_id: int,
        parent_indices: list[int]
    ) -> list[DocumentChunk]:
        if not parent_indices:
            return []
        return (
            self.db.query(DocumentChunk)
            .filter(
                DocumentChunk.document_id == document_id,
                DocumentChunk.parent_index.in_(parent_indices)
            )
            .all()
        )