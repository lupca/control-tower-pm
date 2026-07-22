---
agent_id: "@claude-sonnet-high"
type: ai
model: claude-sonnet-5
effort: high
total_tasks_executed: 2
total_tasks_reviewed: 2
success_rate: 1.0
avg_review_rounds: 1.0
strengths: [code, backend, frontend, testing]
weaknesses: []
recent_trend: stable
last_active: 2026-07-22
---

# Agent Profile: @claude-sonnet-high

> Claude Sonnet 5, high reasoning effort. Highest-effort Sonnet executor tier — harder execution tasks that don't warrant escalating to `@claude-opus`.

## Performance Summary
- **Tasks Executed**: 2 (even split of the deprecated [[@sonnet-5]] history — see Notes)
- **Tasks Reviewed**: 2 (self-review, waived by explicit User instruction for that batch only — see [[@sonnet-5]] and `AGENTS.md` §1)
- **Success Rate (1st review pass)**: 100%
- **Average Review Rounds**: 1.0

## Notes
- 2026-07-22 (CT-015): `@sonnet-5`'s pre-tiering history (8 executed / 7 reviewed, CT-003–CT-010) had no per-effort attribution recorded, so it was split evenly across `@claude-sonnet-{low,medium,high}` (3/3/2 executed, 3/2/2 reviewed) rather than reconstructed task-by-task. See [[@sonnet-5]] for the original task list and full context.
