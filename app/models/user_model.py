from app.enums.user_types import UserType
from sqlalchemy import String, Integer, Column, Enum
from app.models.audit_base import AuditBase
from app.db.base import Base

class User(Base, AuditBase):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=True, index=True)
    email = Column(String(255), nullable=False)
    password_hash = Column(String(512), nullable=False)
    user_type = Column(Enum(UserType), nullable=False, default=UserType.USER)    