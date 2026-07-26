---
id: CTV2-031
title: "Agent Runner: Dramatiq + Redis + SSE Streaming"
status: done
priority: critical
risk: high
executor: "@gpt-5.6-sol"
reviewer: "@claude-opus"
note: "Reopened - previous executor only implemented 20%"
deadline: 2026-07-30
created: 2026-07-26
depends_on: [CTV2-030]
files:
  - backend/app/workers/__init__.py
  - backend/app/workers/agent_runner.py
  - backend/app/workers/output_streamer.py
  - backend/app/api/dispatch.py
  - backend/app/api/stream.py
  - backend/app/services/process_manager.py
  - backend/app/db/models.py (add AgentRun)
  - docker-compose.yml (add redis, worker)
  - backend/tests/unit/test_agent_runner.py
  - backend/tests/integration/test_dispatch_flow.py
  - backend/tests/integration/test_streaming.py
tests:
  - All unit tests pass
  - All integration tests pass
  - Stress test: 10 concurrent agents
  - Failure recovery test
  - Stream reconnection test
---

# CTV2-031: Agent Runner with Dramatiq + Redis + SSE

## 1. Overview

Hệ thống quản lý và giám sát CLI agents (agy, codex, claude) chạy background với:
- **Dramatiq**: Task queue với auto-retry, persistence
- **Redis**: Message broker + Pub/Sub cho realtime streaming
- **SSE**: Server-Sent Events cho frontend streaming
- **PostgreSQL**: Persistent state và output history

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CONTROL TOWER V2                               │
│                                                                             │
│  ┌─────────────┐                                                           │
│  │  Frontend   │◀─────────── SSE Stream ──────────────────────┐            │
│  │  (React)    │                                              │            │
│  └──────┬──────┘                                              │            │
│         │ POST /dispatch                                      │            │
│         ▼                                                     │            │
│  ┌─────────────┐    enqueue    ┌─────────────┐    poll    ┌──┴──────────┐ │
│  │   FastAPI   │──────────────▶│    Redis    │◀───────────│   FastAPI   │ │
│  │  /dispatch  │               │   (Broker)  │            │  /stream    │ │
│  └─────────────┘               └──────┬──────┘            └─────────────┘ │
│                                       │                          ▲         │
│                                       │ dequeue                  │         │
│                                       ▼                          │         │
│                               ┌─────────────┐                    │         │
│                               │  Dramatiq   │                    │         │
│                               │   Worker    │                    │         │
│                               └──────┬──────┘                    │         │
│                                      │                           │         │
│                                      │ spawn                     │         │
│                                      ▼                           │         │
│                               ┌─────────────┐    PUBLISH         │         │
│                               │ CLI Agent   │────────────────────┘         │
│                               │ subprocess  │    (line by line)            │
│                               │ agy/codex/  │                              │
│                               │ claude      │                              │
│                               └──────┬──────┘                              │
│                                      │                                     │
│                                      │ on complete                         │
│                                      ▼                                     │
│                               ┌─────────────┐                              │
│                               │ PostgreSQL  │                              │
│                               │ - AgentRun  │                              │
│                               │ - Output    │                              │
│                               │ - Task      │                              │
│                               └─────────────┘                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 3. Database Schema

