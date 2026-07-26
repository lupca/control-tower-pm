import pytest
from app.db.models import Task, Session, AuditLog


def test_task_model_crud(db):
    task = Task(
        id="TEST-100",
        project="demo",
        title="Sample task",
        status="todo",
        acceptance_criteria=["AC1", "AC2"]
    )
    db.add(task)

    retrieved = db.query(Task).filter(Task.id == "TEST-100").first()
    assert retrieved is not None
    assert retrieved.project == "demo"
    assert len(retrieved.acceptance_criteria) == 2


def test_session_model_crud(db):
    session = Session(task_id="TEST-100", thread_id="thread-1", current_gate="spec")
    db.add(session)

    retrieved = db.query(Session).filter(Session.thread_id == "thread-1").first()
    assert retrieved is not None
    assert retrieved.current_gate == "spec"


def test_audit_log_crud(db):
    audit = AuditLog(task_id="TEST-100", action="dispatched", actor="@gemini-3.6")
    db.add(audit)

    retrieved = db.query(AuditLog).filter(AuditLog.task_id == "TEST-100").first()
    assert retrieved is not None
    assert retrieved.action == "dispatched"
