import pytest
from tests.factories.todo_factory import TodoFactory

@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)

@pytest.fixture
def todo(db):
    return TodoFactory(sqlalchemy_session=db)

@pytest.fixture
def completed_todo(db):
    return TodoFactory(
        sqlalchemy_session=db,
        status="completed"
    )
