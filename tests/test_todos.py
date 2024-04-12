from fastapi import status

from app.db.database import get_db
from app.db.models import Todos
from app.routers.auth import get_current_user
from tests.utils import (
    TestingSessionLocal,
    app,
    client,
    override_get_current_user,
    override_get_db,
    test_todo,
)

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all_authenticated(test_todo):
    response = client.get("/todos")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "id": 1,
            "complete": False,
            "owner_id": 1,
            "title": "Learn to Code!",
            "description": "Need to practice everyday!",
            "priority": 5,
        }
    ]


def test_read_one_authenticated(test_todo):
    response = client.get("/todos/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": 1,
        "complete": False,
        "owner_id": 1,
        "title": "Learn to Code!",
        "description": "Need to practice everyday!",
        "priority": 5,
    }


def test_read_one_not_found(test_todo):
    response = client.get("/todos/2")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "To-do not found!"}


def test_create_todo(test_todo):
    request_data = {
        "title": "New Todo!",
        "description": "New todo description",
        "priority": 4,
        "complete": False,
    }

    response = client.post("/todos", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()

    assert model.title == request_data.get("title")
    assert model.description == request_data.get("description")
    assert model.priority == request_data.get("priority")
    assert model.complete == request_data.get("complete")


def test_update_todo(test_todo):
    request_data = {
        "title": "Change the title of the todo already saved",
        "description": "Need to learn everyday",
    }

    response = client.put("/todos/1", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()

    assert model.title == request_data.get("title")
    assert model.description == request_data.get("description")
    assert model.priority == test_todo.priority
    assert model.complete == test_todo.complete


def test_update_todo_not_found(test_todo):
    request_data = {
        "title": "Change the title of the todo already saved",
        "description": "Need to learn everyday",
    }

    response = client.put("/todos/2", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "To-do not found!"}


def test_delete_todo(test_todo):
    response = client.delete("/todos/1")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


def test_delete_todo_not_found(test_todo):
    response = client.delete("/todos/999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "To-do not found!"}
