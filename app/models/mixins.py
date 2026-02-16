# =====================================
# Standard Library
# =====================================
from datetime import datetime

# =====================================
# SQLAlchemy Column Types
# =====================================
from sqlalchemy import Column, DateTime, Boolean


# =====================================
# TimestampMixin
# =====================================
class TimestampMixin:

    # Timestamp when record is first created
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Timestamp updated automatically on every update
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Soft delete flag
    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
