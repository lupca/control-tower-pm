---
id: CTV2-072
title: "Refactor Prompt System + Tool Execution Loop for API Mode"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: high
risk: high
deadline: null
executor: "@gpt-5.6-luna"
reviewer: "@claude-opus"
result_ref: "bf047f0"
depends_on: []
files:
  - backend/app/prompts/global_context.md
  - backend/app/services/tool_definitions.py
  - backend/app/services/context_hierarchy.py
  - backend/app/services/coordinator.py
  - backend/app/services/command_router.py
  - backend/app/api/chat.py
flows: [chat-session, coordinator-invoke]
tests:
  - backend/tests/test_coordinator.py
  - backend/tests/unit/test_context_hierarchy.py
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: medium
prediction_factors:
  score: 0.6
  deductions:
    - "cross-cutting concern, touches coordinator core (-0.15)"
    - "requires tool execution loop (new feature) (-0.15)"
    - "risk: high (schemas/core changes) (-0.1)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-072: Refactor Prompt System + Tool Execution Loop for API Mode

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Context

Hiện tại V2 có vấn đề:
1. `app/prompts/global_context.md` không tồn tại - dùng hardcoded fallback 5 dòng
2. API mode (Kimi, SiliconFlow) gửi tools nhưng không execute tool_calls
3. LLM hallucinate references đến `.agents/rules/` không tồn tại
4. Tool definitions có schemas nhưng thiếu usage guide trong prompt

Reference V1: `AGENTS.md`, `AGENTS-REFERENCE.md`, `knowledge/guides/` có prompt structure tốt nhưng V2 đã đổi kiến trúc (DB-first, LangGraph, 3-tier context).

## Tiêu chí nghiệm thu (AC)

### Part A: Prompt System
- [x] AC1: Tạo `backend/app/prompts/global_context.md` với nội dung đầy đủ:
  - Role definition (Control Tower V2 coordinator)
  - Gate rules (Spec/Plan/Dispatch/Review/Verdict)
  - Tool usage instructions (khi nào dùng tool nào)
  - Output format guidelines
  - KHÔNG reference paths không tồn tại
- [x] AC2: Tool definitions trong prompt phải match `tool_definitions.py`
- [x] AC3: Context hierarchy inject prompt đúng thứ tự với cache_control

### Part B: Tool Execution Loop
- [x] AC4: `coordinator.py` implement tool execution loop cho API mode:
  - Nhận `response.tool_calls` từ adapter
  - Execute tools via `CommandRouter`
  - Append tool results vào messages
  - Gọi lại LLM với tool results
  - Repeat until LLM trả text without tool_calls
- [x] AC5: `chat.py` stream tool execution progress (không chỉ final text)
- [x] AC6: Tool results được persist vào session.messages với role="tool"

### Part C: Testing
- [x] AC7: Unit test cho tool execution loop
- [x] AC8: Integration test: user hỏi "có project nào?" → LLM gọi `get_status` → execute → trả lời đúng

## Verification

```bash
# Unit tests
cd /home/lupca/projects/control-tower-v2 && pytest backend/tests/unit/test_tool_execution.py -v

# Integration test
pytest backend/tests/integration/test_tool_chat.py -v

# Manual test với Kimi
# 1. Set Kimi as default coordinator
# 2. Chat: "tiến độ các project thế nào?"
# 3. Verify: LLM gọi get_status tool, execute, trả về project list
```

## Plan

### Phase 1: Research V1 vs V2 Architecture

1. **Đọc V1 prompt structure**:
   - `/home/lupca/projects/control-tower/AGENTS.md` - main rules
   - `/home/lupca/projects/control-tower/AGENTS-REFERENCE.md` - graph usage, audit
   - `/home/lupca/projects/control-tower/knowledge/guides/*.md` - tool guides
   
2. **So sánh với V2**:
   - V2 dùng DB thay vì File-Over-API
   - V2 có 3-tier context (Global/Project/Task) với caching
   - V2 có tool schemas trong `tool_definitions.py`
   - V2 thiếu: prompt file, tool execution loop

