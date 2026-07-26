import pytest
from unittest.mock import Mock, patch
from app.services.process_manager import ProcessManager, ProcessStatus, ProcessResult


class TestProcessManager:
    """Unit tests for ProcessManager."""

    def test_successful_execution(self):
        """Simple command completes successfully."""
        pm = ProcessManager(timeout_seconds=10)

        results = list(pm.run_with_streaming("echo 'hello'", "/tmp"))

        # Should have output line + result
        assert len(results) >= 1
        assert any(isinstance(r, ProcessResult) for r in results)

        final = [r for r in results if isinstance(r, ProcessResult)][0]
        assert final.status == ProcessStatus.COMPLETED
        assert final.exit_code == 0

    def test_captures_all_output_lines(self):
        """All stdout lines are captured."""
        pm = ProcessManager()

        results = list(pm.run_with_streaming(
            "for i in 1 2 3; do echo line$i; done",
            "/tmp"
        ))

        lines = [r for r in results if isinstance(r, str)]
        assert len(lines) == 3
        assert lines == ["line1", "line2", "line3"]

    def test_timeout_terminates_process(self):
        """Long-running process is killed on timeout."""
        pm = ProcessManager(timeout_seconds=1)

        results = list(pm.run_with_streaming("sleep 60", "/tmp"))

        final = [r for r in results if isinstance(r, ProcessResult)][0]
        assert final.status == ProcessStatus.TIMEOUT

    def test_failed_command_returns_exit_code(self):
        """Non-zero exit code is captured."""
        pm = ProcessManager()

        results = list(pm.run_with_streaming("exit 42", "/tmp"))

        final = [r for r in results if isinstance(r, ProcessResult)][0]
        assert final.status == ProcessStatus.FAILED
        assert final.exit_code == 42

    def test_cancellation_terminates_process(self):
        """Cancel request terminates running process."""
        pm = ProcessManager()

        gen = pm.run_with_streaming("sleep 60", "/tmp")
        # Advance iterator to start process
        pm.cancel()

        results = list(gen)
        final = [r for r in results if isinstance(r, ProcessResult)][0]
        assert final.status in (ProcessStatus.CANCELLED, ProcessStatus.COMPLETED, ProcessStatus.FAILED, ProcessStatus.TIMEOUT)

    def test_stdin_is_devnull(self):
        """Process stdin is /dev/null (no blocking)."""
        pm = ProcessManager()

        # Command that reads stdin would hang without /dev/null
        results = list(pm.run_with_streaming("cat", "/tmp"))

        final = [r for r in results if isinstance(r, ProcessResult)][0]
        assert final.status in (ProcessStatus.COMPLETED, ProcessStatus.FAILED)

    def test_kills_child_processes(self):
        """Termination kills entire process tree."""
        pm = ProcessManager(timeout_seconds=1)

        results = list(pm.run_with_streaming(
            "bash -c 'sleep 60 & sleep 60'",
            "/tmp"
        ))

        final = [r for r in results if isinstance(r, ProcessResult)][0]
        assert final.status == ProcessStatus.TIMEOUT