```sql
-- New table: agent_runs
CREATE TABLE agent_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id VARCHAR(20) REFERENCES tasks(id) ON DELETE CASCADE,
    
    -- Agent info
    agent_id VARCHAR(50) NOT NULL,           -- @gemini-3.6-flash
    cli VARCHAR(20) NOT NULL,                -- agy, codex, claude
    command TEXT NOT NULL,                   -- Full command executed
    
    -- Execution state
    status VARCHAR(20) NOT NULL DEFAULT 'queued',  
    -- queued, running, success, failed, timeout, cancelled
    
    pid INTEGER,                             -- OS process ID (when running)
    dramatiq_message_id VARCHAR(50),         -- Dramatiq tracking
    
    -- Timing
    queued_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    timeout_seconds INTEGER DEFAULT 14400,   -- 4 hours default
    
    -- Result
    exit_code INTEGER,
    result_ref VARCHAR(255),                 -- git commit/branch/PR
    error_message TEXT,
    
    -- Output
    output_lines INTEGER DEFAULT 0,          -- Line count
    output_bytes INTEGER DEFAULT 0,          -- Total size
    
    -- Retry tracking
    attempt INTEGER DEFAULT 1,
    max_attempts INTEGER DEFAULT 3,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_agent_runs_task ON agent_runs(task_id);
CREATE INDEX idx_agent_runs_status ON agent_runs(status);

-- Output storage (for replay/history)
CREATE TABLE agent_output_chunks (
    id SERIAL PRIMARY KEY,
    run_id UUID REFERENCES agent_runs(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_output_chunks_run ON agent_output_chunks(run_id, chunk_index);
```

## 4. Component Design

### 4.1 Process Manager Service

```python
# backend/app/services/process_manager.py
import subprocess
import signal
import psutil
from typing import Optional, Generator
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
    ) -> Generator[str, None, ProcessResult]:
        """
        Run command and yield output lines as they come.
        Returns ProcessResult when done.
        
        Usage:
            for line in pm.run_with_streaming(cmd, cwd):
                if isinstance(line, ProcessResult):
                    # Done
                else:
                    # Output line
        """
        import os
        
        # Merge environment
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
            for line in iter(self.process.stdout.readline, ''):
                if self._cancelled:
                    self._terminate()
                    yield ProcessResult(ProcessStatus.CANCELLED, -1, "Cancelled by user")
                    return
                yield line.rstrip('\n')
            
            # Wait for completion with timeout
            try:
                exit_code = self.process.wait(timeout=self.timeout)
            except subprocess.TimeoutExpired:
                self._terminate()
                yield ProcessResult(ProcessStatus.TIMEOUT, -1, f"Timeout after {self.timeout}s")
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
                # Kill entire process group
                parent = psutil.Process(self.process.pid)
                children = parent.children(recursive=True)
                
                for child in children:
                    child.terminate()
                parent.terminate()
                
                # Wait briefly, then force kill
                gone, alive = psutil.wait_procs(children + [parent], timeout=5)
                for p in alive:
                    p.kill()
                    
            except psutil.NoSuchProcess:
                pass
    
    @property
    def pid(self) -> Optional[int]:
        return self.process.pid if self.process else None
```

### 4.2 Dramatiq Worker

```python
# backend/app/workers/agent_runner.py
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

# Configure broker with middleware
redis_broker = RedisBroker(url="redis://redis:6379/0")
redis_broker.add_middleware(CurrentMessage())
dramatiq.set_broker(redis_broker)

# Redis client for pub/sub
redis_client = redis.Redis.from_url("redis://redis:6379/0")


def get_channel(run_id: str) -> str:
    return f"agent_run:{run_id}:output"


def publish_line(run_id: str, line: str, line_type: str = "stdout"):
    """Publish a line to Redis for SSE streaming."""
    payload = json.dumps({
        "type": line_type,
        "content": line,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    redis_client.publish(get_channel(run_id), payload)


def publish_status(run_id: str, status: str, **kwargs):
    """Publish status update."""
    payload = json.dumps({
        "type": "status",
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **kwargs
    })
    redis_client.publish(get_channel(run_id), payload)


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
        
        # 3. Persist remaining buffer
        if chunk_buffer:
            _persist_chunk(db, run_id, chunk_buffer)
        
        # 4. Update final status
        run.status = result.status.value
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
            result.status.value,
            exit_code=result.exit_code,
            result_ref=run.result_ref,
            error=result.error
        )
        
        logger.info(f"Agent run {run_id} completed: {result.status.value}")
        
        # 7. Retry on failure (Dramatiq handles this via exception)
        if result.status == ProcessStatus.FAILED:
            message = CurrentMessage.get_current_message()
            if message and message.options.get("retries", 0) < 3:
                raise Exception(f"Agent failed: {result.error}")
        
    except Exception as e:
        logger.exception(f"Agent run {run_id} error: {e}")
        
        run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
        if run:
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
    chunk = AgentOutputChunk(
        run_id=run_id,
        chunk_index=db.query(AgentOutputChunk).filter(
            AgentOutputChunk.run_id == run_id
        ).count(),
        content="\n".join(lines)
    )
    db.add(chunk)
    db.commit()


def _parse_result_ref(repo_root: str) -> str | None:
    """Parse git commit/branch from repo."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip()[:12] if result.returncode == 0 else None
    except:
        return None


def _update_task_status(db: Session, task_id: str, status: str, result_ref: str = None, error: str = None):
    """Update task status in database."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.status = status
        if result_ref:
            task.result_ref = result_ref
        if error:
            task.error = error
        task.updated_at = datetime.now(timezone.utc)
        if status == "done":
            task.completed_at = datetime.now(timezone.utc)
        db.commit()
```

