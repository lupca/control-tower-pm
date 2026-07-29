---
id: CTV2-114
title: "Polling Events Phase 1: Database + Service"
status: done
priority: high
risk: normal
created: 2026-07-28
deadline: null
executor: "@antigravity-3.6-high"
reviewer: "@claude-opus"
result_ref: 48193af
depends_on: []
files:
  - backend/alembic/versions/
  - backend/app/db/models.py
  - backend/app/services/task_event_service.py
tests: []
flows: []
predicted_success: high
prediction_factors:
  score: 0.8
  deductions:
    - "greenfield service, no existing tests (-0.1)"
    - "migration + model + service in one task (-0.1)"
confidence_interval: [0.7, 0.9]
dispatched: 2026-07-28
updated: 2026-07-28
---

# CTV2-114: Polling Events Phase 1: Database + Service

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Reference

Design doc: `docs/design/polling-notification-architecture.md`

## Acceptance Criteria

- [ ] **AC1**: Alembic migration tạo `task_events` table với schema từ design doc
- [ ] **AC2**: `TaskEvent` SQLAlchemy model với fields: `id`, `task_id`, `event_type`, `payload`, `created_at`, `consumed_at`
- [ ] **AC3**: `TaskEventService.emit(task_id, event_type, payload)` function ghi event vào DB
- [ ] **AC4**: Unit tests cho emit function

## Plan

*(Filled at Plan Gate)*
