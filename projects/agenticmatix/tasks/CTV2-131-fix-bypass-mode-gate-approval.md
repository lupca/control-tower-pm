---
id: CTV2-131
title: "Fix bypass mode not auto-approving gates"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: high
risk: normal
deadline: null
executor: "@gpt-5.6-sol"
reviewer: "@claude-opus"
result_ref: "8e9ead8"
depends_on: []
files:
  - backend/app/services/task_orchestration.py
flows: []
tests:
  - backend/tests/unit/test_task_orchestration.py
dispatched: 2026-07-29
in_review: 2026-07-29
predicted_success: high
prediction_factors:
  score: 0.9
  deductions:
    - "single file change, low blast radius (-0.0)"
    - "existing tests cover gate logic (-0.0)"
    - "clear fix path (-0.1 conservative)"
created: 2026-07-29
updated: 2026-07-29
---

# CTV2-131: Fix bypass mode not auto-approving gates

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Tiêu chí nghiệm thu (AC)

- [x] AC1: `_request_gate()` computes effective mode via `mode_for_task(task)` before checking gate behavior, instead of reading stale `task.mode` directly
- [x] AC2: When `autonomy=auto` and task risk is within `auto_max_risk`, gates auto-approve without setting `awaiting_approval=True`
- [x] AC3: Existing test `test_bypass_dispatch_is_audited_and_idempotent` still passes
- [x] AC4: Add test case: task created with `mode=supervised` but autonomy policy changed to `auto` → dispatch gate should auto-approve

## Verification

- `cd /home/lupca/projects/control-tower-v2 && source .venv/bin/activate && pytest backend/tests/unit/test_task_orchestration.py -v` → 100% pass
- `grep -n "task.mode ==" backend/app/services/task_orchestration.py` → only in `decide_gate()` (for plan-only block), not in `_request_gate()` gate decision

## Plan

1. In `_request_gate()` at ~line 1044, before the `if task.mode == "plan-only"` check:
   - Add: `effective_mode = self.mode_for_task(task)`
2. Replace `task.mode` with `effective_mode` in the gate decision logic (lines 1059, 1074)
3. Optionally sync `task.mode = effective_mode` to DB for consistency (but this is secondary)
4. Add test: create task when autonomy=supervised, then change Setting to auto, verify dispatch auto-approves

## Sub-tasks

- [ ] Replace `task.mode` with computed `effective_mode` in `_request_gate()` gate decisions
- [ ] Add test for dynamic mode resolution scenario