### 4.3 Dispatch API

```python
# backend/app/api/dispatch.py
import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.models import AgentRun, Task, Agent
from app.workers.agent_runner import run_agent
from app.services.command_builder import build_dispatch_command

router = APIRouter(prefix="/api", tags=["dispatch"])


class DispatchRequest(BaseModel):
    task_id: str
    agent_id: str
    timeout_seconds: int = 14400  # 4 hours default


class DispatchResponse(BaseModel):
    run_id: str
    task_id: str
    agent_id: str
    command: str
    status: str


@router.post("/dispatch", response_model=DispatchResponse)
def dispatch_agent(req: DispatchRequest, db: Session = Depends(get_db)):
    """
    Queue an agent to execute a task.
    Returns immediately with run_id for tracking.
    """
    # 1. Validate task exists
    task = db.query(Task).filter(Task.id == req.task_id).first()
    if not task:
        raise HTTPException(404, f"Task {req.task_id} not found")
    
    # 2. Validate agent exists
    agent = db.query(Agent).filter(Agent.id == req.agent_id).first()
    if not agent:
        raise HTTPException(404, f"Agent {req.agent_id} not found")
    
    # 3. Check no active run for this task
    active_run = db.query(AgentRun).filter(
        AgentRun.task_id == req.task_id,
        AgentRun.status.in_(["queued", "running"])
    ).first()
    if active_run:
        raise HTTPException(409, f"Task {req.task_id} already has active run: {active_run.id}")
    
    # 4. Build command
    command, repo_root, cli = build_dispatch_command(task, agent)
    
    # 5. Create run record
    run_id = str(uuid.uuid4())
    run = AgentRun(
        id=run_id,
        task_id=req.task_id,
        agent_id=req.agent_id,
        cli=cli,
        command=command,
        status="queued",
        timeout_seconds=req.timeout_seconds
    )
    db.add(run)
    
    # 6. Update task status
    task.status = "dispatched"
    task.executor = req.agent_id
    db.commit()
    
    # 7. Queue to Dramatiq
    run_agent.send(
        run_id=run_id,
        task_id=req.task_id,
        command=command,
        repo_root=repo_root,
        timeout_seconds=req.timeout_seconds
    )
    
    return DispatchResponse(
        run_id=run_id,
        task_id=req.task_id,
        agent_id=req.agent_id,
        command=command,
        status="queued"
    )


@router.get("/dispatch/{run_id}")
def get_run_status(run_id: str, db: Session = Depends(get_db)):
    """Get current status of an agent run."""
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        raise HTTPException(404, f"Run {run_id} not found")
    return run


@router.post("/dispatch/{run_id}/cancel")
def cancel_run(run_id: str, db: Session = Depends(get_db)):
    """Request cancellation of a running agent."""
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        raise HTTPException(404, f"Run {run_id} not found")
    
    if run.status not in ["queued", "running"]:
        raise HTTPException(400, f"Cannot cancel run in status: {run.status}")
    
    # TODO: Signal worker to cancel (via Redis)
    # For now, just mark as cancelled
    run.status = "cancelled"
    db.commit()
    
    return {"status": "cancelled"}
```

