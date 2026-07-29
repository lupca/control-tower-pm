---
id: CTV2-202
title: "Add DispatchDecision + DispatchCandidate tables"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: urgent
risk: high
deadline: null
executor: "@claude-sonnet-high"
reviewer: "@gemini-3.1-pro-high"
result_ref: "4b14baf..28f33f5"
depends_on: [CTV2-201]
files:
  - backend/app/db/models.py
  - backend/app/services/task_orchestration.py
  - backend/app/services/agent_matcher.py
flows: []
tests:
  - backend/tests/test_task_orchestration.py
dispatched: 2026-07-29
in_review: null
predicted_success: medium
prediction_factors:
  score: 0.5
  deductions:
    - "blast_radius: high (-0.3)"
    - "depends_on: CTV2-201 (-0.2)"
confidence_interval: [0.4, 0.6]
created: 2026-07-29
updated: 2026-07-29
---

# CTV2-202: Add DispatchDecision + DispatchCandidate tables

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Context

AgentMatcher scores agents but doesn't persist decisions. Need this data to understand why agents were selected/rejected and to train dispatch models.

## Tiêu chí nghiệm thu (AC)

- [ ] Create DispatchDecision model: id, task_id, task_round_id, kind (execute|review), policy_version, task_feature_snapshot (JSON), selected_agent_id, selected_score, selection_reason, exploration (bool), human_override, created_at
- [ ] Create DispatchCandidate model: dispatch_decision_id, agent_id, eligible, rejection_reason, predicted_pass1, predicted_runtime, quota_pressure, final_score
- [ ] Modify AgentMatcher.suggest_agents to return structured ScoringResult with all candidate scores
- [ ] Persist DispatchDecision in request_dispatch before creating AgentRun
- [ ] Link AgentRun.dispatch_decision_id
- [ ] Tests verify DispatchDecision and candidates are persisted on dispatch

## Verification

- `pytest backend/tests/test_task_orchestration.py -v` → 100% pass
- `alembic upgrade head` → no errors

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] Create DispatchDecision SQLAlchemy model
- [ ] Create DispatchCandidate SQLAlchemy model
- [ ] Create alembic migration
- [ ] Update AgentMatcher to return ScoringResult
- [ ] Update request_dispatch to persist DispatchDecision
- [ ] Add AgentRun.dispatch_decision_id FK
- [ ] Add tests
