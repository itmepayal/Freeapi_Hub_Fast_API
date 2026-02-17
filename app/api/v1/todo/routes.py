# =====================================
# Standard Library
# =====================================
from uuid import UUID
from typing import List

# =====================================
# FastAPI
# =====================================
from fastapi import APIRouter, Depends, HTTPException, Query, status

# =====================================
# Database
# =====================================
from sqlalchemy.orm import Session
from app.core.db.connect import get_db

# =====================================
# Logger
# =====================================
from app.core.logger.logging import logger

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
    prefix="",
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
    logger.info("POST /todos — create request")

    todo_obj = create_todo(db, todo)

    logger.info(f"POST /todos — created id={todo_obj.id}")

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
def read(todo_id: UUID, db: Session = Depends(get_db)):
    logger.info(f"GET /todos/{todo_id}")

    todo = get_todo(db, todo_id)

    if not todo:
        logger.warning(f"Todo not found: {todo_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    logger.info(f"Todo fetched: {todo_id}")

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
    logger.info(
        f"GET /todos — list | search={search} status={status_filter} "
        f"skip={skip} limit={limit}"
    )

    items, total = list_todos(
        db,
        search=search,
        status=status_filter,
        skip=skip,
        limit=limit,
    )

    logger.info(f"GET /todos — returned={len(items)} total={total}")

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
def edit(todo_id: UUID, data: TodoUpdate, db: Session = Depends(get_db)):
    logger.info(f"PUT /todos/{todo_id} — update request")

    todo = get_todo(db, todo_id)

    if not todo:
        logger.warning(f"Update failed — not found {todo_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    updated = update_todo(db, todo, data)

    logger.info(f"PUT /todos/{todo_id} — updated")

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
def remove(todo_id: UUID, db: Session = Depends(get_db)):
    logger.info(f"DELETE /todos/{todo_id}")

    todo = get_todo(db, todo_id)

    if not todo:
        logger.warning(f"Delete failed — not found {todo_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    soft_delete_todo(db, todo)

    logger.info(f"DELETE /todos/{todo_id} — soft deleted")

    return APIResponse(
        message="Todo deleted successfully",
    )
