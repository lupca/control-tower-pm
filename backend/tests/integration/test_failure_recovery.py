import pytest
from unittest.mock import patch, Mock, MagicMock
from app.workers.agent_runner import run_agent
from app.db.models import AgentRun, Project, Task
from app.services.process_manager import ProcessManager, ProcessResult, ProcessStatus


class TestFailureRecovery:
    """Tests for failure handling and recovery."""

    def test_failed_agent_retries(self, db_session):
        """Failed agent is retried up to max_attempts."""
        proj = Project(id="test", name="Test Project")
        db_session.add(proj)
        task = Task(id="T-RETRY", project="test", title="Retry Task")
        db_session.add(task)

        run = AgentRun(
            id="retry-test",
            task_id="T-RETRY",
            agent_id="@test",
            cli="agy",
            command="test",
            status="queued",
            attempt=1,
            max_attempts=3
        )
        db_session.add(run)
        db_session.commit()

        attempt_count = [0]

        def mock_run(*args, **kwargs):
            attempt_count[0] += 1
            if attempt_count[0] < 3:
                yield ProcessResult(ProcessStatus.FAILED, 1, "Simulated failure")
            else:
                yield "Success output"
                yield ProcessResult(ProcessStatus.COMPLETED, 0, None)

        with patch('app.workers.agent_runner.redis_client'):
            with patch.object(ProcessManager, 'run_with_streaming', mock_run):
                # First attempt raises exception for Dramatiq retry
                with pytest.raises(Exception):
                    run_agent("retry-test", "T-RETRY", "test", "/tmp")

                # Second attempt raises exception for Dramatiq retry
                with pytest.raises(Exception):
                    run_agent("retry-test", "T-RETRY", "test", "/tmp")

                # Third attempt succeeds
                run_agent("retry-test", "T-RETRY", "test", "/tmp")

        db_session.refresh(run)
        assert run.status == "success"
        assert run.attempt == 3

    def test_timeout_does_not_retry(self, db_session):
        """Timeout is terminal, no retry."""
        proj = Project(id="test", name="Test Project")
        db_session.add(proj)
        task = Task(id="T-TIMEOUT", project="test", title="Timeout Task")
        db_session.add(task)

        run = AgentRun(
            id="timeout-test",
            task_id="T-TIMEOUT",
            agent_id="@test",
            cli="agy",
            command="sleep 999",
            status="queued"
        )
        db_session.add(run)
        db_session.commit()

        with patch('app.workers.agent_runner.redis_client'):
            with patch.object(
                ProcessManager,
                'run_with_streaming',
                return_value=iter([ProcessResult(ProcessStatus.TIMEOUT, -1, "Timeout after 14400s")])
            ):
                run_agent("timeout-test", "T-TIMEOUT", "sleep 999", "/tmp")

        db_session.refresh(run)
        assert run.status == "timeout"
        assert run.attempt == 1

    def test_worker_crash_recovers(self, db_session):
        """Queued task recovers after worker restart."""
        proj = Project(id="test", name="Test Project")
        db_session.add(proj)
        task = Task(id="T-CRASH", project="test", title="Crash Task")
        db_session.add(task)

        run = AgentRun(
            id="crash-test",
            task_id="T-CRASH",
            agent_id="@test",
            cli="agy",
            command="echo recovered",
            status="queued"
        )
        db_session.add(run)
        db_session.commit()

        with patch('app.workers.agent_runner.redis_client'):
            run_agent("crash-test", "T-CRASH", "echo recovered", "/tmp")

        db_session.refresh(run)
        assert run.status == "success"

    def test_db_error_marks_failed(self, db_session):
        """Database error during execution raises exception for retry."""
        proj = Project(id="test", name="Test Project")
        db_session.add(proj)
        task = Task(id="T-DB", project="test", title="DB Task")
        db_session.add(task)

        run = AgentRun(
            id="db-error-test",
            task_id="T-DB",
            agent_id="@test",
            cli="agy",
            command="echo test",
            status="queued"
        )
        db_session.add(run)
        db_session.commit()

        with patch('app.workers.agent_runner.redis_client'):
            with patch('app.workers.agent_runner.SessionLocal') as mock_session:
                mock_db = MagicMock()
                mock_db.query.return_value.filter.return_value.first.return_value = run
                mock_db.commit.side_effect = Exception("DB connection lost")
                mock_session.return_value = mock_db

                with pytest.raises(Exception):
                    run_agent("db-error-test", "T-DB", "echo test", "/tmp")
