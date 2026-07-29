---
id: CTV2-116
title: "Polling Events Phase 3: API + Frontend"
status: done
priority: medium
risk: normal
created: 2026-07-28
deadline: null
executor: "@gpt-5.6-sol"
reviewer: "@claude-opus"
result_ref: 48bd9b6
depends_on: [CTV2-115]
files:
  - backend/app/api/events.py
  - frontend/src/hooks/useTaskEvents.ts
  - frontend/src/components/notifications/
tests: []
flows: []
predicted_success: high
prediction_factors:
  score: 0.8
  deductions:
    - "new API endpoint + frontend hook (-0.1)"
    - "UI component for notifications (-0.1)"
confidence_interval: [0.7, 0.9]
dispatched: 2026-07-28
updated: 2026-07-28
---

# CTV2-116: Polling Events Phase 3: API + Frontend

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Reference

Design doc: `docs/design/polling-notification-architecture.md`

## Acceptance Criteria

- [ ] **AC1**: `GET /api/events` endpoint với params: `since`, `task_id`, `types`
- [ ] **AC2**: Response format: `{events: [...], cursor: "...", has_more: bool}`
- [ ] **AC3**: Frontend `useTaskEvents` hook poll mỗi 10s với cursor
- [ ] **AC4**: Notification badge/panel hiển thị recent events
- [ ] **AC5**: Giữ nguyên SSE cho agent output (không thay đổi)

## Plan

*(Filled at Plan Gate)*
