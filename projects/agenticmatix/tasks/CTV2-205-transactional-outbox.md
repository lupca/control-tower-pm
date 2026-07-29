---
id: CTV2-205
title: "Implement transactional outbox pattern"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: urgent
risk: high
deadline: null
executor: "@claude-sonnet-high"
reviewer: "@gemini-3.1-pro-high"
result_ref: "0514cbd..9854411"
depends_on: []
files:
  - backend/app/db/models.py
  - backend/app/services/task_orchestration.py
  - backend/app/workers/
flows: []
tests:
  - backend/tests/test_task_orchestration.py
dispatched: 2026-07-29
in_review: null
predicted_success: medium
prediction_factors:
  score: 0.5
  deductions:
    - "new_pattern: outbox requires worker (-0.3)"
    - "reliability: critical path (-0.2)"
confidence_interval: [0.4, 0.6]
created: 2026-07-29
updated: 2026-07-29
---

# CTV2-205: Implement transactional outbox pattern

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Context

Current flow: INSERT AgentRun → COMMIT → run_agent.send(). If crash between commit and send, run stays queued forever with no job.

## Tiêu chí nghiệm thu (AC)

- [ ] Create OutboxEvent model: id, event_type, payload (JSON), created_at, published_at, attempts
- [ ] In same transaction: create AgentRun + create OutboxEvent(type=run_requested)
- [ ] Create outbox_publisher worker that polls unpublished events, enqueues Dramatiq, marks published
- [ ] Add reconciliation job to detect orphaned runs (queued but no message_id)
- [ ] Backoff and dead-letter for repeatedly failed publishes
- [ ] Tests: verify AgentRun + OutboxEvent created atomically

## Verification

- `pytest backend/tests/test_task_orchestration.py -v` → 100% pass
- Manual: kill process after commit, verify reconciliation picks up orphan

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] Create OutboxEvent model
- [ ] Create alembic migration
- [ ] Update _apply_gate to create OutboxEvent
- [ ] Create outbox_publisher worker
- [ ] Add reconciliation job
- [ ] Add tests
