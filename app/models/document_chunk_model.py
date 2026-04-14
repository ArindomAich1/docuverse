from app.models.audit_base import AuditBase
from sqlalchemy import Integer, Column, ForeignKey, Text
from app.db.base import Base

class DocumentChunk(Base, AuditBase):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    parent_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)