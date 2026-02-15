# =====================================
# Standard Library
# =====================================
from datetime import datetime
from typing import Optional, Literal

# =====================================
# Third-Party
# =====================================
from pydantic import BaseModel, Field


# =====================================
# Base Schema
# =====================================
class TodoBase(BaseModel):
    """Shared fields for Todo"""

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None

    status: Literal[
        "pending",
        "in_progress",
        "completed"
    ] = "pending"

    priority: Literal[
        "low",
        "medium",
        "high"
    ] = "medium"

    due_date: Optional[datetime] = None
    reminder_at: Optional[datetime] = None


# =====================================
# Create Schema
# =====================================
class TodoCreate(TodoBase):
    """Schema used when creating a todo"""
    pass


# =====================================
# Update Schema
# =====================================
class TodoUpdate(BaseModel):
    """Schema used when updating a todo (all optional)"""

    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200
    )

    description: Optional[str] = None
    status: Optional[Literal[
        "pending",
        "in_progress",
        "completed"
    ]] = None

    priority: Optional[Literal[
        "low",
        "medium",
        "high"
    ]] = None

    is_completed: Optional[bool] = None
    due_date: Optional[datetime] = None
    reminder_at: Optional[datetime] = None


# =====================================
# Response Schema
# =====================================
class TodoOut(TodoBase):
    """Schema returned in API responses"""

    id: int
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
