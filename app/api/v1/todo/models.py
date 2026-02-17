# =====================================
# Standard Library
# =====================================
import uuid
from datetime import datetime

# =====================================
# SQLAlchemy
# =====================================
from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    DateTime,
    Enum,
    Index,
    ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

# =====================================
# Local Imports
# =====================================
from app.core.db.connect import Base
from app.models.mixins import TimestampMixin
from app.api.v1.todo.enums import TodoStatus, TodoPriority


# =====================================
# Todo Model
# =====================================
class Todo(Base, TimestampMixin):
    __tablename__ = "todos"

    __table_args__ = (
        Index("idx_todo_status", "status"),
        Index("idx_todo_created", "created_at"),
        # Index("idx_todo_user", "user_id"),
    )

    # ---------------------------------
    # Primary Key
    # ---------------------------------
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # ---------------------------------
    # Foreign Keys
    # ---------------------------------
    # user_id = Column(
    #     UUID(as_uuid=True),
    #     ForeignKey("users.id", ondelete="CASCADE"),
    #     nullable=False
    # )

    # ---------------------------------
    # Core Fields
    # ---------------------------------
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)

    # ---------------------------------
    # Status & Priority
    # ---------------------------------
    status = Column(
        Enum(TodoStatus, name="todo_status_enum"),
        default=TodoStatus.pending,
        nullable=False
    )

    priority = Column(
        Enum(TodoPriority, name="todo_priority_enum"),
        default=TodoPriority.medium,
        nullable=False
    )

    is_completed = Column(Boolean, default=False)

    # ---------------------------------
    # Scheduling
    # ---------------------------------
    due_date = Column(DateTime)
    reminder_at = Column(DateTime)

    # ---------------------------------
    # Relationships
    # ---------------------------------
    # owner = relationship("User", back_populates="todos")
