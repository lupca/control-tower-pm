import pytest
from app.graph.state import TaskState, GateType, Mode, FourEyesViolation
from app.graph.router import route_next_gate


def test_task_state_defaults():
    state = TaskState()
    assert state.current_gate == GateType.SPEC
    assert state.status == "todo"
    assert state.mode == Mode.SUPERVISED
    assert state.awaiting_approval is False


def test_router_logic():
    state_bypass = TaskState(current_gate=GateType.SPEC, mode=Mode.BYPASS)
    next_node = route_next_gate(state_bypass)
    assert next_node == "plan_node"

    state_review = TaskState(raw_input="/review-order CTV2-001")
    next_node_review = route_next_gate(state_review)
    assert next_node_review == "review_order_node"

    state_verdict = TaskState(verdict="pass")
    next_node_verdict = route_next_gate(state_verdict)
    assert next_node_verdict == "verdict_node"
