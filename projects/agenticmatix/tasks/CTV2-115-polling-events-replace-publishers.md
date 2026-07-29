---
id: CTV2-115
title: "Polling Events Phase 2: Replace Publishers"
status: done
priority: high
risk: normal
created: 2026-07-28
deadline: null
executor: "@gpt-5.6-sol"
reviewer: "@claude-opus"
result_ref: 312936d
depends_on: [CTV2-114]
files:
  - backend/app/workers/
  - backend/app/services/cli_dispatcher.py
  - backend/app/graph/nodes/dispatch.py
tests: []
flows: []
predicted_success: high
prediction_factors:
  score: 0.75
  deductions:
    - "refactoring existing code paths (-0.15)"
    - "removing old notification system (-0.1)"
confidence_interval: [0.65, 0.85]
dispatched: 2026-07-28
updated: 2026-07-28
---

# CTV2-115: Polling Events Phase 2: Replace Publishers

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Reference

Design doc: `docs/design/polling-notification-architecture.md`

## Acceptance Criteria

- [ ] **AC1**: Worker: Thay `_record_task_rollup()` → `emit_task_event()` cho `done`, `failed`, `running`
- [ ] **AC2**: Gate nodes: Thay `_notify_gate_pending()` → `emit_task_event("gate_pending")`
- [ ] **AC3**: Dispatch: Emit `cancelled` event khi user cancel
- [ ] **AC4**: Remove `publish_event()`, `publish_task_event()` nếu không còn caller
- [ ] **AC5**: Existing flows vẫn hoạt động (smoke test)

## Plan

*(Filled at Plan Gate)*
