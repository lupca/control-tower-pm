from app.graph.state import TaskState, GateType, Mode


def route_next_gate(state: TaskState) -> str:
    # Verdict input directly moves to verdict_node
    if state.verdict is not None:
        return "verdict_node"

    # Review order command
    if state.raw_input.strip().startswith("/review-order") or state.current_gate == GateType.REVIEW_ORDER:
        return "review_order_node"

    # Bypass mode flow
    if state.mode == Mode.BYPASS:
        if state.current_gate == GateType.SPEC:
            return "plan_node"
        elif state.current_gate == GateType.PLAN:
            return "dispatch_node"

    # Supervised flow with approval check
    if state.current_gate == GateType.SPEC:
        if state.approval == "approve":
            return "plan_node"
        return "spec_node"

    if state.current_gate == GateType.PLAN:
        if state.approval == "approve":
            return "dispatch_node"
        return "plan_node"

    if state.current_gate == GateType.DISPATCH:
        return "dispatch_node"

    return "spec_node"
