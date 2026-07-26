from typing import Dict, Any
from app.graph.state import TaskState, GateType


def dispatch_gate(state: TaskState) -> Dict[str, Any]:
    executor = state.executor or "@gemini-3.6"
    return {
        "current_gate": GateType.DISPATCH,
        "executor": executor,
        "status": "dispatched",
        "awaiting_approval": False,
        "approval_prompt": None
    }
