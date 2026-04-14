from sqlalchemy import String, Integer, Column, DateTime, ForeignKey
from app.models.audit_base import AuditBase
from app.db.base import Base

class OTP(Base, AuditBase):
    __tablename__ = "otp"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    otp = Column(String(4), nullable=False)
    expiration_time = Column(DateTime, nullable=False)
    operation_type = Column(Integer, nullable=False)