---
id: CTV2-204
title: "Add task-level locking and idempotency constraints"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: urgent
risk: high
deadline: null
executor: "@claude-sonnet-high"
reviewer: "@gemini-3.1-pro-high"
result_ref: "6559ba0..0514cbd"
depends_on: []
files:
  - backend/app/db/models.py
  - backend/app/services/task_orchestration.py
flows: []
tests:
  - backend/tests/test_task_orchestration.py
dispatched: 2026-07-29
in_review: null
predicted_success: medium
prediction_factors:
  score: 0.5
  deductions:
    - "concurrency: complex locking (-0.3)"
    - "hub_node: Task, TaskOrchestrationService (-0.2)"
confidence_interval: [0.4, 0.6]
created: 2026-07-29
updated: 2026-07-29
---

# CTV2-204: Add task-level locking and idempotency constraints

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Context

advance_task can be triggered by multiple sources (nudge, retry, user, scheduler). Without locking, two actors can read status=todo and create duplicate runs.

## Tiêu chí nghiệm thu (AC)

- [ ] Add Task.version column for optimistic locking
- [ ] Use SELECT FOR UPDATE SKIP LOCKED on task in advance_task
- [ ] Add compare-and-set on status transitions: UPDATE WHERE status = :expected AND version = :expected_version
- [ ] Add UNIQUE(task_round_id, kind, attempt) constraint on AgentRun
- [ ] Add idempotency_key column to AgentRun with unique constraint
- [ ] Verify existing with_for_update() usage covers all race windows
- [ ] Tests: concurrent dispatch attempts result in exactly one run

## Verification

- `pytest backend/tests/test_task_orchestration.py -v` → 100% pass
- `pytest backend/tests/test_command_router.py::test_concurrent_dispatch -v` → pass

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] Add Task.version column
- [ ] Create alembic migration
- [ ] Update advance_task with SELECT FOR UPDATE SKIP LOCKED
- [ ] Add compare-and-set helper
- [ ] Add AgentRun constraints
- [ ] Add concurrency tests
