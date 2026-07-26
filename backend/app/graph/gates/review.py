import re
from typing import Dict, Any
from app.graph.state import TaskState, GateType


def review_order_gate(state: TaskState) -> Dict[str, Any]:
    raw = state.raw_input.strip()
    task_id = state.task_id

    if raw.startswith("/review-order"):
        match = re.search(r"/review-order\s+([A-Za-z0-9_-]+)", raw)
        if match:
            task_id = match.group(1)

    reviewer = state.reviewer or "@antigravity"

    return {
        "task_id": task_id,
        "current_gate": GateType.REVIEW_ORDER,
        "reviewer": reviewer,
        "status": "in-review",
        "awaiting_approval": False,
        "approval_prompt": None
    }
