import re
from typing import Dict, Any
from app.graph.state import TaskState, GateType, FourEyesViolation
from app.graph.gates import (
    spec_gate,
    plan_gate,
    dispatch_gate,
    review_order_gate,
    verdict_gate
)


def parse_input_node(state: TaskState) -> Dict[str, Any]:
    raw = state.raw_input.strip()
    updates: Dict[str, Any] = {}

    if not raw:
        return updates

    # Check for review-order
    if raw.startswith("/review-order"):
        updates["current_gate"] = GateType.REVIEW_ORDER
        match = re.search(r"/review-order\s+([A-Za-z0-9_-]+)", raw)
        if match:
            updates["task_id"] = match.group(1)
    # Check for pm task creation
    elif raw.startswith("/pm"):
        updates["current_gate"] = GateType.SPEC

    return updates


def spec_node(state: TaskState) -> Dict[str, Any]:
    return spec_gate(state)


def plan_node(state: TaskState) -> Dict[str, Any]:
    return plan_gate(state)


def dispatch_node(state: TaskState) -> Dict[str, Any]:
    return dispatch_gate(state)


def review_order_node(state: TaskState) -> Dict[str, Any]:
    return review_order_gate(state)


def verdict_node(state: TaskState) -> Dict[str, Any]:
    return verdict_gate(state)
