import uuid
import pytest

# =====================================
# Service Imports
# =====================================
from app.api.v1.todos.services import (
    create_todo,
    get_todo,
    list_todos,
    update_todo,
    soft_delete_todo,
)
from app.api.v1.todos.schemas import TodoCreate, TodoUpdate
from app.api.v1.todos.enums import TodoStatus
from app.core.exceptions import NotFoundException, DomainValidationException

# =====================================
# Integration Tests for Todo Services
# =====================================

def test_create_and_get_todo(db):
    """Integration test: create a todo and fetch it from DB."""
    # Step 1: Create a new todo using the service layer
    data = TodoCreate(title="Integration Todo")
    todo = create_todo(db, data)

    # Step 2: Validate that the todo was created with an ID and correct title
    assert todo.id is not None
    assert todo.title == "Integration Todo"

    # Step 3: Fetch the same todo using get_todo service
    fetched = get_todo(db, todo.id)

    # Step 4: Assert that the fetched todo matches the created todo
    assert fetched.id == todo.id
    assert fetched.title == todo.title


def test_get_todo_not_found(db):
    """Test fetching a non-existent todo raises NotFoundException."""
    # Generate a UUID that does not exist in the DB
    non_existent_id = uuid.uuid4()

    # Expect NotFoundException to be raised when trying to fetch
    with pytest.raises(NotFoundException):
        get_todo(db, non_existent_id)


def test_update_todo_service(db):
    """Test updating a todo's title via service."""
    # Step 1: Create a todo to update
    todo = create_todo(db, TodoCreate(title="Old Title"))

    # Step 2: Prepare update data
    update_data = TodoUpdate(title="Updated Title")

    # Step 3: Call service to update the todo
    updated = update_todo(db, todo.id, update_data)

    # Step 4: Assert that the update was applied correctly
    assert updated.title == "Updated Title"


def test_soft_delete_todo_service(db):
    """Test soft delete marks the todo as deleted (is_deleted=True)."""
    # Step 1: Create a todo to delete
    todo = create_todo(db, TodoCreate(title="Delete Me"))

    # Step 2: Soft delete the todo using service
    soft_delete_todo(db, todo.id)

    # Step 3: Fetch the todo directly from DB
    fetched = db.query(todo.__class__).filter_by(id=todo.id).first()

    # Step 4: Assert that the todo is marked as deleted
    assert fetched.is_deleted is True


def test_list_todos_with_filters(db):
    """Test listing todos filtered by status."""
    # Step 1: Create multiple todos with different statuses
    create_todo(db, TodoCreate(title="Todo1"))  
    create_todo(db, TodoCreate(title="Todo2", status=TodoStatus.completed))

    # Step 2: List todos with status='pending' using service
    items, total = list_todos(db, status="pending")

    # Step 3: Assert that all fetched todos have status pending
    assert all(todo.status.value == "pending" for todo in items)

    # Step 4: Optionally, assert that total count matches expected
    assert total == len(items)