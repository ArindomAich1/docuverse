from app.enums.chat_roles import ChatRoles
from sqlalchemy import String, Integer, Column, ForeignKey, Enum, Text
from app.models.audit_base import AuditBase
from app.db.base import Base

class Chats(Base, AuditBase):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    role = Column(Enum(ChatRoles), nullable=False)
    content = Column(Text, nullable=False)