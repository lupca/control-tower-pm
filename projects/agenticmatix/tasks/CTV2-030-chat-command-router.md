---
id: CTV2-030
title: "Chat command router + LangGraph integration"
status: done
priority: critical
risk: medium
executor: "@gemini-3.6-high"
reviewer: "@claude-opus"
deadline: 2026-07-28
created: 2026-07-26
files:
  - backend/app/api/chat.py
  - backend/app/services/command_router.py
  - backend/app/graph/builder.py
tests:
  - /pm command creates task
  - /dispatch command triggers gate
  - /verdict command closes task
  - Regular chat still works
---

# CTV2-030: Chat Command Router + LangGraph Integration

## Problem
Hiện tại chat UI chỉ forward text → LLM → response.
Slash commands (`/pm`, `/dispatch`, `/verdict`) không hoạt động.

## Solution

### 1. Command Router Service

```python
# backend/app/services/command_router.py
import re
from typing import Tuple, Optional
from app.graph.builder import get_graph
from app.graph.state import TaskState, GateType

COMMANDS = {
    "/pm": "create_task",
    "/dispatch": "dispatch_task", 
    "/review-order": "review_order",
    "/verdict": "verdict",
    "/status": "get_status",
    "/help": "show_help",
}

class CommandRouter:
    def __init__(self, db_session, graph=None):
        self.db = db_session
        self.graph = graph or get_graph()
    
    def parse(self, message: str) -> Tuple[Optional[str], str]:
        """
        Parse message for slash command.
        Returns: (command_name, args) or (None, original_message)
        """
        message = message.strip()
        if not message.startswith("/"):
            return None, message
        
        parts = message.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd in COMMANDS:
            return COMMANDS[cmd], args
        return None, message
    
    async def execute(self, command: str, args: str, session_id: str) -> dict:
        """Execute command and return result."""
        handler = getattr(self, f"_handle_{command}", None)
        if not handler:
            return {"error": f"Unknown command: {command}"}
        return await handler(args, session_id)
    
    async def _handle_create_task(self, args: str, session_id: str) -> dict:
        """
        /pm <task description> [--project <name>]
        Creates task and runs through Spec Gate.
        """
        # Parse args
        project = self._extract_flag(args, "--project") or "default"
        description = self._remove_flags(args)
        
        if not description:
            return {"error": "Usage: /pm <task description> [--project <name>]"}
        
        # Create initial state
        state = TaskState(
            raw_input=description,
            project=project,
            current_gate=GateType.SPEC
        )
        
        # Run through Spec Gate
        result = await self.graph.ainvoke(
            state.dict(),
            config={"configurable": {"thread_id": session_id}}
        )
        
        return {
            "action": "task_created",
            "task_id": result.get("task_id"),
            "title": result.get("title"),
            "acceptance_criteria": result.get("acceptance_criteria"),
            "current_gate": result.get("current_gate"),
            "awaiting_approval": result.get("awaiting_approval", False)
        }
    
    async def _handle_dispatch_task(self, args: str, session_id: str) -> dict:
        """
        /dispatch <task_id> @<agent>
        Runs task through Dispatch Gate.
        """
        parts = args.split()
        if len(parts) < 2:
            return {"error": "Usage: /dispatch <task_id> @<agent>"}
        
        task_id = parts[0]
        executor = parts[1]
        
        # Load existing state
        state = self._load_task_state(task_id)
        if not state:
            return {"error": f"Task {task_id} not found"}
        
        state.executor = executor
        state.current_gate = GateType.DISPATCH
        
        result = await self.graph.ainvoke(
            state.dict(),
            config={"configurable": {"thread_id": session_id}}
        )
        
        return {
            "action": "dispatched",
            "task_id": task_id,
            "executor": executor,
            "status": result.get("status"),
            "dispatched_at": result.get("dispatched_at")
        }
    
    async def _handle_verdict(self, args: str, session_id: str) -> dict:
        """
        /verdict <task_id> <pass|changes> --reviewer @<agent>
        Records review verdict.
        """
        # Parse: task_id, verdict, reviewer
        parts = args.split()
        if len(parts) < 2:
            return {"error": "Usage: /verdict <task_id> <pass|changes> --reviewer @<agent>"}
        
        task_id = parts[0]
        verdict = parts[1]
        reviewer = self._extract_flag(args, "--reviewer")
        
        if verdict not in ("pass", "changes"):
            return {"error": "Verdict must be 'pass' or 'changes'"}
        
        state = self._load_task_state(task_id)
        if not state:
            return {"error": f"Task {task_id} not found"}
        
        state.verdict = verdict
        state.reviewer = reviewer
        state.current_gate = GateType.VERDICT
        
        result = await self.graph.ainvoke(
            state.dict(),
            config={"configurable": {"thread_id": session_id}}
        )
        
        return {
            "action": "verdict_recorded",
            "task_id": task_id,
            "verdict": verdict,
            "status": result.get("status"),
            "completed_at": result.get("completed_at")
        }
```

### 2. Updated Chat API

```python
# backend/app/api/chat.py
from app.services.command_router import CommandRouter

@router.post("/chat")
async def chat_endpoint(req: ChatRequest, db: DBSession = Depends(get_db)):
    db_session = get_or_create_session(req.thread_id, db)
    
    # 1. Check for slash command
    router = CommandRouter(db)
    command, args = router.parse(req.message)
    
    if command:
        # Execute command, return structured result
        result = await router.execute(command, args, req.thread_id)
        
        # Format as chat response
        if "error" in result:
            response_text = f"❌ Error: {result['error']}"
        else:
            response_text = format_command_result(result)
        
        # Save to session and return
        save_message(db_session, "user", req.message, db)
        save_message(db_session, "assistant", response_text, db)
        
        return {"type": "command", "result": result, "message": response_text}
    
    # 2. Regular chat - forward to LLM
    # ... existing streaming logic ...
```

### 3. Command Format Examples

```
# Create task
/pm Add user authentication with OAuth2 --project topvnsport

# Dispatch to agent
/dispatch PMI-001 @gemini-3.6-flash

# Review order
/review-order PMI-001 --ref PR#123 --reviewer @gpt-5.6-sol

# Record verdict
/verdict PMI-001 pass --reviewer @gpt-5.6-sol

# Check status
/status PMI-001

# Help
/help
```

## Acceptance Criteria
- [ ] AC1: CommandRouter parses slash commands correctly
- [ ] AC2: `/pm` creates task + runs Spec Gate
- [ ] AC3: `/dispatch` runs Dispatch Gate + sets executor
- [ ] AC4: `/verdict` runs Verdict Gate + enforces four-eyes
- [ ] AC5: `/status` returns task state
- [ ] AC6: `/help` shows available commands
- [ ] AC7: Regular chat (no slash) still works as before
- [ ] AC8: Command results saved to session messages
- [ ] AC9: Error messages clear and actionable
