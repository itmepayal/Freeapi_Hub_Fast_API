# =====================================
# Standard Library
# =====================================
from uuid import UUID
from datetime import datetime
from typing import Optional

# =====================================
# Third-Party
# =====================================
from pydantic import (
    BaseModel, 
    Field, 
    field_validator,
    ConfigDict
)

# =====================================
# Local
# =====================================
from app.api.v1.todos.enums import TodoStatus, TodoPriority  

# =====================================
# Base Schema
# =====================================
class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None

    status: TodoStatus = TodoStatus.pending
    priority: TodoPriority = TodoPriority.medium

    due_date: Optional[datetime] = None
    reminder_at: Optional[datetime] = None
    
    @field_validator("reminder_at")
    @classmethod
    def reminder_before_due(cls, v, info):
        due = info.data.get("due_date")
        
        if v and due and v > due:
            raise ValueError("Reminder must be before due date")

        return v

# =====================================
# Create Schema
# =====================================
class TodoCreate(TodoBase):
    pass

# =====================================
# Update Schema
# =====================================
class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None

    status: Optional[TodoStatus] = None
    priority: Optional[TodoPriority] = None

    due_date: Optional[datetime] = None
    reminder_at: Optional[datetime] = None
    
    @field_validator("reminder_at")
    @classmethod
    def reminder_before_due(cls, v, info):
        due = info.data.get("due_date")

        if v and due and v > due:
            raise ValueError("Reminder must be before due date")

        return v

# =====================================
# Response Schema
# =====================================
class TodoOut(TodoBase):
    id: UUID
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
