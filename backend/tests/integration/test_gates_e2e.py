import pytest
from app.graph.state import TaskState, GateType, Mode, FourEyesViolation
from app.graph.gates.spec import spec_gate
from app.graph.gates.plan import plan_gate
from app.graph.gates.dispatch import dispatch_gate
from app.graph.gates.review import review_order_gate
from app.graph.gates.verdict import verdict_gate
from app.db.models import Task, Session, AuditLog


def test_spec_gate_isolated():
    state = TaskState(raw_input="/pm add feature --project sample")
    res = spec_gate(state)
    assert res["project"] == "sample"
    assert res["task_id"] == "SAMPLE-001"
    assert res["current_gate"] == GateType.SPEC
    assert len(res["acceptance_criteria"]) > 0


def test_plan_gate_isolated():
    state = TaskState(task_id="TEST-001", title="Write tests", acceptance_criteria=["AC1"])
    res = plan_gate(state)
    assert res["current_gate"] == GateType.PLAN
    assert res["plan"] is not None


def test_dispatch_gate_isolated():
    state = TaskState(task_id="TEST-001", executor="@alice")
    res = dispatch_gate(state)
    assert res["current_gate"] == GateType.DISPATCH
    assert res["status"] == "dispatched"
    assert res["executor"] == "@alice"


def test_review_order_gate_isolated():
    state = TaskState(raw_input="/review-order TEST-001", result_ref="ref123")
    res = review_order_gate(state)
    assert res["status"] == "in-review"
    assert res["current_gate"] == GateType.REVIEW_ORDER


def test_verdict_gate_pass_and_four_eyes():
    # Pass case
    state_valid = TaskState(executor="@alice", reviewer="@bob", verdict="pass")
    res_valid = verdict_gate(state_valid)
    assert res_valid["status"] == "done"
    assert res_valid["verdict"] == "pass"

    # Four-eyes failure case
    state_invalid = TaskState(executor="@alice", reviewer="@alice", verdict="pass")
    with pytest.raises(FourEyesViolation):
        verdict_gate(state_invalid)


def test_supervised_mode_pause_at_gates(graph):
    # 1. Spec phase - supervised mode
    res1 = graph.invoke({"raw_input": "/pm feature X --project proj", "mode": Mode.SUPERVISED})
    assert res1["current_gate"] == GateType.SPEC
    assert res1["awaiting_approval"] is True

    # 2. Approve spec -> Plan phase
    res2 = graph.invoke({"approval": "approve"})
    assert res2["current_gate"] == GateType.PLAN
    assert res2["awaiting_approval"] is True

    # 3. Approve plan -> Dispatch phase
    res3 = graph.invoke({"approval": "approve"})
    assert res3["current_gate"] == GateType.DISPATCH
    assert res3["status"] == "dispatched"
    assert res3["awaiting_approval"] is False


def test_db_persistence_integration(db):
    task = Task(id="DB-001", project="DB", title="DB Task", status="todo")
    db.add(task)

    fetched = db.query(Task).filter(Task.id == "DB-001").first()
    assert fetched is not None
    assert fetched.title == "DB Task"

    session = Session(task_id="DB-001", current_gate="spec")
    db.add(session)

    audit = AuditLog(task_id="DB-001", action="gate_pass", actor="@antigravity")
    db.add(audit)

    logs = db.query(AuditLog).filter(AuditLog.task_id == "DB-001").all()
    assert len(logs) == 1
    assert logs[0].action == "gate_pass"