### 4.4 SSE Streaming API

```python
# backend/app/api/stream.py
import json
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import redis.asyncio as aioredis

from app.db.base import get_db
from app.db.models import AgentRun, AgentOutputChunk

router = APIRouter(prefix="/api", tags=["stream"])


async def create_redis_client():
    return await aioredis.from_url("redis://redis:6379/0")


@router.get("/runs/{run_id}/stream")
async def stream_run_output(run_id: str, db: Session = Depends(get_db)):
    """
    Stream real-time output from an agent run via SSE.
    
    Events:
    - stdout: Output line from agent
    - status: Status change (running, success, failed, etc.)
    - history: Buffered output from before connection
    - done: Stream complete
    """
    # Validate run exists
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        raise HTTPException(404, f"Run {run_id} not found")
    
    async def event_generator():
        redis = await create_redis_client()
        pubsub = redis.pubsub()
        channel = f"agent_run:{run_id}:output"
        
        try:
            # 1. Send any buffered history first
            chunks = db.query(AgentOutputChunk).filter(
                AgentOutputChunk.run_id == run_id
            ).order_by(AgentOutputChunk.chunk_index).all()
            
            for chunk in chunks:
                for line in chunk.content.split("\n"):
                    event = json.dumps({"type": "history", "content": line})
                    yield f"data: {event}\n\n"
            
            # 2. If already completed, send final status and done
            if run.status in ["success", "failed", "timeout", "cancelled"]:
                event = json.dumps({
                    "type": "status",
                    "status": run.status,
                    "exit_code": run.exit_code,
                    "result_ref": run.result_ref,
                    "error": run.error_message
                })
                yield f"data: {event}\n\n"
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                return
            
            # 3. Subscribe to live updates
            await pubsub.subscribe(channel)
            
            while True:
                message = await asyncio.wait_for(
                    pubsub.get_message(ignore_subscribe_messages=True),
                    timeout=30.0  # Heartbeat every 30s
                )
                
                if message is None:
                    # Send heartbeat
                    yield f": heartbeat\n\n"
                    continue
                
                data = json.loads(message["data"])
                yield f"data: {json.dumps(data)}\n\n"
                
                # Check for completion
                if data.get("type") == "status" and data.get("status") in [
                    "success", "failed", "timeout", "cancelled"
                ]:
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    break
                    
        except asyncio.TimeoutError:
            # Reconnect hint
            yield f"data: {json.dumps({'type': 'timeout', 'message': 'Reconnect'})}\n\n"
            
        finally:
            await pubsub.unsubscribe(channel)
            await redis.close()
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@router.get("/runs/{run_id}/output")
def get_run_output(run_id: str, db: Session = Depends(get_db)):
    """Get full output history (for completed runs)."""
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        raise HTTPException(404, f"Run {run_id} not found")
    
    chunks = db.query(AgentOutputChunk).filter(
        AgentOutputChunk.run_id == run_id
    ).order_by(AgentOutputChunk.chunk_index).all()
    
    output = "\n".join(chunk.content for chunk in chunks)
    
    return {
        "run_id": run_id,
        "status": run.status,
        "output": output,
        "line_count": run.output_lines,
        "byte_count": run.output_bytes
    }
```

## 5. Docker Compose

```yaml
# docker-compose.yml additions
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes  # Persistence
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  worker:
    build: ./backend
    command: >
      dramatiq app.workers.agent_runner
      --processes 2
      --threads 4
      --watch app
    depends_on:
      redis:
        condition: service_healthy
      db:
        condition: service_healthy
    environment:
      - DATABASE_URL=postgresql://ct:secret@db:5432/control_tower
      - REDIS_URL=redis://redis:6379/0
    volumes:
      # Mount repos for agent access
      - /home/lupca/projects:/home/lupca/projects:rw
    restart: unless-stopped

volumes:
  redis_data:
```

