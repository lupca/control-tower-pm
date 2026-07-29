---
id: CTV2-208
title: "Structured BrakeDecision with observations"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: medium
risk: normal
deadline: null
executor: "@gpt-5.6-luna"
reviewer: "@claude-sonnet-medium"
result_ref: "ba2a44b..cd2ad3a"
depends_on: [CTV2-203]
files:
  - backend/app/services/task_orchestration.py
flows: []
tests:
  - backend/tests/test_task_orchestration.py
dispatched: 2026-07-29
in_review: null
predicted_success: high
prediction_factors:
  score: 0.7
  deductions:
    - "depends_on: CTV2-203 (-0.2)"
    - "observability: logging focus (-0.1)"
confidence_interval: [0.6, 0.8]
created: 2026-07-29
updated: 2026-07-29
---

# CTV2-208: Structured BrakeDecision with observations

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Context

check_brakes returns simple allow/queue/stop. Need structured response with retry hints and full context for debugging.

## Tiêu chí nghiệm thu (AC)

- [ ] Extend BrakeDecision dataclass: add retry_after_seconds, observations dict
- [ ] Add brake check order: terminal? → pending gate? → dependencies? → autonomy? → budget? → agent capability? → account health? → concurrency?
- [ ] Return detailed observations: {active_runs, max_concurrent, task_cost, cost_limit, ...}
- [ ] Add max_active_seconds_per_run, max_tool_calls_per_run, max_no_progress_seconds settings
- [ ] Log full BrakeDecision to AuditLog for debugging

## Verification

- `pytest backend/tests/test_task_orchestration.py -v` → 100% pass

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] Extend BrakeDecision dataclass
- [ ] Refactor check_brakes with ordered checks
- [ ] Add new settings
- [ ] Add audit logging
- [ ] Add tests