### Phase 2: Create `global_context.md`

3. **Tạo `backend/app/prompts/global_context.md`**:
   ```markdown
   # Control Tower V2 - Coordinator System Prompt
   
   You are Control Tower V2, an intelligent task coordination assistant.
   
   ## Your Role
   - Coordinate task lifecycle: create, plan, dispatch, review, verdict
   - Use tools to query and mutate project/task state
   - Follow strict gate validation rules
   
   ## Gate Rules
   - **Spec Gate**: Validate title + acceptance criteria before creating task
   - **Plan Gate**: Require step-by-step execution plan
   - **Dispatch Gate**: Assign executor, move to dispatched
   - **Review-Order Gate**: Request independent review (reviewer ≠ executor)
   - **Verdict Gate**: Record pass/changes, enforce four-eyes rule
   
   ## Available Tools
   (Tool schemas are injected separately. Use these tools when:)
   - `pm_create_task`: User asks to create/add a new task
   - `get_status`: User asks about task/project status
   - `dispatch_task`: User approves plan, ready to assign executor
   - `record_verdict`: Reviewer submits pass/changes verdict
   - `approve_gate`: User explicitly approves a pending gate
   - `cancel_task`: User wants to cancel a task
   - `compact_context`: Session getting long, need to summarize
   
   ## Output Guidelines
   - Be concise, terse responses
   - Use Vietnamese when user uses Vietnamese
   - Format task IDs as `[PROJECT-NNN]`
   - Always confirm mutations before executing
   ```

### Phase 3: Implement Tool Execution Loop

4. **Update `coordinator.py`**:
   ```python
   async def _execute_tools(
       self,
       tool_calls: list[dict],
       session: SessionModel,
   ) -> list[dict]:
       """Execute tool calls and return results."""
       command_router = CommandRouter(self.db)
       results = []
       for call in tool_calls:
           cmd = call.get("name")
           args = call.get("input", {})
           result = await command_router.execute_tool(cmd, args, session.id)
           results.append({
               "role": "tool",
               "tool_call_id": call.get("id"),
               "name": cmd,
               "content": json.dumps(result),
           })
       return results
   
   async def complete_turn_with_tools(self, ...):
       """Complete turn with tool execution loop."""
       max_iterations = 5
       for _ in range(max_iterations):
           response = await adapter.complete(messages, model, tools=tools)
           
           if not response.tool_calls:
               # Final response - persist and return
               return self._persist_success(...)
           
           # Execute tools
           tool_results = await self._execute_tools(response.tool_calls, session)
           
           # Append to messages
           messages.append({
               "role": "assistant",
               "content": response.text or "",
               "tool_calls": response.tool_calls,
           })
           messages.extend(tool_results)
           
           # Persist tool messages
           for msg in tool_results:
               self.append_message(session, **msg)
       
       raise RuntimeError("Tool execution loop exceeded max iterations")
   ```

5. **Update `command_router.py`**:
   - Add `execute_tool(cmd, args, session_id)` method
   - Map tool names to handlers (same as slash commands)

6. **Update `chat.py`**:
   - Stream tool execution progress
   - Handle tool results in SSE

### Phase 4: Testing

7. **Unit tests**: `backend/tests/unit/test_tool_execution.py`
8. **Integration tests**: `backend/tests/integration/test_tool_chat.py`

## Sub-tasks

- [ ] Research V1 prompt structure
- [ ] Create `backend/app/prompts/global_context.md`
- [ ] Add `execute_tool()` to CommandRouter
- [ ] Implement tool execution loop in coordinator
- [ ] Update chat.py for tool streaming
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Manual test với Kimi model

## Notes

- V1 reference: `AGENTS.md` §1-§4 (roles, gates, lifecycle)
- V2 context hierarchy: `context_hierarchy.py` (3-tier with caching)
- Tool schemas: `tool_definitions.py` (eager + deferred tools)
- CLI mode already works (claude, agy, codex handle tools internally)
- Only API mode (OpenAI adapter) needs this fix
