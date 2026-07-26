import pytest
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as SQLAlchemySession
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.db.base import Base, get_db
import app.db.models  # noqa: F401
from app.main import app
from app.graph.builder import build_graph
from langgraph.checkpoint.memory import MemorySaver


class TestDatabaseWrapper:
    def __init__(self, session: SQLAlchemySession):
        self.session = session

    def query(self, *args, **kwargs):
        return self.session.query(*args, **kwargs)

    def add(self, item):
        self.session.add(item)
        self.session.commit()

    def update_task(self, task_id: str, **kwargs):
        from app.db.models import Task
        task = self.session.query(Task).filter(Task.id == task_id).first()
        if not task:
            task = Task(id=task_id, project="DEMO", title="Test Task", status="dispatched")
            self.session.add(task)
        for key, value in kwargs.items():
            setattr(task, key, value)
        self.session.commit()
        return task


@pytest.fixture
def db():
    """Fresh test database per test using StaticPool."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    wrapper = TestDatabaseWrapper(session)

    yield wrapper

    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def client(db):
    """FastAPI TestClient with overridden get_db using current test db."""
    def override_get_db():
        yield db.session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def graph(db):
    """LangGraph with mocked LLM calls."""
    with patch("os.getenv", return_value=None):
        yield build_graph(checkpointer=MemorySaver())


@pytest.fixture
def mock_llm():
    """Deterministic LLM responses fixture."""
    return {
        "spec": {"acceptance_criteria": ["AC1", "AC2"], "risk": "low"},
        "plan": {"plan": "1. Do this\n2. Do that"}
    }
