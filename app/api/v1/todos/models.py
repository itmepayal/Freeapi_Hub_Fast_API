# =====================================
# Standard Library
# =====================================
import uuid
from datetime import datetime

# =====================================
# SQLAlchemy
# =====================================
from sqlalchemy.orm import validates
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
from app.api.v1.todos.enums import TodoStatus, TodoPriority

# =====================================
# Todo Model
# =====================================
class Todo(Base, TimestampMixin):
    __tablename__ = "todos"
    
    __table_args__ = (
        Index("idx_todo_status_deleted", "status", "is_deleted"),
        Index("idx_todo_created", "created_at"),
    )

    # ---------------------------------
    # Primary Key
    # ---------------------------------
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

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


    # ---------------------------------
    # Scheduling
    # ---------------------------------
    due_date = Column(DateTime)
    reminder_at = Column(DateTime)

    # ---------------------------------
    # Property
    # ---------------------------------
    @property
    def is_completed(self) -> bool:
        return self.status == TodoStatus.completed

    # ---------------------------------
    # Validation
    # ---------------------------------
    @validates("status")
    def validate_status(self, key, value):
        if not isinstance(value, TodoStatus):
            raise ValueError(f"Invalid status: {value}")
        return value

    @validates("priority")
    def validate_priority(self, key, value):
        if not isinstance(value, TodoPriority):
            raise ValueError(f"Invalid priority: {value}")
        return value