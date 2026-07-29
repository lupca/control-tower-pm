---
id: CTV2-206
title: "Consolidate state projections into atomic updates"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: high
risk: normal
deadline: null
executor: "@gpt-5.6-luna"
reviewer: "@claude-sonnet-medium"
result_ref: "9854411..bd9c407"
depends_on: []
files:
  - backend/app/db/models.py
  - backend/app/services/task_orchestration.py
  - backend/app/api/tasks.py
flows: []
tests:
  - backend/tests/test_task_orchestration.py
dispatched: 2026-07-29
in_review: null
predicted_success: high
prediction_factors:
  score: 0.7
  deductions:
    - "refactor: data integrity focus (-0.2)"
    - "documentation: requires field mapping (-0.1)"
confidence_interval: [0.6, 0.8]
created: 2026-07-29
updated: 2026-07-29
---

# CTV2-206: Consolidate state projections into atomic updates

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Context

Task has status, current_gate, awaiting_approval that can contradict each other. Frontend shouldn't infer state from 5 different fields.

## Tiêu chí nghiệm thu (AC)

- [ ] Document which fields are source-of-truth vs projection in models.py docstring
- [ ] Update all GateRecord writes to atomically update Task projection fields in same transaction
- [ ] Add workflow_state computed property or API field: waiting_human | executing | reviewing | blocked | terminal
- [ ] Verify no code path updates projection fields outside GateRecord writes
- [ ] Add DB trigger or application check to prevent inconsistent state combinations

## Verification

- `pytest backend/tests/test_task_orchestration.py -v` → 100% pass
- `grep -r "task.status =" backend/app/` shows only task_orchestration.py

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] Add docstring documenting truth vs projection
- [ ] Audit all Task field updates
- [ ] Add workflow_state property
- [ ] Add consistency check
- [ ] Add tests
