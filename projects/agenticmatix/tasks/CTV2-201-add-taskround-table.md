---
id: CTV2-201
title: "Add TaskRound table for multi-round history"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: urgent
risk: high
deadline: null
executor: "@gpt-5.6-luna-high"
reviewer: "@gemini-3.1-pro-high"
result_ref: "9ea9243..6559ba0"
depends_on: []
files:
  - backend/app/db/models.py
  - backend/app/services/task_orchestration.py
  - backend/alembic/versions/
flows: []
tests:
  - backend/tests/test_task_orchestration.py
dispatched: 2026-07-29
in_review: 2026-07-29
predicted_success: medium
prediction_factors:
  score: 0.5
  deductions:
    - "blast_radius: 73 files (-0.5)"
    - "hub_bridge_node: Task, TaskOrchestrationService (-0.0, already counted in blast)"
confidence_interval: [0.4, 0.6]
created: 2026-07-29
updated: 2026-07-29
---

# CTV2-201: Add TaskRound table for multi-round history

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Context

Currently Task overwrites executor/reviewer/result_ref on each round, losing history. TaskRound preserves per-round state for analytics and debugging.

## Tiêu chí nghiệm thu (AC)

- [ ] Create TaskRound model with fields: id, task_id, round_no, status, base_sha, plan_ref, executor_agent_id, executor_run_id, reviewer_agent_id, reviewer_run_id, result_ref, verdict, findings_ref, started_at, completed_at
- [ ] Add Task.current_round_id FK and Task.final_result_ref, Task.final_verdict projection fields
- [ ] Migrate TaskOrchestrationService.request_dispatch to create TaskRound on dispatch
- [ ] Migrate TaskOrchestrationService verdict recording to update TaskRound
- [ ] Update advance_task to use TaskRound.round_no for round counting instead of audit log queries
- [ ] Add alembic migration with data migration for existing tasks (create TaskRound records for tasks with existing executor/result_ref)
- [ ] Tests: test_task_orchestration.py updated to verify TaskRound creation/update on dispatch and verdict

## Verification

- `cd /home/lupca/projects/control-tower-v2 && pytest backend/tests/test_task_orchestration.py -v` → 100% pass
- `cd /home/lupca/projects/control-tower-v2 && alembic upgrade head` → no errors
- `cd /home/lupca/projects/control-tower-v2 && alembic downgrade -1 && alembic upgrade head` → migration reversible

## Plan

1. **Create TaskRound model** (`backend/app/db/models.py`):
   - Add `TaskRound` class after `TaskDependency` with fields: id (UUID PK), task_id (FK), round_no (int), status, base_sha, plan_ref, executor_agent_id (FK to Agent), executor_run_id (FK to AgentRun), reviewer_agent_id, reviewer_run_id, result_ref, verdict, findings_ref, started_at, completed_at
   - Add `Task.current_round_id` FK to TaskRound (nullable)
   - Add `Task.final_result_ref`, `Task.final_verdict` projection fields
   - Add `Task.rounds` relationship

2. **Alembic migration** (`backend/alembic/versions/0XX_add_taskround.py`):
   - Create `task_rounds` table
   - Add `current_round_id`, `final_result_ref`, `final_verdict` columns to `tasks`
   - Data migration: for each task with existing `executor`/`result_ref`, create a TaskRound record with round_no=1

3. **Update TaskOrchestrationService** (`backend/app/services/task_orchestration.py`):
   - In `request_dispatch`: create new TaskRound if none exists or increment round_no, link via Task.current_round_id
   - In `_request_gate` with gate_type=dispatch: populate TaskRound.executor_agent_id, executor_run_id, started_at
   - Add method to update TaskRound on verdict: set verdict, findings_ref, reviewer_agent_id, reviewer_run_id, completed_at
   - Update Task.final_result_ref/final_verdict projections when verdict=pass

4. **Update round counting logic**:
   - Replace audit log queries with `SELECT MAX(round_no) FROM task_rounds WHERE task_id = ?`

5. **Tests** (`backend/tests/test_task_orchestration.py`):
   - Test TaskRound created on first dispatch
   - Test round_no increments on subsequent dispatches
   - Test TaskRound updated on verdict
   - Test data migration creates records for existing tasks

## Sub-tasks

- [ ] Create TaskRound SQLAlchemy model in models.py
- [ ] Add Task.current_round_id FK + projection fields
- [ ] Create alembic migration with data migration script
- [ ] Update TaskOrchestrationService.request_dispatch
- [ ] Update TaskOrchestrationService verdict methods
- [ ] Update advance_task round counting logic
- [ ] Update/add tests
