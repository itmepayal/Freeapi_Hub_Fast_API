# =====================================
# Package Import
# =====================================
import uuid
import pytest

# =====================================
# App Imports
# =====================================
from app.api.v1.todos import (
    create_todo,
    get_todo,
    list_todos,
    update_todo,
    soft_delete_todo,
)
from app.api.v1.todos import TodoCreate, TodoUpdate, TodoStatus
from app.core.exceptions import NotFoundException

# =====================================
# Todo Services Unit Tests
# =====================================

def test_create_todo(db):
    """Test that a todo can be created successfully via service."""
    # Step 1: Prepare the todo data
    data = TodoCreate(title="Unit Test Todo")
    
    # Step 2: Call service to create todo
    todo = create_todo(db, data)
    
    # Step 3: Validate that todo was created correctly
    assert todo.id is not None                     
    assert todo.title == "Unit Test Todo"         
    assert todo.status == TodoStatus.pending       
    assert todo.is_deleted is False                


def test_get_todo_not_found_raises(db):
    """Test that fetching a non-existent todo raises NotFoundException."""
    # Generate a UUID that does not exist in DB
    non_existent_id = uuid.uuid4()
    
    # Expect NotFoundException when trying to fetch
    with pytest.raises(NotFoundException):
        get_todo(db, non_existent_id)


def test_update_todo(db):
    """Test that a todo's title can be updated via service."""
    # Step 1: Create a todo to update
    data = TodoCreate(title="Update Test")
    todo = create_todo(db, data)
    
    # Step 2: Prepare update data
    update_data = TodoUpdate(title="Updated Title")
    
    # Step 3: Call service to update todo
    updated_todo = update_todo(db, todo.id, update_data)
    
    # Step 4: Validate that the title was updated
    assert updated_todo.title == "Updated Title"


def test_soft_delete(db):
    """Test that soft-deleting a todo marks it as deleted."""
    # Step 1: Create a todo to delete
    data = TodoCreate(title="Delete Test")
    todo = create_todo(db, data)
    
    # Step 2: Call service to soft delete the todo
    soft_delete_todo(db, todo.id)
    
    # Step 3: Fetch the todo from DB to confirm deletion
    deleted_todo = db.query(todo.__class__).filter_by(id=todo.id).first()
    
    # Step 4: Assert that todo is marked as deleted
    assert deleted_todo.is_deleted is True


def test_list_todos_with_status(db):
    """Test listing todos filtered by status."""
    # Step 1: Create multiple todos
    create_todo(db, TodoCreate(title="Todo1"))  
    create_todo(db, TodoCreate(title="Todo2"))  
    
    # Step 2: List todos filtered by status='pending'
    items, total = list_todos(db, status="pending")
    
    # Step 3: Validate total number of todos returned
    assert total == 2
    
    # Step 4: Assert that all fetched todos have the requested status
    assert all(todo.status.value == "pending" for todo in items)