## 6. Error Handling & Recovery

### 6.1 Failure Scenarios

| Scenario | Detection | Recovery |
|----------|-----------|----------|
| Agent crash | Non-zero exit | Auto-retry (3x with backoff) |
| Timeout | TimeoutExpired | Mark timeout, no retry |
| Worker crash | Dramatiq middleware | Re-queue on restart |
| Redis down | Connection error | Worker waits, auto-reconnect |
| DB down | Connection error | Worker fails, manual restart |
| Server restart | Dramatiq persistence | Resume from queue |

### 6.2 Graceful Shutdown

```python
# backend/app/workers/__init__.py
import signal
import dramatiq

def shutdown_handler(signum, frame):
    """Handle SIGTERM for graceful shutdown."""
    dramatiq.get_broker().join(timeout=30000)  # 30s grace period

signal.signal(signal.SIGTERM, shutdown_handler)
```

### 6.3 Idempotency

- Run ID is UUID, generated before queue
- Check for existing active run before dispatch
- DB transaction ensures atomic status updates

## 7. Test Specifications

### 7.1 Unit Tests

```python
# backend/tests/unit/test_process_manager.py
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
        
        # Start long process
        gen = pm.run_with_streaming("sleep 60", "/tmp")
        next(gen)  # Start iteration
        
        # Request cancel
        pm.cancel()
        
        results = list(gen)
        final = [r for r in results if isinstance(r, ProcessResult)][0]
        assert final.status == ProcessStatus.CANCELLED
    
    def test_stdin_is_devnull(self):
        """Process stdin is /dev/null (no blocking)."""
        pm = ProcessManager()
        
        # Command that reads stdin would hang without /dev/null
        results = list(pm.run_with_streaming("cat", "/tmp"))
        
        final = [r for r in results if isinstance(r, ProcessResult)][0]
        assert final.status == ProcessStatus.COMPLETED
    
    def test_kills_child_processes(self):
        """Termination kills entire process tree."""
        pm = ProcessManager(timeout_seconds=1)
        
        # Parent spawns child
        results = list(pm.run_with_streaming(
            "bash -c 'sleep 60 & sleep 60'",
            "/tmp"
        ))
        
        final = [r for r in results if isinstance(r, ProcessResult)][0]
        assert final.status == ProcessStatus.TIMEOUT
        
        # Verify no orphan processes (would need psutil check)
```

```python
# backend/tests/unit/test_agent_runner.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.workers.agent_runner import run_agent, publish_line, publish_status


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
        """Agent run updates DB status to running."""
        # Setup mocks
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_run = Mock(id="run-123", status="queued")
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
```

### 7.2 Integration Tests

```python
# backend/tests/integration/test_dispatch_flow.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app
from app.db.models import Task, Agent, AgentRun


class TestDispatchFlow:
    """Integration tests for dispatch API."""
    
    @pytest.fixture
    def client(self, db_session):
        app.dependency_overrides[get_db] = lambda: db_session
        with TestClient(app) as c:
            yield c
    
    @pytest.fixture
    def sample_task(self, db_session):
        task = Task(id="T-INT-001", project="test", title="Test task", status="todo")
        db_session.add(task)
        db_session.commit()
        return task
    
    @pytest.fixture
    def sample_agent(self, db_session):
        agent = Agent(id="@test-agent", name="Test Agent", role="executor")
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
        # Create existing active run
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
```

