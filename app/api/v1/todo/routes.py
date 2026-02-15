# =====================================
# Standard Library
# =====================================
from typing import List

# =====================================
# FastAPI
# =====================================
from fastapi import APIRouter, Depends, HTTPException, Query, status

# =====================================
# Database
# =====================================
from sqlalchemy.orm import Session
from app.core.database import get_db

# =====================================
# Local Schemas
# =====================================
from app.api.v1.todo.schemas import (
    TodoCreate,
    TodoUpdate,
    TodoOut,
)

# =====================================
# Service Layer
# =====================================
from app.api.v1.todo.services import (
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
    prefix="/todos",
    tags=["Todos"],
)


# =====================================
# Create Todo Endpoint
# =====================================
@router.post(
    "/",
    response_model=APIResponse[TodoOut],
    status_code=status.HTTP_201_CREATED,
    summary="Create todo",
    description="Create a new todo item",
)
def create(todo: TodoCreate, db: Session = Depends(get_db)):
    todo_obj = create_todo(db, todo)

    return APIResponse(
        data=todo_obj,
        message="Todo created successfully",
    )


# =====================================
# Get Todo by ID Endpoint
# =====================================
@router.get(
    "/{todo_id}",
    response_model=APIResponse[TodoOut],
    summary="Get todo by ID",
    description="Fetch a single todo by its ID",
)
def read(todo_id: int, db: Session = Depends(get_db)):
    todo = get_todo(db, todo_id)

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    return APIResponse(
        data=todo,
        message="Todo fetched successfully",
    )


# =====================================
# List Todos Endpoint
# =====================================
@router.get(
    "/",
    response_model=APIResponse[List[TodoOut]],
    summary="List todos",
    description="List todos with optional search and status filters",
)
def list_all(
    search: str | None = Query(
        None,
        description="Search in title or description",
    ),
    status_filter: str | None = Query(
        None,
        alias="status",
        description="Filter by status",
    ),
    skip: int = Query(
        0,
        ge=0,
        description="Number of records to skip",
    ),
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="Maximum records to return",
    ),
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
# Update Todo Endpoint
# =====================================
@router.put(
    "/{todo_id}",
    response_model=APIResponse[TodoOut],
    status_code=status.HTTP_200_OK,
    summary="Update todo",
    description="Update an existing todo",
)
def edit(todo_id: int, data: TodoUpdate, db: Session = Depends(get_db)):
    todo = get_todo(db, todo_id)

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    updated = update_todo(db, todo, data)

    return APIResponse(
        data=updated,
        message="Todo updated successfully",
    )

# =====================================
# Soft Delete Todo Endpoint
# =====================================
@router.delete(
    "/{todo_id}",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Delete todo",
    description="Soft delete a todo item",
)
def remove(todo_id: int, db: Session = Depends(get_db)):
    todo = get_todo(db, todo_id)

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    soft_delete_todo(db, todo)

    return APIResponse(
        message="Todo deleted successfully",
    )
