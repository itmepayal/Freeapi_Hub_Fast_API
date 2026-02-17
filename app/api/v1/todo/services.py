# =====================================
# Standard Library
# =====================================
from typing import Optional, Tuple, List

# =====================================
# FastAPI / SQLAlchemy
# =====================================
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError

# =====================================
# Logger
# =====================================
from app.core.logger.logging import logger

# =====================================
# Local Imports
# =====================================
from app.api.v1.todo.models import Todo
from app.api.v1.todo.schemas import TodoCreate, TodoUpdate


# =====================================
# Helper — Safe Commit
# =====================================
def _safe_commit(db: Session):
    try:
        db.commit()
        logger.debug("DB commit successful")

    except SQLAlchemyError as e:
        db.rollback()
        logger.warning("DB commit failed — rolled back")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database transaction failed"
        ) from e


# =====================================
# Create Todo
# =====================================
def create_todo(db: Session, data: TodoCreate) -> Todo:
    logger.info("Creating todo")
    
    try:
        todo = Todo(**data.model_dump())

        db.add(todo)
        _safe_commit(db)
        db.refresh(todo)

        logger.info(f"Todo created: {todo.id}")
        return todo

    except SQLAlchemyError as e:
        logger.warning("Create todo failed")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create todo"
        ) from e


# =====================================
# Get Single Todo
# =====================================
def get_todo(db: Session, todo_id) -> Optional[Todo]:
    logger.debug(f"Fetching todo {todo_id}")

    try:
        return (
            db.query(Todo)
            .filter(
                Todo.id == todo_id,
                Todo.is_deleted == False
            )
            .first()
        )

    except SQLAlchemyError as e:
        logger.warning("Fetch todo failed")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch todo"
        ) from e


# =====================================
# List Todos
# =====================================
def list_todos(
    db: Session,
    search: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
) -> Tuple[List[Todo], int]:

    logger.debug(
        f"Listing todos | search={search} status={status} skip={skip} limit={limit}"
    )

    try:
        query = db.query(Todo).filter(Todo.is_deleted == False)

        if search:
            query = query.filter(
                or_(
                    Todo.title.ilike(f"%{search}%"),
                    Todo.description.ilike(f"%{search}%")
                )
            )

        if status:
            query = query.filter(Todo.status == status)

        total = query.count()

        items = (
            query.order_by(Todo.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        logger.debug(f"Todos returned: {len(items)} / total={total}")
        return items, total

    except SQLAlchemyError as e:
        logger.warning("List todos failed")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list todos"
        ) from e


# =====================================
# Update Todo
# =====================================
def update_todo(db: Session, todo: Todo, data: TodoUpdate) -> Todo:
    logger.info(f"Updating todo {todo.id}")

    try:
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(todo, field, value)

        _safe_commit(db)
        db.refresh(todo)

        logger.info(f"Todo updated: {todo.id}")
        return todo

    except SQLAlchemyError as e:
        logger.warning("Update todo failed")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update todo"
        ) from e


# =====================================
# Soft Delete
# =====================================
def soft_delete_todo(db: Session, todo: Todo) -> None:
    logger.info(f"Soft deleting todo {todo.id}")

    try:
        todo.is_deleted = True
        _safe_commit(db)

        logger.info(f"Todo soft deleted: {todo.id}")

    except SQLAlchemyError as e:
        logger.warning("Soft delete failed")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete todo"
        ) from e
