from app.enums.row_status import RowStatus
from sqlalchemy.orm import Session
from app.models.document_model import Documents

class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, document: Documents) -> Documents:
        self.db.add(document)
        self.db.flush()
        self.db.refresh(document)
        return document

    def get_all_by_user(self, user_id: int) -> list[Documents]:
        return self.db.query(Documents).filter(
            Documents.user_id == user_id,
            Documents.status_id.in_([0, 1]) 
        ).all()

    def get_count_by_user(self, user_id: int) -> int:
        return self.db.query(Documents).filter(
            Documents.user_id == user_id,
            Documents.status_id.in_([0, 1])
        ).count()

    def get_document_by_id(self, user_id: int, document_id: int, status_id: int) -> Documents:
        return self.db.query(Documents).filter(
            Documents.id == document_id,
            Documents.user_id == user_id,
            Documents.status_id == RowStatus.ACTIVE.value
        ).first()