---
id: CTV2-117
title: "Polling Events Phase 4: LLM Context Integration"
status: done
priority: medium
risk: normal
created: 2026-07-28
deadline: null
executor: "@antigravity-3.6-high"
reviewer: "@claude-opus"
result_ref: 9892b9a
depends_on: [CTV2-114]
files:
  - backend/app/services/context_hierarchy.py
tests: []
flows: []
predicted_success: high
prediction_factors:
  score: 0.8
  deductions:
    - "modifying context builder (-0.1)"
    - "removing rollup from session.messages (-0.1)"
confidence_interval: [0.7, 0.9]
dispatched: 2026-07-28
updated: 2026-07-28
---

# CTV2-117: Polling Events Phase 4: LLM Context Integration

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Reference

Design doc: `docs/design/polling-notification-architecture.md`

## Acceptance Criteria

- [x] **AC1**: `context_hierarchy.py` có method `_get_recent_task_events(task_id, since)` đọc từ `task_events` table
- [x] **AC2**: `build_messages()` inject recent task events vào context khi có task_id
- [x] **AC3**: Remove rollup logic từ `session.messages` (nếu còn)
- [x] **AC4**: Integration test: LLM nhận được task events trong context

## Plan

*(Filled at Plan Gate)*
