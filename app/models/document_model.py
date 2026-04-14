from sqlalchemy import String, Integer, Column, DateTime, ForeignKey
from app.models.audit_base import AuditBase
from app.db.base import Base

class Documents(Base, AuditBase):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    document_s3path = Column(String(255), nullable=False) 
    document_name = Column(String(255), nullable=False)
