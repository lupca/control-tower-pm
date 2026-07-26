import os
import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import CurrentMessage
import redis
import json
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.db.base import SessionLocal
from app.db.models import AgentRun, AgentOutputChunk, Task
from app.services.process_manager import ProcessManager, ProcessResult, ProcessStatus

logger = logging.getLogger(__name__)

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Configure broker with middleware
redis_broker = RedisBroker(url=redis_url)
redis_broker.add_middleware(CurrentMessage())
dramatiq.set_broker(redis_broker)

# Redis client for pub/sub
redis_client = redis.Redis.from_url(redis_url)


def get_channel(run_id: str) -> str:
    return f"agent_run:{run_id}:output"


def publish_line(run_id: str, line: str, line_type: str = "stdout"):
    """Publish a line to Redis for SSE streaming."""
    payload = json.dumps({
        "type": line_type,
        "content": line,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    try:
        redis_client.publish(get_channel(run_id), payload)
    except Exception as e:
        logger.warning(f"Failed to publish to Redis: {e}")


def publish_status(run_id: str, status: str, **kwargs):
    """Publish status update."""
    payload = json.dumps({
        "type": "status",
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **kwargs
    })
    try:
        redis_client.publish(get_channel(run_id), payload)
    except Exception as e:
        logger.warning(f"Failed to publish status to Redis: {e}")


@dramatiq.actor(
    max_retries=3,
    min_backoff=30000,      # 30s initial backoff
    max_backoff=300000,     # 5min max backoff
    time_limit=14400000,    # 4 hour time limit
    notify_shutdown=True,   # Clean shutdown
)
def run_agent(
    run_id: str,
    task_id: str,
    command: str,
    repo_root: str,
    timeout_seconds: int = 14400
):
    """
    Execute CLI agent with full lifecycle management.

    Responsibilities:
    - Stream output to Redis Pub/Sub
    - Persist output to database
    - Update run status
    - Handle retries on failure
    - Clean shutdown on cancellation
    """
    db: Session = SessionLocal()
    pm = ProcessManager(timeout_seconds=timeout_seconds)
    result = None

    try:
        # 1. Mark as running
        run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
        if not run:
            logger.error(f"AgentRun {run_id} not found")
            return

        run.status = "running"
        run.started_at = datetime.now(timezone.utc)
        run.pid = None  # Will set after process starts
        db.commit()

        publish_status(run_id, "running")
        logger.info(f"Starting agent run {run_id} for task {task_id}")

        # 2. Execute with streaming
        line_count = 0
        total_bytes = 0
        chunk_buffer = []
        CHUNK_SIZE = 100  # Lines per chunk

        for output in pm.run_with_streaming(command, repo_root):
            # Update PID on first iteration
            if run.pid is None and pm.pid:
                run.pid = pm.pid
                db.commit()

            if isinstance(output, ProcessResult):
                # Process completed
                result = output
                break
            else:
                # Output line
                line = output
                line_count += 1
                total_bytes += len(line)

                # Stream to Redis
                publish_line(run_id, line)

                # Buffer for DB persistence
                chunk_buffer.append(line)
                if len(chunk_buffer) >= CHUNK_SIZE:
                    _persist_chunk(db, run_id, chunk_buffer)
                    chunk_buffer = []

        if result is None:
            result = ProcessResult(ProcessStatus.COMPLETED, 0, None)

        # 3. Persist remaining buffer
        if chunk_buffer:
            _persist_chunk(db, run_id, chunk_buffer)

        # 4. Update final status
        status_val = result.status.value
        if status_val == "completed":
            status_val = "success"

        run.status = status_val
        run.exit_code = result.exit_code
        run.completed_at = datetime.now(timezone.utc)
        run.output_lines = line_count
        run.output_bytes = total_bytes

        if result.error:
            run.error_message = result.error

        # 5. Parse result (git commit, etc.)
        if result.status == ProcessStatus.COMPLETED:
            run.result_ref = _parse_result_ref(repo_root)
            _update_task_status(db, task_id, "done", run.result_ref)
        else:
            _update_task_status(db, task_id, "failed", error=result.error)

        db.commit()

        # 6. Publish completion
        publish_status(
            run_id,
            status_val,
            exit_code=result.exit_code,
            result_ref=run.result_ref,
            error=result.error
        )

        logger.info(f"Agent run {run_id} completed: {status_val}")

        # 7. Retry on failure (Dramatiq handles this via exception)
        if result and result.status == ProcessStatus.FAILED:
            message = CurrentMessage.get_current_message()
            attempts = run.attempt or 1
            run.attempt = attempts + 1
            db.commit()
            if message and message.options.get("retries", 0) < run.max_attempts:
                raise Exception(f"Agent failed: {result.error}")
            elif not message and attempts < run.max_attempts:
                raise Exception(f"Agent failed: {result.error}")

    except Exception as e:
        logger.exception(f"Agent run {run_id} error: {e}")

        run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
        if run and run.status not in ["success", "completed", "timeout", "cancelled"]:
            run.status = "failed"
            run.error_message = str(e)
            run.completed_at = datetime.now(timezone.utc)
            db.commit()
            publish_status(run_id, "failed", error=str(e))

        raise  # Let Dramatiq handle retry

    finally:
        db.close()


def _persist_chunk(db: Session, run_id: str, lines: list[str]):
    """Persist a chunk of output lines."""
    count = db.query(AgentOutputChunk).filter(
        AgentOutputChunk.run_id == run_id
    ).count()
    chunk = AgentOutputChunk(
        run_id=run_id,
        chunk_index=count,
        content="\n".join(lines)
    )
    db.add(chunk)
    db.commit()


def _parse_result_ref(repo_root: str) -> str | None:
    """Parse git commit/branch from repo."""
    import subprocess
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=10
        )
        return res.stdout.strip()[:12] if res.returncode == 0 else None
    except Exception:
        return None


def _update_task_status(db: Session, task_id: str, status: str, result_ref: str = None, error: str = None):
    """Update task status in database."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.status = status
        if result_ref:
            task.result_ref = result_ref
        if error:
            task.findings = (task.findings or []) + [{"error": error}]
        task.updated_at = datetime.now(timezone.utc)
        if status == "done":
            task.completed_at = datetime.now(timezone.utc)
        db.commit()
