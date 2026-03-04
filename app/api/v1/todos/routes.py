# =====================================
# Standard Library
# =====================================
from uuid import UUID
from typing import List

# =====================================
# FastAPI
# =====================================
from fastapi import APIRouter, Depends, Query, status

# =====================================
# Database
# =====================================
from sqlalchemy.orm import Session
from app.core.db.connect import get_db

# =====================================
# Schemas
# =====================================
from app.api.v1.todos.schemas import (
    TodoCreate,
    TodoUpdate,
    TodoOut,
)

# =====================================
# Services
# =====================================
from app.api.v1.todos.services import (
    create_todo,
    get_todo,
    list_todos,
    update_todo,
    soft_delete_todo,
)

# =====================================
# Response Wrapper
# =====================================
from app.utils.response import APIResponse


# =====================================
# Router Configuration
# =====================================
router = APIRouter(
    prefix="",
    tags=["Todos"],
)


# =====================================
# Create Todo
# =====================================
@router.post(
    "/",
    response_model=APIResponse[TodoOut],
    status_code=status.HTTP_201_CREATED,
)
def create(todo: TodoCreate, db: Session = Depends(get_db)):
    return APIResponse(
        data=create_todo(db, todo),
        message="Todo created successfully",
    )


# =====================================
# Get Todo by ID
# =====================================
@router.get(
    "/{todo_id}",
    response_model=APIResponse[TodoOut],
)
def read(todo_id: UUID, db: Session = Depends(get_db)):
    return APIResponse(
        data=get_todo(db, todo_id),
        message="Todo fetched successfully",
    )


# =====================================
# List Todos
# =====================================
@router.get(
    "/",
    response_model=APIResponse[List[TodoOut]],
)
def list_all(
    search: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = list_todos(
        db,
        search=search,
        status=status_filter,
        skip=skip,
        limit=limit,
    )

    return APIResponse(
        data=items,
        message=f"Total todos: {total}",
    )


# =====================================
# Update Todo
# =====================================
@router.put(
    "/{todo_id}",
    response_model=APIResponse[TodoOut],
)
def edit(todo_id: UUID, data: TodoUpdate, db: Session = Depends(get_db)):
    return APIResponse(
        data=update_todo(db, todo_id, data),
        message="Todo updated successfully",
    )


# =====================================
# Soft Delete Todo
# =====================================
@router.delete(
    "/{todo_id}",
    response_model=APIResponse[None],
)
def remove(todo_id: UUID, db: Session = Depends(get_db)):
    soft_delete_todo(db, todo_id)

    return APIResponse(
        message="Todo deleted successfully",
    )
    