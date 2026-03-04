import pytest
from datetime import datetime, timedelta, timezone
from app.api.v1.todos.models import Todo
from app.api.v1.todos.enums import TodoStatus, TodoPriority

# --------------------------
# Helper function
# --------------------------
def utcnow_naive():
    return datetime.now(timezone.utc).replace(tzinfo=None)

# =====================================
# Default / Property Tests
# =====================================
def test_todo_defaults(db):
    """Test default values are correctly set on Todo creation."""
    todo = Todo(title="Test Todo")
    db.add(todo)
    db.commit()
    db.refresh(todo)

    assert todo.status == TodoStatus.pending
    assert todo.priority == TodoPriority.medium
    assert todo.is_deleted is False
    assert todo.created_at is not None
    assert todo.updated_at is not None

def test_todo_is_completed_property(db):
    """Test the `is_completed` property returns correct boolean based on status."""
    todo = Todo(title="Complete me", status=TodoStatus.completed)
    db.add(todo)
    db.commit()
    db.refresh(todo)

    assert todo.is_completed is True
    
    todo.status = TodoStatus.pending
    db.commit()
    db.refresh(todo)
    assert todo.is_completed is False

# =====================================
# Validation / Enum Tests
# =====================================
def test_invalid_status_raises_error():
    """Check that invalid status values are rejected."""
    with pytest.raises(ValueError):
        Todo(title="Invalid", status="invalid_status")
        
def test_invalid_priority_raises_error():
    """Check that invalid priority values are rejected."""
    with pytest.raises(ValueError):
        Todo(title="Invalid", priority="invalid_priority")

def test_valid_status_accepts_enum():
    """Ensure valid TodoStatus enums are accepted."""
    todo = Todo(title="Valid", status=TodoStatus.in_progress)
    assert todo.status == TodoStatus.in_progress

def test_valid_priority_accepts_enum():
    """Ensure valid TodoPriority enums are accepted."""
    todo = Todo(title="Valid", priority=TodoPriority.high)
    assert todo.priority == TodoPriority.high

# =====================================
# CRUD Tests
# =====================================
def test_create_todo(db):
    """Test creating a Todo record."""
    todo = Todo(title="Create Test")
    db.add(todo)
    db.commit()
    db.refresh(todo)
    assert todo.id is not None
    
def test_update_title(db):
    """Test updating the title field."""
    todo = Todo(title="Old Title")
    db.add(todo)
    db.commit()
    todo.title = "New Title"
    db.commit()
    db.refresh(todo)
    assert todo.title == "New Title"

def test_update_description(db):
    """Test updating the description field."""
    todo = Todo(title="Task")
    db.add(todo)
    db.commit()
    todo.description = "Updated description"
    db.commit()
    db.refresh(todo)
    assert todo.description == "Updated description"
    
def test_update_status(db):
    """Test updating the status field."""
    todo = Todo(title="Task", status=TodoStatus.pending)
    db.add(todo)
    db.commit()
    todo.status = TodoStatus.completed
    db.commit()
    db.refresh(todo)
    assert todo.status == TodoStatus.completed

def test_soft_delete_todo(db):
    """Test soft-deleting a Todo record by setting is_deleted=True."""
    todo = Todo(title="Delete me")
    db.add(todo)
    db.commit()
    todo.is_deleted = True
    db.commit()
    db.refresh(todo)
    assert todo.is_deleted is True

# =====================================
# Index & Query Tests
# =====================================
def test_query_by_status_and_is_deleted(db):
    """Query using status and is_deleted filters."""
    todo = Todo(title="Query Test", status=TodoStatus.pending)
    db.add(todo)
    db.commit()
    results = db.query(Todo).filter_by(status=TodoStatus.pending, is_deleted=False).all()
    assert todo in results

def test_order_by_created_at(db):
    """Ensure todos are ordered correctly by created_at."""
    todo1 = Todo(title="First")
    todo2 = Todo(title="Second")
    db.add_all([todo1, todo2])
    db.commit()
    results = db.query(Todo).order_by(Todo.created_at.asc()).all()
    assert results[0].title == "First"
    assert results[1].title == "Second"

# =====================================
# Timestamp / Audit Tests
# =====================================
def test_updated_at_changes_on_update(db):
    """Check that updated_at changes after an update."""
    todo = Todo(title="Audit Test")
    db.add(todo)
    db.commit()
    old_updated_at = todo.updated_at
    todo.title = "Changed"
    db.commit()
    db.refresh(todo)
    assert todo.updated_at > old_updated_at

def test_created_at_does_not_change_on_update(db):
    """Ensure created_at remains the same after an update."""
    todo = Todo(title="Audit Test")
    db.add(todo)
    db.commit()
    old_created_at = todo.created_at
    todo.title = "Changed"
    db.commit()
    db.refresh(todo)
    assert todo.created_at == old_created_at

# =====================================
# Scheduling / Date Tests
# =====================================
def test_set_due_date(db):
    """Test setting due_date correctly."""
    due = utcnow_naive() + timedelta(days=3)
    todo = Todo(title="Due Test", due_date=due)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    assert todo.due_date == due

def test_set_reminder_at(db):
    """Test setting reminder_at correctly."""
    reminder = utcnow_naive() + timedelta(hours=2)
    todo = Todo(title="Reminder Test", reminder_at=reminder)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    assert todo.reminder_at == reminder
    