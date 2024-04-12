import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config.settings import settings
from app.db.database import Base
from app.db.models import Todos
from app.main import app

engine = create_engine(
    url=settings.TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {"username": "johndoe", "user_id": 1, "user_role": "admin"}


client = TestClient(app)


@pytest.fixture()
def test_todo():
    todo = Todos(
        title="Learn to Code!",
        description="Need to practice everyday!",
        priority=5,
        complete=False,
        owner_id=1,
    )
    print(todo)
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()
