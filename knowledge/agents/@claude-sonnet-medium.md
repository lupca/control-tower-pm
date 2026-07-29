---
agent_id: "@claude-sonnet-medium"
type: ai
model: claude-sonnet-5
effort: medium
total_tasks_executed: 19
total_tasks_reviewed: 2
success_rate: 0.84
avg_review_rounds: 1.0
strengths: [code, backend, frontend, testing]
weaknesses: [edge-case-coverage]
recent_trend: stable
last_active: 2026-07-28
---

# Agent Profile: @claude-sonnet-medium

> Claude Sonnet 5, medium reasoning effort. Default Sonnet executor tier — standard execution tasks.

## Performance Summary
- **Tasks Executed**: 3 (even split of the deprecated [[@sonnet-5]] history — see Notes)
- **Tasks Reviewed**: 2 (self-review, waived by explicit User instruction for that batch only — see [[@sonnet-5]] and `AGENTS.md` §1)
- **Success Rate (1st review pass)**: 100%
- **Average Review Rounds**: 1.0

## Notes
- 2026-07-22 (CT-015): `@sonnet-5`'s pre-tiering history (8 executed / 7 reviewed, CT-003–CT-010) had no per-effort attribution recorded, so it was split evenly across `@claude-sonnet-{low,medium,high}` (3/3/2 executed, 3/2/2 reviewed) rather than reconstructed task-by-task. See [[@sonnet-5]] for the original task list and full context.
- 2026-07-28 (CTV2-110): AgentSelector upgrade — passed but reviewer found it incomplete on first review.
- 2026-07-28 (CTV2-113): Dispatch effort override — passed review but missed edge case: model names with effort suffix (e.g. `gemini-3.6-flash-low`) conflict with `--effort` flag. Required hotfix `133fe16`.
