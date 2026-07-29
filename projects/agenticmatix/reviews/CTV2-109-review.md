---
id: CTV2-109
task_path: projects/control-tower-v2/tasks/CTV2-109-unify-agent-suggestion-fix-spec-plan-gate.md
project: control-tower-v2
result_ref: ef08f4c
executor: "@claude-sonnet-high"
reviewer: "@claude-opus"
status: passed
issued: 2026-07-28
verdict: pass
verdict_date: 2026-07-28
---

# Phieu Review: CTV2-109 — Unify agent suggestion & fix spec_plan_model gate flow

- Du an: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task goc: `projects/control-tower-v2/tasks/CTV2-109-unify-agent-suggestion-fix-spec-plan-gate.md`
- Result-ref: ef08f4c
- Executor: @claude-sonnet-high
- Reviewer: @claude-opus
- Ngay phat phieu: 2026-07-28

## Acceptance Criteria can verify

1. [x] Tao `AgentSuggester` service tai su dung cho moi role:
   - Method `suggest(task, role="executor"|"reviewer"|"coordinator"|"spec_plan", top_n=3)`
   - Filter agents by capability matching role
   - Reuse scoring logic tu `AgentMatcher`
2. [x] Xoa `spec_plan_model` gate:
   - Xoa `resolve_spec_plan_model()` va `request_spec_plan_model()` tu `task_orchestration.py`
   - Xoa gate type `"spec_plan_model"` tu moi noi
3. [x] Update `generate_spec_plan` tool:
   - Them optional `agent_id` parameter
   - Neu khong truyen -> dung `AgentSuggester.suggest(task, role="spec_plan", top_n=1)`
   - Neu khong tim duoc agent -> raise `ConfigurationError` (khong fallback)
4. [x] Update `global_context.md` prompt:
   - Clarify Spec/Plan Gate flow
   - Document `generate_spec_plan(task_id, [agent_id])` usage
5. [x] Update tool schema trong `tool_registry.py`:
   - Add `agent_id` optional parameter to `generate_spec_plan`
6. [x] Xoa `spec_plan_model` setting tu `entity_admin.py`
7. [x] Tests pass:
   - Update existing tests for new flow
   - Add test: `generate_spec_plan` auto-suggests agent when not provided
   - Add test: `generate_spec_plan` errors when no suitable agent found

## Definition of Done (AGENTS.md muc 3)

- [x] Toan bo AC pass
- [x] Test lien quan xanh 100%:
  - backend/tests/test_task_orchestration.py
  - backend/tests/test_spec_plan_generator.py
  - backend/tests/test_agent_matcher.py
  - backend/tests/test_command_router.py
- [x] Khong regression (test khac trong module van xanh)
- [x] Reviewer khac executor (ban dang review, hay xac nhan ban != @claude-sonnet-high)

## Test goi y chay trong repo code

```bash
# All tests pass
pytest backend/tests/test_task_orchestration.py backend/tests/test_spec_plan_generator.py backend/tests/test_agent_matcher.py backend/tests/test_command_router.py -v

# spec_plan_model gate removed
grep -r "spec_plan_model" backend/app/ | grep -v ".pyc" | wc -l  # Should be 0
```

## Cau hoi rui ro (tu code-review-graph, tinh)

- **Hub nodes touched**: `TaskOrchestrationService` (degree 90), `CommandRouter` (degree 121)
- **Bridge node touched**: `generate_spec_plan` — architectural chokepoint
- **Prompt change**: `global_context.md` affects coordinator behavior
- **Blast radius**: 8 files

## Review Toolchain

Chay review theo repo's toolchain:
```
cat .claude/review-toolchain.md
```
Repo PHAI khai bao toolchain. Voi moi tool trong pipeline:
- Preflight theo knowledge/tools/tool-registry.md (health_check -> install neu can -> re-check)
- Tool required=hard ma preflight fail sau install -> BLOCK + escalate, khong review voi partial tools
- /code-review la baseline tool trong registry, chay cung (khong thay the) cac tools khac

Chay tat ca tools trong pipeline, aggregate ket qua, roi verify tung AC item.

## Tra ket qua

Sau khi review xong, bao lai cho control-tower bang lenh:
`/verdict CTV2-109 <pass|changes> --reviewer @claude-opus [--commit <hash>] [--notes "..."]`

---

## Verdict

**PASS** — All ACs verified at commit ef08f4c.

### Verification Summary

| File | Verified |
|------|----------|
| `agent_suggester.py` | Role-aware filtering with _ROLE_CAPABILITIES mapping |
| `task_orchestration.py` | -143 lines: `resolve_spec_plan_model` and `request_spec_plan_model` removed |
| `command_router.py` | `_handle_generate_spec_plan` uses AgentSuggester, errors on no agent |
| `spec_plan_generator.py` | Takes `Agent` directly, raises ConfigurationError if None |
| `tool_registry.py` | Optional `agent_id` parameter added |
| `global_context.md` | Documents `generate_spec_plan(task_id, [agent_id])` |
| `entity_admin.py` | `spec_plan_model` setting removed |
| Tests | All test files contain required coverage |

### grep verification
```
grep -r "spec_plan_model" backend/app/ | grep -v ".pyc" | wc -l  # 0
```

Reviewed by: @claude-opus
Date: 2026-07-28