```python
# backend/tests/integration/test_streaming.py
import pytest
import json
import asyncio
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

from app.main import app
from app.db.models import AgentRun, AgentOutputChunk


class TestStreaming:
    """Integration tests for SSE streaming."""
    
    @pytest.fixture
    def completed_run(self, db_session):
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
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            async with client.stream("GET", "/api/runs/run-stream-test/stream") as response:
                events = []
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        events.append(json.loads(line[5:].strip()))
                
                # Should have history lines
                history = [e for e in events if e["type"] == "history"]
                assert len(history) == 3
                
                # Should have status and done
                assert any(e["type"] == "status" for e in events)
                assert any(e["type"] == "done" for e in events)
    
    @pytest.mark.asyncio
    @patch('app.api.stream.create_redis_client')
    async def test_stream_receives_live_updates(self, mock_redis_factory, db_session):
        """Live updates are streamed via SSE."""
        # Setup mock pubsub
        mock_redis = AsyncMock()
        mock_pubsub = AsyncMock()
        mock_redis.pubsub.return_value = mock_pubsub
        mock_redis_factory.return_value = mock_redis
        
        # Simulate messages
        messages = [
            {"type": "message", "data": json.dumps({"type": "stdout", "content": "live1"}).encode()},
            {"type": "message", "data": json.dumps({"type": "stdout", "content": "live2"}).encode()},
            {"type": "message", "data": json.dumps({"type": "status", "status": "success"}).encode()},
        ]
        mock_pubsub.get_message = AsyncMock(side_effect=messages + [asyncio.TimeoutError()])
        
        # Create running run
        run = AgentRun(
            id="run-live-test",
            task_id="T-LIVE",
            agent_id="@test",
            cli="agy",
            command="test",
            status="running"
        )
        db_session.add(run)
        db_session.commit()
        
        app.dependency_overrides[get_db] = lambda: db_session
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            async with client.stream("GET", "/api/runs/run-live-test/stream") as response:
                events = []
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        events.append(json.loads(line[5:].strip()))
                        if len(events) >= 3:
                            break
                
                assert events[0]["content"] == "live1"
                assert events[1]["content"] == "live2"
                assert events[2]["status"] == "success"
    
    def test_get_full_output(self, completed_run, client, db_session):
        """GET /runs/{run_id}/output returns full history."""
        response = client.get("/api/runs/run-stream-test/output")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "line1" in data["output"]
        assert "line3" in data["output"]
        assert data["line_count"] == 3
```

### 7.3 Stress Tests

```python
# backend/tests/stress/test_concurrent_agents.py
import pytest
import asyncio
from concurrent.futures import ThreadPoolExecutor
from app.workers.agent_runner import run_agent


class TestConcurrentAgents:
    """Stress tests for concurrent agent execution."""
    
    @pytest.mark.slow
    def test_10_concurrent_short_agents(self, db_session):
        """10 agents running simultaneously complete without interference."""
        # Create 10 runs
        runs = []
        for i in range(10):
            run_id = f"stress-{i}"
            task_id = f"T-STRESS-{i}"
            # Quick command
            command = f"echo 'Agent {i} output'"
            runs.append((run_id, task_id, command))
        
        # Execute concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(run_agent, rid, tid, cmd, "/tmp")
                for rid, tid, cmd in runs
            ]
            
            results = [f.result() for f in futures]
        
        # Verify all completed
        for run_id, _, _ in runs:
            run = db_session.query(AgentRun).filter(AgentRun.id == run_id).first()
            assert run.status == "success"
    
    @pytest.mark.slow
    def test_agent_isolation(self, db_session):
        """Concurrent agents don't share state or interfere."""
        # Two agents writing to different outputs
        results = {}
        
        def run_and_capture(agent_num):
            run_id = f"iso-{agent_num}"
            output = []
            # Capture published lines
            # ... (mock redis to capture)
            return output
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            f1 = executor.submit(run_and_capture, 1)
            f2 = executor.submit(run_and_capture, 2)
            
            output1 = f1.result()
            output2 = f2.result()
        
        # Outputs should be distinct
        assert "Agent 1" in "\n".join(output1)
        assert "Agent 2" in "\n".join(output2)
        assert "Agent 2" not in "\n".join(output1)
```

### 7.4 Failure Recovery Tests

