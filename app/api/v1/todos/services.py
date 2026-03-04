# =====================================
# Standard Library
# =====================================
from typing import Optional, Tuple, List

# =====================================
# SQLAlchemy
# =====================================
from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError

# =====================================
# Logger
# =====================================
from app.core.logger.logging import logger

# =====================================
# Custom Exceptions
# =====================================
from app.core.exceptions import (
    NotFoundException,
    InternalServerException,
    DomainValidationException,
)

# =====================================
# Local Imports
# =====================================
from app.api.v1.todos.models import Todo
from app.api.v1.todos.enums import TodoStatus
from app.api.v1.todos.schemas import TodoCreate, TodoUpdate


# =====================================
# Helper — Safe Commit
# =====================================
def _safe_commit(db: Session) -> None:
    try:
        db.commit()
        logger.debug("DB transaction committed")

    except SQLAlchemyError as e:
        db.rollback()
        logger.exception("DB transaction failed — rolled back")
        raise InternalServerException("Database transaction failed") from e


# =====================================
# Create Todo
# =====================================
def create_todo(db: Session, data: TodoCreate) -> Todo:
    logger.info("Creating new todo")

    try:
        todo = Todo(**data.model_dump())
        db.add(todo)

        _safe_commit(db)
        db.refresh(todo)

        logger.info("Todo created", extra={"todo_id": str(todo.id)})
        return todo

    except SQLAlchemyError as e:
        logger.exception("Create todo DB error")
        raise InternalServerException("Failed to create todo") from e


# =====================================
# Get Single Todo
# =====================================
def get_todo(db: Session, todo_id) -> Todo:
    logger.debug("Fetching todo", extra={"todo_id": str(todo_id)})

    try:
        todo = (
            db.query(Todo)
            .filter(
                Todo.id == todo_id,
                Todo.is_deleted == False
            )
            .first()
        )

    except SQLAlchemyError as e:
        logger.exception("Fetch todo DB error")
        raise InternalServerException("Failed to fetch todo") from e

    if not todo:
        logger.warning("Todo not found", extra={"todo_id": str(todo_id)})
        raise NotFoundException("Todo not found")

    return todo


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
        "Listing todos",
        extra={"search": search, "status": status, "skip": skip, "limit": limit},
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
            try:
                query = query.filter(Todo.status == TodoStatus(status))
            except ValueError:
                logger.warning("Invalid status filter", extra={"status": status})
                raise DomainValidationException("Invalid status value")

        total = query.count()

        items = (
            query.order_by(Todo.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        logger.debug("Todos listed", extra={"count": len(items), "total": total})
        return items, total

    except SQLAlchemyError as e:
        logger.exception("List todos DB error")
        raise InternalServerException("Failed to list todos") from e


# =====================================
# Update Todo
# =====================================
def update_todo(db: Session, todo_id, data: TodoUpdate) -> Todo:
    logger.info("Updating todo", extra={"todo_id": str(todo_id)})

    todo = get_todo(db, todo_id)

    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(todo, field, value)

    _safe_commit(db)
    db.refresh(todo)

    logger.info("Todo updated", extra={"todo_id": str(todo.id)})
    return todo


# =====================================
# Soft Delete Todo
# =====================================
def soft_delete_todo(db: Session, todo_id) -> None:
    logger.info("Soft deleting todo", extra={"todo_id": str(todo_id)})

    todo = get_todo(db, todo_id)

    todo.is_deleted = True
    _safe_commit(db)

    logger.info("Todo soft deleted", extra={"todo_id": str(todo.id)})
    