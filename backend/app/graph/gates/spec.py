import os
import re
from typing import Dict, Any
from app.graph.state import TaskState, GateType


def spec_gate(state: TaskState) -> Dict[str, Any]:
    raw = state.raw_input.strip()
    project = state.project
    title = state.title
    task_id = state.task_id

    # Parse raw input if project/title not set
    if raw.startswith("/pm"):
        # Format: /pm add tests --project demo
        # Format: /pm quick fix --project demo
        match = re.search(r"/pm\s+(.+?)(?:\s+--project\s+(\w+))?$", raw)
        if match:
            extracted_title = match.group(1).strip()
            extracted_proj = match.group(2)
            if extracted_proj:
                project = extracted_proj
            title = extracted_title

    if not project:
        project = "DEMO"
    if not title:
        title = raw or "Untitled Task"

    if not task_id:
        task_id = f"{project.upper()}-001"

    # LLM Call for AC (with try/except and mockable anthropic integration)
    ac = ["Generated AC 1", "Generated AC 2"]
    risk = "low"

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            resp = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
                messages=[{
                    "role": "user",
                    "content": f"Generate 2 acceptance criteria for task: {title} in project {project}"
                }]
            )
            # Parse response
            text = resp.content[0].text
            ac = [line.strip("- ").strip() for line in text.split("\n") if line.strip()]
        except Exception:
            pass

    return {
        "task_id": task_id,
        "project": project,
        "title": title,
        "current_gate": GateType.SPEC,
        "acceptance_criteria": ac,
        "awaiting_approval": state.mode == "supervised",
        "approval_prompt": f"Approve spec for {task_id}?" if state.mode == "supervised" else None
    }
