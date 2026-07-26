import os
import dramatiq
import subprocess
import redis
import json
import logging
from datetime import datetime, timezone
from dramatiq.brokers.redis import RedisBroker

from app.db.base import SessionLocal
from app.db.models import AgentRun, Task
from app.services.process_manager import ProcessManager, ProcessResult, ProcessStatus

logger = logging.getLogger(__name__)

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_broker = RedisBroker(url=redis_url)
dramatiq.set_broker(redis_broker)

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


@dramatiq.actor(max_retries=3, min_backoff=30000, time_limit=14400000)
def run_agent(run_id: str, task_id: str, command: str, repo_root: str, timeout_seconds: int = 14400, **kwargs):
    channel = f'run:{run_id}'
    try:
        redis_client.publish(channel, 'started')
    except Exception as e:
        logger.warning(f"Failed to publish started to Redis: {e}")

    publish_status(run_id, "running")

    db = None
    run = None
    try:
        db = SessionLocal()
        run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
        if run:
            run.status = "running"
            run.started_at = datetime.now(timezone.utc)
            db.commit()
    except Exception as e:
        logger.warning(f"DB update failed for run start: {e}")

    exit_code = 1
    pm = ProcessManager(timeout_seconds=timeout_seconds)

    try:
        for output in pm.run_with_streaming(command, repo_root):
            if isinstance(output, ProcessResult):
                exit_code = output.exit_code if output.exit_code is not None else 0
                break
            else:
                line_str = str(output).strip()
                try:
                    redis_client.publish(channel, line_str)
                except Exception:
                    pass
                publish_line(run_id, line_str)
    except Exception as e:
        logger.exception(f"Error running process in run_agent: {e}")
        try:
            process = subprocess.Popen(
                command, shell=True, cwd=repo_root,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL, text=True, bufsize=1
            )
            if process.stdout:
                for line in process.stdout:
                    line_str = line.strip()
                    try:
                        redis_client.publish(channel, line_str)
                    except Exception:
                        pass
                    publish_line(run_id, line_str)
            exit_code = process.wait()
        except Exception:
            exit_code = 1

    try:
        redis_client.publish(channel, f'__DONE__{exit_code}')
    except Exception:
        pass

    status_str = "success" if exit_code == 0 else "failed"
    publish_status(run_id, status_str, exit_code=exit_code)

    if db:
        try:
            if not run:
                run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
            if run:
                run.status = status_str
                run.completed_at = datetime.now(timezone.utc)
                run.exit_code = exit_code
                db.commit()
            task = db.query(Task).filter(Task.id == task_id).first()
            if task and task is not run:
                task.status = "done" if exit_code == 0 else "failed"
                db.commit()
        except Exception as e:
            logger.warning(f"DB update failed for run complete: {e}")
        finally:
            db.close()

    return exit_code
