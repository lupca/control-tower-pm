---
id: CT-007
title: "Goal-Conditioned Autonomy — Từ task list sang goal pursuit"
status: todo
priority: low
risk: high
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: [CT-001, CT-005, CT-006]
files:
  - AGENTS.md
  - .claude/skills/pm/SKILL.md
flows: []
tests: []
dispatched: null
in_review: null
created: 2026-07-22
updated: 2026-07-22
tier: 3
paradigm_source: "Claude /goal command, Devin"
---

# CT-007: Goal-Conditioned Autonomy — Từ task list sang goal pursuit

> Dự án: [[projects/control-tower/control-tower]]

## Bối cảnh (Context)

Hiện tại: Human defines task list → AI executes từng task một.

Research: Goal-conditioned autonomy định nghĩa **completion conditions** và let AI pursue until met. "OSWorld improved from 14.9% to 72.7% with goal-conditioned autonomy."

**Đây là paradigm shift lớn nhất** — thay đổi fundamental cách define và track work.

## Tiêu chí nghiệm thu (AC)

- [ ] AC1: New entity type: `Goal` (khác với `Task`)
  ```yaml
  # projects/<name>/goals/GOAL-001.md
  ---
  id: GOAL-001
  title: "API response time < 100ms for /products"
  status: pursuing | achieved | abandoned
  completion_conditions:
    - metric: p99_latency
      target: "< 100ms"
      measurement: "production APM"
    - metric: regression
      target: "none in other endpoints"
      measurement: "test suite"
  max_iterations: 5
  current_iteration: 2
  escalate_if: "2 consecutive failed attempts"
  spawned_tasks: [PMI-010, PMI-011]
  ---
  ```
- [ ] AC2: New macro `/goal <description>` để define goal với completion conditions
- [ ] AC3: Goal auto-spawns tasks:
  - Analyze current state vs goal
  - Generate hypothesis
  - Create task to test hypothesis
  - On task completion, measure if goal met
  - If not met, generate new hypothesis → new task
- [ ] AC4: Goal escalates to human khi:
  - Max iterations reached
  - Consecutive failures
  - Confidence drops below threshold
- [ ] AC5: Goals can have sub-goals (hierarchical)

## Plan

*(Điền khi Plan Gate)*

## Sub-tasks

- [ ] Design Goal entity schema
- [ ] Create `/goal` skill
- [ ] Implement hypothesis generation
- [ ] Connect to measurement/metrics systems
- [ ] Hierarchical goal decomposition
- [ ] Integration with existing task system

## Research References

- [Claude /goal command](https://www.anthropic.com/news/measuring-agent-autonomy)
- [Devin / Manus — End-to-end autonomous SE](https://www.cbinsights.com/research/ai-agent-market-map/)
- [Agent2Agent (A2A) Protocol](https://galileo.ai/blog/google-agent2agent-a2a-protocol-guide)
