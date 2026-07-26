import os
from typing import Dict, Any
from app.graph.state import TaskState, GateType


def plan_gate(state: TaskState) -> Dict[str, Any]:
    plan_text = f"1. Implement {state.title}\n2. Run tests and verify."

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            resp = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": f"Create implementation plan for: {state.title}\nAcceptance Criteria: {state.acceptance_criteria}"
                }]
            )
            plan_text = resp.content[0].text
        except Exception:
            pass

    return {
        "current_gate": GateType.PLAN,
        "plan": plan_text,
        "awaiting_approval": state.mode == "supervised",
        "approval_prompt": f"Approve plan for {state.task_id}?" if state.mode == "supervised" else None
    }
