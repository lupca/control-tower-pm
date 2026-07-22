---
id: CT-006
title: "Confidence Calibration — Know WHEN to escalate"
status: done
priority: medium
risk: normal
deadline: null
executor: "@sonnet-5"
reviewer: "@sonnet-5"
result_ref: "control-tower@main (commit 510b3b4)"
depends_on: [CT-001]
files:
  - .claude/skills/pm/SKILL.md
  - .claude/skills/pm/references/task-creation.md
  - .claude/skills/pm/references/task-execution.md
  - .claude/skills/verdict/SKILL.md
  - .claude/skills/lint/SKILL.md
  - knowledge/metrics/prediction-accuracy.md
  - AGENTS.md
flows: [pm-create, plan, dispatch]
tests: []
dispatched: 2026-07-22
in_review: 2026-07-22
created: 2026-07-22
updated: 2026-07-22
tier: 2
paradigm_source: "MIT Conformal Prediction for NLP (2025)"
---

# CT-006: Confidence Calibration — Know WHEN to escalate

> Dự án: [[projects/control-tower/control-tower]]

> ⚠️ **Four-eyes waived by explicit User instruction** (2026-07-22): batch-processed alongside CT-004, CT-005, CT-007–CT-010 with `reviewer: executor` per User request in chat, compensated by an independent aggregate review — see [[CT-011-review-paradigm-shift-batch]] (reviewer `@claude-4.5`). Deliberate, logged exception to `AGENTS.md` §1, not an oversight.

## Bối cảnh (Context)

Hiện tại: Fixed gates — Spec Gate ALWAYS, Plan Gate ALWAYS, Verdict ALWAYS needs human.

Research: Conformal prediction provides "distribution-free uncertainty quantification — know WHEN to defer to humans" với formal guarantees.

## Tiêu chí nghiệm thu (AC)

- [x] AC1: Thêm `confidence_interval: [lower, upper]` vào task metadata (`AGENTS.md` §16.1).
- [x] AC2: Confidence được tính từ `predicted_success` score (CT-001), verifier results (CT-005), historical accuracy (`knowledge/metrics/prediction-accuracy.md`).
- [x] AC3: Dynamic gate rules — **implemented with 1 deliberate deviation, see note below.**
- [x] AC4: Human can always override to require gates ("I want to review all tasks this week") — `AGENTS.md` §16.3.
- [x] AC5: Calibration tracking: `prediction-accuracy.md` gained `Confidence Interval`/`In Interval?` columns, populated by `/verdict`.
- [x] AC6: `/lint` warning nếu calibration drift quá lớn — checklist item 13.

## Plan

### Phase 1: Schema
1. `AGENTS.md` §16.1 — `confidence_interval:` field + computation inputs.

### Phase 2: Dynamic gates — **deviation from AC3's literal wording**
2. AC3's original wording said "narrow AND lower > 0.85 → Auto-proceed (log only, no human gate)". This directly conflicts with `AGENTS.md` §4's mandatory rule that Spec Gate and Plan Gate ALWAYS stop for User confirmation — a rule CT-006 doesn't have authority to override (that would be a separate, much larger decision needing its own explicit sign-off, not something to slip in as a side effect of a scoring feature). **Implemented instead:** confidence changes gate FRICTION (how much scrutiny is asked for — a bare "ok" is acceptable when narrow+high, itemized confirmation required when wide/low) but the gate itself never disappears. Documented explicitly in `AGENTS.md` §16.2 so this isn't mistaken for the literal AC3 behavior later.
3. `.claude/skills/pm/references/task-creation.md` step 11, `task-execution.md` Plan Gate step 5 — apply the friction rule at both gates.

### Phase 3: Tracking + drift
4. `knowledge/metrics/prediction-accuracy.md` — new columns.
5. `.claude/skills/verdict/SKILL.md` step 9 — record in-interval outcome.
6. `.claude/skills/lint/SKILL.md` item 13 — drift check (< 70% in-interval over last 5+ calibrated tasks).

## Sub-tasks

- [x] Research conformal prediction implementation (applied as a lightweight heuristic interval, not a full conformal-prediction implementation — no ML training loop exists in this Markdown-only system)
- [x] Define confidence computation formula
- [x] Implement dynamic gate logic (friction, not presence — see deviation note above)
- [x] User preference override ("always ask me")
- [x] Calibration drift detection

## Research References

- [MIT Conformal Prediction for NLP (2025)](https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00715/125278/Conformal-Prediction-for-Natural-Language)
- [Human-AI Joint Cognitive Systems Framework (ACM 2024)](https://interactions.acm.org/archive/view/january-february-2024/applying-hcai-in-developing-effective-human-ai-teaming)
