# =====================================
# Standard Library
# =====================================
from datetime import datetime, UTC

# =====================================
# SQLAlchemy Column Types
# =====================================
from sqlalchemy import Column, DateTime, Boolean

# =====================================
# TimestampMixin
# =====================================
class TimestampMixin:
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False
    )

    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )