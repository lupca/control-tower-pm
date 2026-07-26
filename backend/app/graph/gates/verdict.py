from typing import Dict, Any
from app.graph.state import TaskState, GateType, FourEyesViolation


def verdict_gate(state: TaskState) -> Dict[str, Any]:
    reviewer = state.reviewer
    executor = state.executor

    # Enforce four-eyes
    if reviewer and executor and reviewer == executor:
        raise FourEyesViolation(
            f"Four-eyes violation: reviewer '{reviewer}' cannot be the same as executor '{executor}'"
        )

    verdict = state.verdict or "pass"
    if verdict == "pass":
        status = "done"
    else:
        status = "changes-requested"

    return {
        "current_gate": GateType.VERDICT,
        "verdict": verdict,
        "status": status,
        "awaiting_approval": False,
        "approval_prompt": None
    }
