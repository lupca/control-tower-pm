---
agent_id: "@claude-opus"
type: ai
model: claude-opus-4-5-20251101
total_tasks_executed: 3
total_tasks_reviewed: 9
success_rate: 1.0
avg_review_rounds: 1.0
strengths: [review, research, architecture, complex-analysis, coordination, skill-design]
weaknesses: []
recent_trend: stable
last_active: 2026-07-24
---

# Agent Profile: @claude-opus

> Independent reviewer model for high-risk and architecture reviews. Top Claude tier — reserved for the 2-3 most important reviews/research/architecture calls, not routine execution.

## Performance Summary
- **Tasks Executed**: 3 (CT-022, CT-023, + 1 legacy)
- **Tasks Reviewed**: 5 (WEB-001 — 3 review rounds, caught scope mismatch + OMS bug; WMS-001, WMS-002, WMS-003, CT-001 — merged from deprecated [[@claude]] per CT-015 tiering)
- **Success Rate**: 100%
- **Average Review Rounds**: 1.0

## Notes
- WEB-001: Caught critical scope mismatch (OMS coupon vs PMI product-level) on round 1, caught OMS updated_at bug on round 2, approved on round 3. Thorough reviewer.
- 2026-07-22 (CT-015): Consolidated `@claude`'s review history (4 tasks: WMS-001, WMS-002, WMS-003, CT-001) into this profile — `@claude-opus` is now the single reviewer-tier profile for Claude models. `@claude` is deprecated, see [[@claude]].
- 2026-07-23 (CT-022): Reviewer Rotation — inline skill edit, passed 1st review. (merged from @claude-opus-4.5)
- 2026-07-24 (CT-023): OCR review toolchain — edited 3 skill files + created convention guide, passed 1st review by @antigravity.
