import pytest
from uuid import UUID
from app.api.v1.todos.schemas import TodoCreate, TodoUpdate
from app.api.v1.todos.enums import TodoStatus, TodoPriority

# =====================================
# Test: Create Todo
# =====================================
def test_create_todo(client, test_payload):
    # Send POST request to create a new todo
    response = client.post('/api/v1/todos/', json=test_payload)
    
    # Assert that HTTP 201 Created is returned
    assert response.status_code == 201
    
    data = response.json()["data"]
    
    # Check that returned data matches input
    assert data["title"] == test_payload["title"]
    assert data["status"] == test_payload["status"]
    
    # Ensure the response includes an ID for the new todo
    assert "id" in data

# =====================================
# Test: Get Todo by ID
# =====================================
def test_get_todo_by_id(client, test_payload):
    # First, create a todo to ensure one exists
    create_resp = client.post("/api/v1/todos/", json=test_payload)
    todo_id = create_resp.json()["data"]["id"]

    # Fetch the todo by ID
    get_resp = client.get(f"/api/v1/todos/{todo_id}")
    assert get_resp.status_code == 200
    
    data = get_resp.json()["data"]
    
    # Validate that the returned todo matches the created one
    assert data["id"] == todo_id
    assert data["title"] == test_payload["title"]

# =====================================
# Test: Get Non-Existent Todo
# =====================================
def test_get_todo_not_found(client):
    # Use a UUID that does not exist in the database
    response = client.get("/api/v1/todos/00000000-0000-0000-0000-000000000000")
    
    # Expect HTTP 404 Not Found
    assert response.status_code == 404

# =====================================
# Test: Update Todo
# =====================================
def test_update_todo(client, test_payload):
    # Create a todo first
    create_resp = client.post("/api/v1/todos/", json=test_payload)
    todo_id = create_resp.json()["data"]["id"]
    
    # Prepare updated data
    update_data = {"title": "Updated Todo", "status": "in_progress"}
    
    # Send PUT request to update the todo
    response = client.put(f"/api/v1/todos/{todo_id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()["data"]
    
    # Verify the update was applied
    assert data["title"] == "Updated Todo"
    assert data["status"] == "in_progress"

# =====================================
# Test: Soft Delete Todo
# =====================================
def test_soft_delete_todo(client, test_payload):
    # Create a todo
    create_resp = client.post("/api/v1/todos/", json=test_payload)
    todo_id = create_resp.json()["data"]["id"]

    # Delete the todo (soft delete)
    response = client.delete(f"/api/v1/todos/{todo_id}")
    assert response.status_code == 200

    # Attempt to fetch the deleted todo
    get_resp = client.get(f"/api/v1/todos/{todo_id}")
    
    # Should return 404 as the todo is soft-deleted
    assert get_resp.status_code == 404

# =====================================
# Test: List Todos with Pagination
# =====================================
def test_list_todos(client, test_payload):
    # Create multiple todos for listing
    for i in range(5):
        client.post("/api/v1/todos/", json={**test_payload, "title": f"Todo {i}"})

    # Fetch todos with pagination (skip=0, limit=3)
    response = client.get("/api/v1/todos/?skip=0&limit=3")
    assert response.status_code == 200
    
    data = response.json()["data"]
    
    # Ensure only 3 todos are returned as per limit
    assert len(data) == 3
