from sqlalchemy import Column, DateTime, Integer
from datetime import datetime

class AuditBase:

    status_id = Column(Integer, nullable=False, default=1)

    created_at = Column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False
    )


    deleted_at = Column(
        DateTime
    )

    created_by = Column(Integer, nullable=True)

    updated_by = Column(Integer, nullable=True)