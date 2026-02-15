# =====================================
# Standard Library
# =====================================
from datetime import datetime

# =====================================
# SQLAlchemy
# =====================================
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    Enum,
)
from sqlalchemy.orm import relationship

# =====================================
# Local Imports
# =====================================
from app.core.database import Base


# =====================================
# Todo Model
# =====================================
class Todo(Base):
    __tablename__ = "todos"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Core Fields
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)

    # Status & Priority
    status = Column(
        Enum(
            "pending",
            "in_progress",
            "completed",
            name="status_enum"
        ),
        default="pending",
        nullable=False
    )

    priority = Column(
        Enum(
            "low",
            "medium",
            "high",
            name="priority_enum"
        ),
        default="medium",
        nullable=False
    )

    is_completed = Column(Boolean, default=False)

    # Scheduling Fields
    due_date = Column(DateTime, nullable=True)
    reminder_at = Column(DateTime, nullable=True)

    # Audit Fields
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Soft Delete Flag
    is_deleted = Column(Boolean, default=False)
