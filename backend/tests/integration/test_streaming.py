import pytest
import json
import asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.db.base import get_db
from app.db.models import AgentRun, AgentOutputChunk, Project, Task


class TestStreaming:
    """Integration tests for SSE streaming."""

    @pytest.fixture
    def sample_project(self, db_session):
        proj = Project(id="test", name="Test Project")
        db_session.add(proj)
        db_session.commit()
        return proj

    @pytest.fixture
    def sample_task(self, db_session, sample_project):
        task = Task(id="T-STREAM", project="test", title="Stream task", status="done")
        db_session.add(task)
        db_session.commit()
        return task

    @pytest.fixture
    def completed_run(self, db_session, sample_task):
        """Run with buffered output."""
        run = AgentRun(
            id="run-stream-test",
            task_id="T-STREAM",
            agent_id="@test",
            cli="agy",
            command="test",
            status="success",
            exit_code=0,
            output_lines=3
        )
        db_session.add(run)

        chunk = AgentOutputChunk(
            run_id="run-stream-test",
            chunk_index=0,
            content="line1\nline2\nline3"
        )
        db_session.add(chunk)
        db_session.commit()
        return run

    @pytest.mark.asyncio
    async def test_stream_returns_history_for_completed(self, completed_run, db_session):
        """Completed runs stream history then done."""
        app.dependency_overrides[get_db] = lambda: db_session

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            async with client.stream("GET", "/api/runs/run-stream-test/stream") as response:
                events = []
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        events.append(json.loads(line[5:].strip()))

                # Should have history lines
                history = [e for e in events if e.get("type") == "history"]
                assert len(history) == 3

                # Should have status and done
                assert any(e.get("type") == "status" for e in events)
                assert any(e.get("type") == "done" for e in events)

    @pytest.mark.asyncio
    @patch('app.api.stream.create_redis_client')
    async def test_stream_receives_live_updates(self, mock_redis_factory, db_session, sample_task):
        """Live updates are streamed via SSE."""
        mock_redis = AsyncMock()
        mock_pubsub = AsyncMock()
        mock_redis.pubsub.return_value = mock_pubsub
        mock_redis_factory.return_value = mock_redis

        messages = [
            {"type": "message", "data": json.dumps({"type": "stdout", "content": "live1"}).encode()},
            {"type": "message", "data": json.dumps({"type": "stdout", "content": "live2"}).encode()},
            {"type": "message", "data": json.dumps({"type": "status", "status": "success"}).encode()},
        ]
        mock_pubsub.get_message = AsyncMock(side_effect=messages + [asyncio.TimeoutError()])

        run = AgentRun(
            id="run-live-test",
            task_id="T-STREAM",
            agent_id="@test",
            cli="agy",
            command="test",
            status="running"
        )
        db_session.add(run)
        db_session.commit()

        app.dependency_overrides[get_db] = lambda: db_session

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            async with client.stream("GET", "/api/runs/run-live-test/stream") as response:
                events = []
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        events.append(json.loads(line[5:].strip()))
                        if len(events) >= 3:
                            break

                stdout_events = [e for e in events if e.get("type") == "stdout"]
                status_events = [e for e in events if e.get("type") == "status"]

                assert len(stdout_events) >= 2
                assert stdout_events[0]["content"] == "live1"
                assert stdout_events[1]["content"] == "live2"
                assert len(status_events) >= 1
                assert status_events[0]["status"] == "success"

    def test_get_full_output(self, completed_run, db_session):
        """GET /runs/{run_id}/output returns full history."""
        app.dependency_overrides[get_db] = lambda: db_session
        with TestClient(app) as client:
            response = client.get("/api/runs/run-stream-test/output")

            assert response.status_code == 200
            data = response.json()

            assert data["status"] == "success"
            assert "line1" in data["output"]
            assert "line3" in data["output"]
            assert data["line_count"] == 3
