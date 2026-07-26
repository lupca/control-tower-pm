---
id: CTV2-053
title: "Hierarchical Context Chat System (Global/Project/Task)"
status: done
priority: high
risk: normal
deadline: null
executor: "@claude-sonnet-high"
reviewer: "@claude-opus"
result_ref: "2b4542e"
depends_on: []
files:
  - backend/app/services/context_hierarchy.py
  - backend/app/services/coordinator.py
  - backend/app/db/models.py
  - backend/app/api/chat.py
flows: []
tests:
  - backend/tests/test_coordinator.py
  - backend/tests/integration/test_full_flow.py
dispatched: 2026-07-26
in_review: 2026-07-26
predicted_success: medium
prediction_factors:
  score: 0.65
  deductions:
    - "cross-cutting concern, touches coordinator core (-0.15)"
    - "requires LLM API changes for cache_control (-0.1)"
    - "needs token measurement instrumentation (-0.1)"
created: 2026-07-26
updated: 2026-07-26
confidence_interval: [0.5, 0.7]
---

# CTV2-053: Hierarchical Context Chat System (Global/Project/Task)

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Bối cảnh

User chat với CTV2 qua CLI hoặc API (`/api/chat`). Hiện tại `CoordinatorService` không có cơ chế inject context theo cấp độ - mỗi turn gửi toàn bộ `session.messages` mà không phân biệt Global/Project/Task context.

## Tiêu chí nghiệm thu (AC)

- [x] **Global Context**: System prompt + gate rules, load 1 lần khi khởi động, dùng chung cho tất cả projects
- [x] **Project Context**: Load từ `Project.description` + `projects/{id}/context.md` (nếu có), cache per session
- [x] **Task Context**: `Session.messages` của task hiện tại, append mỗi turn
- [x] Context được inject theo thứ tự: Global → Project → Task vào mỗi LLM call
- [x] Anthropic `cache_control` markers tại tier boundaries để tối ưu token
- [x] Token metrics: log `input_tokens`, `cached_tokens` cho mỗi turn để đo cache hit rate
- [x] Context compaction: khi `Session.messages` > threshold, summarize thành 1 message

## Verification

- `pytest backend/tests/test_context_hierarchy.py -v` → 100% pass
- `pytest backend/tests/integration/test_full_flow.py -v` → verify context injection
- Check `LLMUsage.cached_tokens > 0` sau turn thứ 2 trong cùng session
- Manual: gửi 3 turns, verify Global+Project context không gửi lại (check logs)

## Plan

### Phase 1: Context Hierarchy Service

1. **`backend/app/services/context_hierarchy.py`** (new file)
   ```python
   class ContextHierarchy:
       def __init__(self, db: Session):
           self.db = db
           self._global_context: list[dict] | None = None  # cached
       
       def get_global_context(self) -> list[dict]:
           """System prompt + gate rules. Cached in memory."""
           if self._global_context is None:
               self._global_context = self._load_global()
           return self._global_context
       
       def get_project_context(self, project_id: str) -> list[dict]:
           """Project description + context.md. Cached per session."""
           project = self.db.query(Project).get(project_id)
           messages = []
           if project and project.description:
               messages.append({
                   "role": "user",
                   "content": f"[Project Context: {project.name}]\n{project.description}"
               })
           return messages
       
       def get_task_context(self, session: SessionModel) -> list[dict]:
           """Session messages for current task."""
           return session.messages or []
       
       def build_messages(self, session: SessionModel, project_id: str) -> list[dict]:
           """Compose 3 tiers with cache_control markers."""
           messages = []
           
           # Tier 1: Global (with cache_control)
           global_ctx = self.get_global_context()
           if global_ctx:
               messages.extend(global_ctx)
               messages[-1]["cache_control"] = {"type": "ephemeral"}
           
           # Tier 2: Project (with cache_control)
           project_ctx = self.get_project_context(project_id)
           if project_ctx:
               messages.extend(project_ctx)
               messages[-1]["cache_control"] = {"type": "ephemeral"}
           
           # Tier 3: Task (no cache_control - dynamic)
           messages.extend(self.get_task_context(session))
           
           return messages
   ```

### Phase 2: Integrate với CoordinatorService

2. **Update `backend/app/services/coordinator.py`**
   - Import `ContextHierarchy`
   - Trong `stream_turn()`, thay vì gửi raw `session.messages`:
     ```python
     ctx = ContextHierarchy(self.db)
     messages = ctx.build_messages(session, project_id)
     ```
   - Pass `messages` vào LLM call

### Phase 3: DB Schema Update

3. **Update `backend/app/db/models.py`**
   - Add `Project.context_md` column (Text, nullable) để store project-specific context
   - Or: load từ file `projects/{id}/context.md` trong repo

### Phase 4: Token Telemetry

4. **Verify `LLMUsage` records `cached_tokens`**
   - Anthropic API returns `usage.cache_read_input_tokens`
   - Ensure `llm_client.py` captures và lưu vào `LLMUsage.cached_tokens`

### Phase 5: Context Compaction

5. **Add compaction logic**
   - Khi `len(session.messages) > 50` (configurable):
     - Call LLM để summarize conversation
     - Replace messages với summary
   - Triggered manually via `/compact` command hoặc auto khi threshold

## Findings (changes-requested round 1)

- [ ] **Bug `anthropic_adapter.py:98`**: `cache_control` ở request level là SAI - Anthropic API chỉ nhận trong content blocks
- [ ] **Thiếu deferred tool loading**: Research nói tiết kiệm ~10% context, chưa implement
- [ ] **Global context thiếu tool definitions**: Chỉ có system prompt, thiếu tool schemas
- [ ] **Không integrate LangGraph**: ContextHierarchy là standalone class, không dùng StateGraph/Checkpointer
- [ ] **Project context thiếu auto-memory**: Không học từ sessions trước, không có 25KB cap

## Sub-tasks

- [x] Create `backend/app/services/context_hierarchy.py` với `ContextHierarchy` class
- [x] Update `CoordinatorService.stream_turn()` để dùng `ContextHierarchy.build_messages()`
- [x] Add `cache_control` markers vào messages theo Anthropic spec
- [x] Verify `LLMUsage.cached_tokens` được capture từ API response
- [x] Add `Project.context_md` column hoặc file-based context loading
- [x] Write unit tests cho `ContextHierarchy`
- [x] Add integration test verify cache hit rate > 0% sau turn 2
- [x] (Optional) Add `/compact` command để trigger context compaction

## Token Optimization Strategy

```
Turn 1:
  Global (4K tokens)  → cache WRITE
  Project (2K tokens) → cache WRITE  
  Task (1K tokens)    → no cache
  Total: 7K input tokens, cost = full

Turn 2+:
  Global (4K tokens)  → cache READ (90% discount)
  Project (2K tokens) → cache READ (90% discount)
  Task (2K tokens)    → no cache
  Total: 8K input, nhưng 6K cached → effective cost ~2.6K

Expected savings: 60-70% sau turn 1
```
