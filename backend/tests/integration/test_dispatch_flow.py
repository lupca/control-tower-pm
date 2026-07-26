import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app
from app.db.base import get_db
from app.db.models import Task, Agent, AgentRun, Project


class TestDispatchFlow:
    """Integration tests for dispatch API."""

    @pytest.fixture
    def client(self, db_session):
        app.dependency_overrides[get_db] = lambda: db_session
        with TestClient(app) as c:
            yield c

    @pytest.fixture
    def sample_project(self, db_session):
        proj = Project(id="test", name="Test Project")
        db_session.add(proj)
        db_session.commit()
        return proj

    @pytest.fixture
    def sample_task(self, db_session, sample_project):
        task = Task(id="T-INT-001", project="test", title="Test task", status="todo")
        db_session.add(task)
        db_session.commit()
        return task

    @pytest.fixture
    def sample_agent(self, db_session):
        agent = Agent(id="@test-agent", name="Test Agent", role="executor", cli="agy")
        db_session.add(agent)
        db_session.commit()
        return agent

    @patch('app.api.dispatch.run_agent')
    def test_dispatch_creates_run_and_queues(
        self, mock_run_agent, client, sample_task, sample_agent, db_session
    ):
        """POST /dispatch creates AgentRun and queues to Dramatiq."""
        response = client.post("/api/dispatch", json={
            "task_id": "T-INT-001",
            "agent_id": "@test-agent"
        })

        assert response.status_code == 200
        data = response.json()

        # Verify response
        assert data["task_id"] == "T-INT-001"
        assert data["agent_id"] == "@test-agent"
        assert data["status"] == "queued"
        assert "run_id" in data

        # Verify DB record
        run = db_session.query(AgentRun).filter(AgentRun.id == data["run_id"]).first()
        assert run is not None
        assert run.status == "queued"

        # Verify Dramatiq called
        mock_run_agent.send.assert_called_once()

    def test_dispatch_rejects_missing_task(self, client, sample_agent):
        """Dispatch fails for non-existent task."""
        response = client.post("/api/dispatch", json={
            "task_id": "NONEXISTENT",
            "agent_id": "@test-agent"
        })

        assert response.status_code == 404

    def test_dispatch_rejects_duplicate_active_run(
        self, client, sample_task, sample_agent, db_session
    ):
        """Cannot dispatch if task already has active run."""
        existing = AgentRun(
            task_id="T-INT-001",
            agent_id="@test-agent",
            cli="agy",
            command="test",
            status="running"
        )
        db_session.add(existing)
        db_session.commit()

        response = client.post("/api/dispatch", json={
            "task_id": "T-INT-001",
            "agent_id": "@test-agent"
        })

        assert response.status_code == 409

    def test_get_run_status(self, client, sample_task, db_session):
        """GET /dispatch/{run_id} returns run status."""
        run = AgentRun(
            id="run-test-123",
            task_id="T-INT-001",
            agent_id="@test-agent",
            cli="agy",
            command="test",
            status="running",
            pid=12345
        )
        db_session.add(run)
        db_session.commit()

        response = client.get("/api/dispatch/run-test-123")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert data["pid"] == 12345

    def test_cancel_running_task(self, client, sample_task, db_session):
        """POST /dispatch/{run_id}/cancel cancels running task."""
        run = AgentRun(
            id="run-cancel-test",
            task_id="T-INT-001",
            agent_id="@test-agent",
            cli="agy",
            command="test",
            status="running"
        )
        db_session.add(run)
        db_session.commit()

        response = client.post("/api/dispatch/run-cancel-test/cancel")

        assert response.status_code == 200

        # Verify status updated
        db_session.refresh(run)
        assert run.status == "cancelled"
