---
id: CTV2-209
title: "Normalize CLI adapter events"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: medium
risk: normal
deadline: null
executor: "@gpt-5.6-luna"
reviewer: "@claude-sonnet-medium"
result_ref: "5047ebd..ba2a44b"
depends_on: []
files:
  - backend/app/db/models.py
  - backend/app/workers/agent_runner.py
flows: []
tests:
  - backend/tests/unit/test_agent_runner.py
dispatched: 2026-07-29
in_review: null
predicted_success: high
prediction_factors:
  score: 0.7
  deductions:
    - "parsing: CLI output varies (-0.2)"
    - "new_table: AgentEvent (-0.1)"
confidence_interval: [0.6, 0.8]
created: 2026-07-29
updated: 2026-07-29
---

# CTV2-209: Normalize CLI adapter events

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Context

Different CLIs (claude/agy/codex) emit different event formats. Need normalized schema for dashboard and dispatch model training.

## Tiêu chí nghiệm thu (AC)

- [ ] Create AgentEvent model: run_id, seq, event_type, timestamp, payload (JSON)
- [ ] Define event types: run.started, llm.requested, llm.completed, tool.started, tool.completed, gate.requested, workspace.changed, run.heartbeat, run.completed
- [ ] Create CLI adapter layer that parses vendor stdout and emits normalized events
- [ ] Keep VendorRawEvent table for debugging original output
- [ ] Dashboard and dispatch model use only normalized events

## Verification

- `pytest backend/tests/unit/test_agent_runner.py -v` → 100% pass

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] Create AgentEvent model
- [ ] Create VendorRawEvent model
- [ ] Create alembic migration
- [ ] Create CLI adapter parsers (claude, agy, codex)
- [ ] Update agent_runner to use adapters
- [ ] Add tests
