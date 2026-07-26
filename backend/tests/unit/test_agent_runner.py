import pytest
from unittest.mock import Mock, patch, MagicMock
from app.workers.agent_runner import run_agent, publish_line, publish_status
from app.services.process_manager import ProcessResult, ProcessStatus


class TestAgentRunner:
    """Unit tests for Dramatiq worker."""

    @patch('app.workers.agent_runner.redis_client')
    def test_publish_line_format(self, mock_redis):
        """Published line has correct JSON format."""
        publish_line("run-123", "test output")

        mock_redis.publish.assert_called_once()
        channel, payload = mock_redis.publish.call_args[0]

        assert channel == "agent_run:run-123:output"

        import json
        data = json.loads(payload)
        assert data["type"] == "stdout"
        assert data["content"] == "test output"
        assert "timestamp" in data

    @patch('app.workers.agent_runner.redis_client')
    def test_publish_status_includes_extras(self, mock_redis):
        """Status publish includes extra kwargs."""
        publish_status("run-123", "success", exit_code=0, result_ref="abc123")

        import json
        payload = mock_redis.publish.call_args[0][1]
        data = json.loads(payload)

        assert data["status"] == "success"
        assert data["exit_code"] == 0
        assert data["result_ref"] == "abc123"

    @patch('app.workers.agent_runner.ProcessManager')
    @patch('app.workers.agent_runner.SessionLocal')
    @patch('app.workers.agent_runner.redis_client')
    def test_run_agent_updates_status_to_running(
        self, mock_redis, mock_session, mock_pm
    ):
        """Agent run updates DB status to running and completed."""
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_run = Mock(id="run-123", status="queued", attempt=1)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_run

        mock_pm_instance = Mock()
        mock_pm.return_value = mock_pm_instance
        mock_pm_instance.run_with_streaming.return_value = iter([
            ProcessResult(ProcessStatus.COMPLETED, 0, None)
        ])
        mock_pm_instance.pid = 12345

        # Execute
        run_agent("run-123", "task-1", "echo test", "/tmp")

        # Verify status update
        assert mock_run.status == "success"
        assert mock_run.started_at is not None
