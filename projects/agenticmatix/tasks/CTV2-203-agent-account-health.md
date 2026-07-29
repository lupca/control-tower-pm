---
id: CTV2-203
title: "Add AgentAccount for subscription health tracking"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: high
risk: normal
deadline: null
executor: "@gpt-5.6-luna"
reviewer: "@claude-sonnet-medium"
result_ref: "28f33f5..f5972bc"
depends_on: [CTV2-202]
files:
  - backend/app/db/models.py
  - backend/app/workers/agent_runner.py
  - backend/app/services/agent_matcher.py
flows: []
tests:
  - backend/tests/unit/test_agent_runner.py
dispatched: 2026-07-29
in_review: null
predicted_success: medium
prediction_factors:
  score: 0.6
  deductions:
    - "depends_on: CTV2-202 (-0.2)"
    - "new_table: moderate complexity (-0.2)"
confidence_interval: [0.5, 0.7]
created: 2026-07-29
updated: 2026-07-29
---

# CTV2-203: Add AgentAccount for subscription health tracking

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Context

CLI subscriptions have rate limits, quotas, and cooldowns that LLMUsage.cost_usd doesn't capture. Need account-level health metrics.

## Tiêu chí nghiệm thu (AC)

- [ ] Create AgentAccount model: id, agent_id, cli, subscription_plan, status, quota_pressure, cooldown_until, last_rate_limit_at, health_score, updated_at
- [ ] Create RunResourceUsage model: agent_run_id, llm_calls, input_tokens, output_tokens, tool_calls, bash_commands, files_read, files_written, active_seconds, rate_limit_events, estimated_cost_usd
- [ ] Update agent_runner to populate RunResourceUsage on run completion
- [ ] Update AgentMatcher to factor in AgentAccount.quota_pressure

## Verification

- `pytest backend/tests/unit/test_agent_runner.py -v` → 100% pass
- `alembic upgrade head` → no errors

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] Create AgentAccount model
- [ ] Create RunResourceUsage model
- [ ] Create alembic migration
- [ ] Update agent_runner completion logic
- [ ] Update AgentMatcher scoring
- [ ] Add tests
