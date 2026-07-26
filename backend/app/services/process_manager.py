import subprocess
import signal
import psutil
import os
from typing import Optional, Generator, Union
from dataclasses import dataclass
from enum import Enum


class ProcessStatus(Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class ProcessResult:
    status: ProcessStatus
    exit_code: Optional[int]
    error: Optional[str]


class ProcessManager:
    """
    Manages subprocess lifecycle with proper cleanup.
    Handles: stdin isolation, signal forwarding, timeout, cleanup.
    """

    def __init__(self, timeout_seconds: int = 14400):
        self.timeout = timeout_seconds
        self.process: Optional[subprocess.Popen] = None
        self._cancelled = False

    def run_with_streaming(
        self,
        command: str,
        cwd: str,
        env: Optional[dict] = None
    ) -> Generator[Union[str, ProcessResult], None, None]:
        """
        Run command and yield output lines as they come.
        Yields ProcessResult when done.

        Usage:
            for line in pm.run_with_streaming(cmd, cwd):
                if isinstance(line, ProcessResult):
                    # Done
                else:
                    # Output line
        """
        process_env = os.environ.copy()
        if env:
            process_env.update(env)

        try:
            self.process = subprocess.Popen(
                command,
                shell=True,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,  # Critical: no stdin
                text=True,
                bufsize=1,  # Line buffered
                env=process_env,
                start_new_session=True,  # New process group for cleanup
            )

            # Stream output
            if self.process.stdout:
                for line in iter(self.process.stdout.readline, ''):
                    if self._cancelled:
                        self._terminate()
                        yield ProcessResult(ProcessStatus.CANCELLED, -1, "Cancelled by user")
                        return
                    yield line.rstrip('\r\n')

            # Wait for completion with timeout
            try:
                exit_code = self.process.wait(timeout=self.timeout)
            except subprocess.TimeoutExpired:
                self._terminate()
                yield ProcessResult(ProcessStatus.TIMEOUT, -1, f"Timeout after {self.timeout}s")
                return

            if self._cancelled:
                self._terminate()
                yield ProcessResult(ProcessStatus.CANCELLED, -1, "Cancelled by user")
                return

            if exit_code == 0:
                yield ProcessResult(ProcessStatus.COMPLETED, exit_code, None)
            else:
                yield ProcessResult(ProcessStatus.FAILED, exit_code, f"Exit code: {exit_code}")

        except Exception as e:
            self._terminate()
            yield ProcessResult(ProcessStatus.FAILED, -1, str(e))

    def cancel(self):
        """Request cancellation."""
        self._cancelled = True

    def _terminate(self):
        """Terminate process and all children."""
        if self.process and self.process.poll() is None:
            try:
                parent = psutil.Process(self.process.pid)
                children = parent.children(recursive=True)

                for child in children:
                    try:
                        child.terminate()
                    except psutil.NoSuchProcess:
                        pass
                try:
                    parent.terminate()
                except psutil.NoSuchProcess:
                    pass

                # Wait briefly, then force kill
                gone, alive = psutil.wait_procs(children + [parent], timeout=5)
                for p in alive:
                    try:
                        p.kill()
                    except psutil.NoSuchProcess:
                        pass

            except psutil.NoSuchProcess:
                pass
            except Exception:
                pass

    @property
    def pid(self) -> Optional[int]:
        return self.process.pid if self.process else None