```python
# backend/tests/integration/test_failure_recovery.py
import pytest
from unittest.mock import patch, Mock
from app.workers.agent_runner import run_agent


class TestFailureRecovery:
    """Tests for failure handling and recovery."""
    
    def test_failed_agent_retries(self, db_session):
        """Failed agent is retried up to max_attempts."""
        # First two attempts fail, third succeeds
        attempt_count = [0]
        
        original_run = ProcessManager.run_with_streaming
        
        def mock_run(*args, **kwargs):
            attempt_count[0] += 1
            if attempt_count[0] < 3:
                yield ProcessResult(ProcessStatus.FAILED, 1, "Simulated failure")
            else:
                yield "Success output"
                yield ProcessResult(ProcessStatus.COMPLETED, 0, None)
        
        with patch.object(ProcessManager, 'run_with_streaming', mock_run):
            # This should retry automatically via Dramatiq
            run_agent("retry-test", "T-RETRY", "test", "/tmp")
        
        run = db_session.query(AgentRun).filter(AgentRun.id == "retry-test").first()
        assert run.status == "success"
        assert run.attempt == 3
    
    def test_timeout_does_not_retry(self, db_session):
        """Timeout is terminal, no retry."""
        with patch.object(
            ProcessManager, 
            'run_with_streaming',
            return_value=iter([ProcessResult(ProcessStatus.TIMEOUT, -1, "Timeout")])
        ):
            run_agent("timeout-test", "T-TIMEOUT", "sleep 999", "/tmp")
        
        run = db_session.query(AgentRun).filter(AgentRun.id == "timeout-test").first()
        assert run.status == "timeout"
        assert run.attempt == 1  # No retry
    
    def test_worker_crash_recovers(self, db_session):
        """Queued task recovers after worker restart."""
        # Simulate: task queued, worker dies, worker restarts
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
        
        # Worker restart would re-process queue
        # Dramatiq handles this automatically with Redis persistence
        
        # Manual simulation
        run_agent("crash-test", "T-CRASH", "echo recovered", "/tmp")
        
        db_session.refresh(run)
        assert run.status == "success"
    
    def test_db_error_marks_failed(self, db_session):
        """Database error during execution marks run as failed."""
        with patch('app.workers.agent_runner.SessionLocal') as mock_session:
            mock_db = Mock()
            mock_db.commit.side_effect = Exception("DB connection lost")
            mock_session.return_value = mock_db
            
            with pytest.raises(Exception):
                run_agent("db-error-test", "T-DB", "echo test", "/tmp")
        
        # Status should be failed (set before exception)
        # In real scenario, Dramatiq would retry
```

## 8. Acceptance Criteria

### Must Have
- [ ] AC1: `ProcessManager` handles subprocess lifecycle (start, stream, timeout, kill)
- [ ] AC2: `run_agent` Dramatiq actor với auto-retry, backoff
- [ ] AC3: Redis Pub/Sub streaming output line-by-line
- [ ] AC4: `POST /api/dispatch` queues agent và returns run_id
- [ ] AC5: `GET /api/runs/{id}/stream` SSE endpoint với history + live
- [ ] AC6: `AgentRun` table tracks full execution state
- [ ] AC7: Child processes killed on timeout/cancel
- [ ] AC8: Worker survives restart (Redis persistence)

### Should Have
- [ ] AC9: Output chunks persisted to DB for replay
- [ ] AC10: Cancel endpoint signals running agent
- [ ] AC11: Heartbeat keeps SSE connection alive
- [ ] AC12: Graceful shutdown waits for running agents

### Tests
- [ ] T1: Unit tests for ProcessManager (6 tests)
- [ ] T2: Unit tests for agent_runner (3 tests)
- [ ] T3: Integration tests for dispatch API (5 tests)
- [ ] T4: Integration tests for streaming (3 tests)
- [ ] T5: Stress test: 10 concurrent agents
- [ ] T6: Failure recovery tests (4 tests)

### Coverage
- [ ] ProcessManager: 90%+
- [ ] agent_runner: 85%+
- [ ] dispatch API: 95%+
- [ ] stream API: 90%+
