import pytest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch, MagicMock
from app.workers.agent_runner import run_agent
from app.db.models import AgentRun, Project, Task
from app.services.process_manager import ProcessResult, ProcessStatus


class TestConcurrentAgents:
    """Stress tests for concurrent agent execution."""

    @pytest.mark.slow
    def test_10_concurrent_short_agents(self, db_session):
        """10 agents running simultaneously complete without interference."""
        proj = Project(id="test", name="Test Project")
        db_session.add(proj)
        db_session.commit()

        runs = []
        for i in range(10):
            run_id = f"stress-{i}"
            task_id = f"T-STRESS-{i}"
            task = Task(id=task_id, project="test", title=f"Task {i}")
            db_session.add(task)

            run = AgentRun(
                id=run_id,
                task_id=task_id,
                agent_id="@test",
                cli="agy",
                command=f"echo 'Agent {i} output'",
                status="queued"
            )
            db_session.add(run)
            runs.append((run_id, task_id, f"echo 'Agent {i} output'"))

        db_session.commit()

        with patch('app.workers.agent_runner.redis_client'):
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [
                    executor.submit(run_agent, rid, tid, cmd, "/tmp")
                    for rid, tid, cmd in runs
                ]

                for f in futures:
                    f.result()

        for run_id, _, _ in runs:
            run = db_session.query(AgentRun).filter(AgentRun.id == run_id).first()
            assert run is not None
            assert run.status == "success"

    @pytest.mark.slow
    def test_agent_isolation(self, db_session):
        """Concurrent agents don't share state or interfere."""
        proj = Project(id="test", name="Test Project")
        db_session.add(proj)

        t1 = Task(id="T-ISO-1", project="test", title="Task 1")
        t2 = Task(id="T-ISO-2", project="test", title="Task 2")
        r1 = AgentRun(id="iso-1", task_id="T-ISO-1", agent_id="@a1", cli="agy", command="echo Agent 1", status="queued")
        r2 = AgentRun(id="iso-2", task_id="T-ISO-2", agent_id="@a2", cli="agy", command="echo Agent 2", status="queued")
        db_session.add_all([t1, t2, r1, r2])
        db_session.commit()

        published = {}

        def mock_publish(channel, payload):
            if channel not in published:
                published[channel] = []
            published[channel].append(payload)

        with patch('app.workers.agent_runner.redis_client') as mock_redis:
            mock_redis.publish.side_effect = mock_publish
            with ThreadPoolExecutor(max_workers=2) as executor:
                f1 = executor.submit(run_agent, "iso-1", "T-ISO-1", "echo Agent 1 output", "/tmp")
                f2 = executor.submit(run_agent, "iso-2", "T-ISO-2", "echo Agent 2 output", "/tmp")
                f1.result()
                f2.result()

        ch1_data = str(published.get("agent_run:iso-1:output", []))
        ch2_data = str(published.get("agent_run:iso-2:output", []))

        assert "Agent 1 output" in ch1_data
        assert "Agent 2 output" in ch2_data
        assert "Agent 2 output" not in ch1_data
