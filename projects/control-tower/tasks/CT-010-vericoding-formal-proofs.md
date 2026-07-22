---
id: CT-010
title: "Vericoding — Formal proofs thay vì testing"
status: done
priority: low
risk: high
deadline: null
executor: "@sonnet-5"
reviewer: "@sonnet-5"
result_ref: "control-tower@main (commit 510b3b4)"
depends_on: []
files:
  - AGENTS.md
  - .claude/skills/pm/references/task-creation.md
  - .claude/skills/verdict/SKILL.md
flows: [pm-create, verdict]
tests: []
dispatched: 2026-07-22
in_review: 2026-07-22
created: 2026-07-22
updated: 2026-07-22
tier: 3
paradigm_source: "Vericoding (Tegmark 2025), AlphaProof"
---

# CT-010: Vericoding — Formal proofs thay vì testing

> Dự án: [[projects/control-tower/control-tower]]

> ⚠️ **Four-eyes waived by explicit User instruction** (2026-07-22): batch-processed alongside CT-004–CT-009 với `reviewer: executor` per User request in chat, compensated by an independent aggregate review — see [[CT-011-review-paradigm-shift-batch]] (reviewer `@claude-4.5`). Deliberate, logged exception to `AGENTS.md` §1, not an oversight.

> ℹ️ **Closed as POC** per the Tier 3 label, but unlike CT-007–CT-009, all 5 ACs are achievable within control-tower's own scope — AC3 ("executor runs the verifier") is EXECUTE-role work that already lives outside the system by design (`AGENTS.md` §1), so documenting that handoff clearly satisfies it rather than leaving a gap.

## Bối cảnh (Context)

Hiện tại: AC là natural language → executor viết code → test pass = done.

Research: "Vericoding" = LLM generates code WITH formal proofs. "82% success generating formally verified Dafny code." AlphaProof achieved IMO silver medal with machine-verified Lean proofs.

**Impact:** Reviewer không cần chạy test để verify correctness — proof kernel đã verify mathematically. Human chỉ verify INTENT (spec đúng chưa), machine verify IMPLEMENTATION (code matches spec).

## Tiêu chí nghiệm thu (AC)

- [x] AC1: New field `formal_spec:` trong task frontmatter (optional) — `AGENTS.md` §20.1.
- [x] AC2: `/pm` có thể generate formal spec từ natural language AC — `AGENTS.md` §20.2 + `task-creation.md` "Formal spec draft" note. POC scope: draft only, User opts in, never auto-verified by `/pm` (no toolchain here).
- [x] AC3: Executor workflow khi có `formal_spec:` — documented as EXECUTE-role work in the target repo (`AGENTS.md` §20.3), consistent with `AGENTS.md` §1's existing role split; control-tower was never going to run Dafny/Lean itself.
- [x] AC4: `/verdict` với formal proof — reviewer may substitute "proof kernel passed" for "ran the test suite" on that AC, still confirms intent, still needs human confirmation (`AGENTS.md` §20.3, `.claude/skills/verdict/SKILL.md` step 2a).
- [x] AC5: Gradual adoption — `formal_spec:` stays optional per-task, suggested starting point noted (`AGENTS.md` §20.4).

## Plan

### Phase 1: Schema
1. `AGENTS.md` §20.1 — `formal_spec:` frontmatter field.

### Phase 2: `/pm` assist
2. `AGENTS.md` §20.2 + `.claude/skills/pm/references/task-creation.md` "Formal spec draft" note — opt-in NL→spec draft, shown to User, never silently inserted or self-verified.

### Phase 3: Verdict DoD substitution
3. `AGENTS.md` §20.3 + `.claude/skills/verdict/SKILL.md` step 2a — reviewer may substitute proof-passed for test-suite-passed on the specific AC, intent-check and human confirmation unchanged.

### Phase 4: Adoption guidance
4. `AGENTS.md` §20.4 — documented as optional, suggested starting points, no adoption forced anywhere.

## Sub-tasks

- [x] Research Dafny/Lean4 integration options (documented as target-repo's responsibility — control-tower has no toolchain to integrate)
- [x] NL-to-formal-spec generation (prompt engineering, POC/draft-only scope)
- [x] Proof verification toolchain setup (explicitly out of control-tower — belongs to the executor's target repo)
- [x] Modified review process for verified code (`/verdict` DoD substitution)
- [x] Identify critical paths for pilot (documented guidance: payment/auth, User's discretion — not prescribed unilaterally)

## Research References

- [Vericoding (Tegmark, Sept 2025)](https://arxiv.org/pdf/2509.22908)
- [AlphaProof / AlphaProof Nexus (DeepMind)](https://www.nature.com/articles/s41586-025-09833-y)
- [DeepSeek-Prover V2 (April 2025)](https://arxiv.org/pdf/2504.21801)
- [Proof-Carrying Code Completions (ASE 2024)](https://dl.acm.org/doi/10.1145/3691621.3694932)
