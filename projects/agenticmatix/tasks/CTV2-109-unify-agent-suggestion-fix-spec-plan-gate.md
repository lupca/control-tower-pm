---
id: CTV2-109
title: "Unify agent suggestion & fix spec_plan_model gate flow"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: high
risk: high
deadline: null
executor: "@claude-sonnet-high"
reviewer: "@claude-opus"
result_ref: "ef08f4c"
depends_on: []
files:
  - backend/app/services/task_orchestration.py
  - backend/app/services/spec_plan_generator.py
  - backend/app/services/command_router.py
  - backend/app/services/agent_matcher.py
  - backend/app/services/tool_registry.py
  - backend/app/services/entity_admin.py
  - backend/app/prompts/global_context.md
flows: []
tests:
  - backend/tests/test_task_orchestration.py
  - backend/tests/test_spec_plan_generator.py
  - backend/tests/test_agent_matcher.py
  - backend/tests/test_command_router.py
dispatched: 2026-07-28
in_review: 2026-07-28
predicted_success: low
prediction_factors:
  score: 0.3
  deductions:
    - "hub node: TaskOrchestrationService (degree 90) (-0.2)"
    - "hub node: CommandRouter (degree 121) (-0.2)"
    - "blast_radius: 8 files (-0.3)"
created: 2026-07-28
updated: 2026-07-28
---

# CTV2-109: Unify agent suggestion & fix spec_plan_model gate flow

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Context

Bug phát hiện: `spec_plan_model` gate crash khi approve (`KeyError: 'expected_status'`). 

Root causes:
1. `spec_plan_model` gate implement riêng, không follow pattern của dispatch
2. `suggested_model` có thể null → `ConfigurationError` sau khi approve
3. Idempotency key tăng sau approve → second call tạo pending mới
4. Không có cách override model khi approve

## Tiêu chí nghiệm thu (AC)

1. [ ] Tạo `AgentSuggester` service tái sử dụng cho mọi role:
   - Method `suggest(task, role="executor"|"reviewer"|"coordinator"|"spec_plan", top_n=3)`
   - Filter agents by capability matching role
   - Reuse scoring logic từ `AgentMatcher`
2. [ ] Xóa `spec_plan_model` gate:
   - Xóa `resolve_spec_plan_model()` và `request_spec_plan_model()` từ `task_orchestration.py`
   - Xóa gate type `"spec_plan_model"` từ mọi nơi
3. [ ] Update `generate_spec_plan` tool:
   - Thêm optional `agent_id` parameter
   - Nếu không truyền → dùng `AgentSuggester.suggest(task, role="spec_plan", top_n=1)`
   - Nếu không tìm được agent → raise `ConfigurationError` (không fallback)
4. [ ] Update `global_context.md` prompt:
   - Clarify Spec/Plan Gate flow
   - Document `generate_spec_plan(task_id, [agent_id])` usage
5. [ ] Update tool schema trong `tool_registry.py`:
   - Add `agent_id` optional parameter to `generate_spec_plan`
6. [ ] Xóa `spec_plan_model` setting từ `entity_admin.py`
7. [ ] Tests pass:
   - Update existing tests for new flow
   - Add test: `generate_spec_plan` auto-suggests agent when not provided
   - Add test: `generate_spec_plan` errors when no suitable agent found

## Verification

```bash
# All tests pass
pytest backend/tests/test_task_orchestration.py backend/tests/test_spec_plan_generator.py backend/tests/test_agent_matcher.py backend/tests/test_command_router.py -v

# spec_plan_model gate removed
grep -r "spec_plan_model" backend/app/ | grep -v ".pyc" | wc -l  # Should be 0

# generate_spec_plan works without agent_id
# (manual test or integration test)
```

## Plan

### Phase 1: Create AgentSuggester service
1. Create `backend/app/services/agent_suggester.py`:
   - Extract reusable scoring logic from `AgentMatcher`
   - Add `role` parameter to filter by capability
   - Role mapping: `executor` → any, `reviewer` → any, `coordinator` → `capabilities LIKE '%coordinator%'`, `spec_plan` → `capabilities LIKE '%coordinator%' OR '%spec_plan%'`

### Phase 2: Remove spec_plan_model gate
2. In `task_orchestration.py`:
   - Delete `resolve_spec_plan_model()` (lines 167-236)
   - Delete `request_spec_plan_model()` (lines 238-308)
   - Remove any references to gate_type `"spec_plan_model"`

3. In `entity_admin.py`:
   - Remove `"spec_plan_model"` from settings descriptions (line ~312)

### Phase 3: Update generate_spec_plan flow
4. In `tool_registry.py`:
   - Update `generate_spec_plan` tool schema to add optional `agent_id` parameter

5. In `command_router.py` (`_handle_generate_spec_plan`):
   - Remove call to `service.request_spec_plan_model()`
   - If `agent_id` not provided → call `AgentSuggester.suggest(task, role="spec_plan", top_n=1)`
   - If no agent found → return error immediately
   - Pass agent directly to `generate_spec_plan()`

6. In `spec_plan_generator.py`:
   - Update `generate_spec_plan(task, repo_root, agent)` signature
   - Remove `model_config` dict handling, take `Agent` directly

### Phase 4: Update prompt
7. In `global_context.md`:
   - Update Spec/Plan Gate description to clarify flow
   - Add note about `generate_spec_plan(task_id, [agent_id])`

### Phase 5: Tests
8. Update tests:
   - Remove tests for `resolve_spec_plan_model`, `request_spec_plan_model`
   - Update `test_generate_spec_plan_*` tests
   - Add test: auto-suggest agent when not provided
   - Add test: error when no suitable agent found

## Sub-tasks

- [ ] Create `AgentSuggester` service in `backend/app/services/agent_suggester.py`
- [ ] Remove `resolve_spec_plan_model` and `request_spec_plan_model` from orchestration
- [ ] Update `_handle_generate_spec_plan` in command_router to use AgentSuggester
- [ ] Update `generate_spec_plan` function signature in spec_plan_generator.py
- [ ] Update tool schema in tool_registry.py
- [ ] Update global_context.md prompt
- [ ] Remove spec_plan_model setting from entity_admin.py
- [ ] Update/add tests

## Safety Notes

- **Hub nodes touched**: `TaskOrchestrationService`, `CommandRouter` — high blast radius
- **Bridge node touched**: `generate_spec_plan` — architectural chokepoint
- **Prompt change**: `global_context.md` affects coordinator behavior
- **Test thoroughly**: existing spec_plan tests may need significant updates

## Causal Analysis
- **Root cause**: spec_plan_model gate implemented separately without following dispatch pattern
- **Mechanism**: gate payload missing expected_status field → KeyError in _apply_gate; also suggested_model could be null after approval
- **Counterfactual**: if spec_plan_model followed dispatch pattern (resolve agent before gate creation), no crash would occur
- **Pattern**: [[ad-hoc-gate-pattern]]
