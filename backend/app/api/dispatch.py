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
    return {
        "id": run.id,
        "run_id": run.id,
        "task_id": run.task_id,
        "agent_id": run.agent_id,
        "cli": run.cli,
        "command": run.command,
        "status": run.status,
        "pid": run.pid,
        "queued_at": run.queued_at.isoformat() if run.queued_at else None,
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "completed_at": run.completed_at.isoformat() if run.completed_at else None,
        "exit_code": run.exit_code,
        "result_ref": run.result_ref,
        "error_message": run.error_message,
        "output_lines": run.output_lines,
        "output_bytes": run.output_bytes,
        "attempt": run.attempt
    }


@router.post("/dispatch/{run_id}/cancel")
def cancel_run(run_id: str, db: Session = Depends(get_db)):
    """Request cancellation of a running agent."""
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        raise HTTPException(404, f"Run {run_id} not found")

    if run.status not in ["queued", "running"]:
        raise HTTPException(400, f"Cannot cancel run in status: {run.status}")

    run.status = "cancelled"
    db.commit()

    return {"status": "cancelled"}
