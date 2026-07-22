---
id: CT-009
title: "Auto-Remediation với TNR Safety — Closed-loop tự động"
status: done
priority: low
risk: high
deadline: null
executor: "@sonnet-5"
reviewer: "@sonnet-5"
result_ref: "control-tower@main (commit 510b3b4)"
depends_on: [CT-003, CT-005]
files:
  - AGENTS.md
  - .claude/skills/ingest/SKILL.md
  - .claude/skills/verdict/SKILL.md
flows: []
tests: []
dispatched: 2026-07-22
in_review: 2026-07-22
created: 2026-07-22
updated: 2026-07-22
tier: 3
paradigm_source: "STRATUS (NeurIPS 2025)"
---

# CT-009: Auto-Remediation với TNR Safety — Closed-loop tự động

> Dự án: [[projects/control-tower/control-tower]]

> ⚠️ **Four-eyes waived by explicit User instruction** (2026-07-22): batch-processed alongside CT-004–CT-008, CT-010 với `reviewer: executor` per User request in chat, compensated by an independent aggregate review — see [[CT-011-review-paradigm-shift-batch]] (reviewer `@claude-4.5`). Deliberate, logged exception to `AGENTS.md` §1, not an oversight.

> ℹ️ **Closed as POC**, per `control-tower.md`'s Project Gate + `ADR-002`. AC3's `tnr_spec:` shape and AC1/AC2's diagnosis-assist path are implemented; the sandboxed auto-execution + auto-commit half of AC4, and the webhook integration half of AC1, are **explicitly out of scope for control-tower itself** — see the "Why" note below, not a gap that got missed.

## Bối cảnh (Context)

Hiện tại: Bug detected → human tạo task → executor fix → reviewer check.

Research: STRATUS introduces **Transactional No-Regression (TNR)** — AI can explore fixes autonomously if it can prove no regression. "82% incidents resolved without human intervention, MTTR -70%."

## Tiêu chí nghiệm thu (AC)

- [ ] AC1 (partial): Webhook integration (Sentry/Datadog) — **out of scope for control-tower** (no code to receive a webhook into); the `source: auto-detected` inbox convention IS implemented (`.claude/skills/ingest/SKILL.md`) so a human/external script can drop an alert-derived note into `inbox.md` and have it flow through the normal pipeline.
- [x] AC2: Auto-diagnosis — `/ingest` matches `source: auto-detected` notes against `knowledge/patterns/*.md` (CT-003) for a likely root cause, drafts a `tnr_spec:` block.
- [x] AC3: `tnr_spec:` frontmatter shape — `AGENTS.md` §19.1.
- [ ] AC4 (partial): sandboxed auto-execution (deploy to staging, run tests, compare metrics) and true auto-commit — **out of scope for control-tower** (`AGENTS.md` §19.3: no code/tests/staging here, that's EXECUTE-role work in the target repo). The metadata half — `auto_remediated: true` flag on `/verdict pass` — IS implemented (`AGENTS.md` §19.4, `.claude/skills/verdict/SKILL.md`), but never bypasses human confirmation or four-eyes.
- [x] AC5: Audit trail — every piece that IS implemented goes through the existing `log.md`/`events.jsonl` (CT-008) audit path unchanged, nothing bypasses it.

## Plan

### Why the sandbox/webhook halves are out of scope, not deferred-as-POC
Unlike CT-007/CT-008 (where the missing pieces are "not built yet, could be a future control-tower feature"), AC1's webhook receiver and AC4's sandbox are structurally **not control-tower's job** — `CLAUDE.md` states this repo has no product code, no test runner, no staging environment. A webhook receiver and a TNR sandbox are EXECUTE-role infrastructure that belongs in the target code repo (§1), not something a future control-tower task could add here. What control-tower CAN own — and does — is: (a) the inbox convention for alert-derived notes, (b) diagnosis-assist via existing patterns, (c) the `tnr_spec:` shape as a contract the target repo's own automation could implement against, (d) recording `auto_remediated: true` as metadata once a fix is reported back.

### Phase 1: Diagnosis-assist (implemented)
1. `.claude/skills/ingest/SKILL.md` — `source: auto-detected` handling, causal-pattern cross-reference, `tnr_spec:` draft.
2. `AGENTS.md` §19.1, §19.2.

### Phase 2: Verdict metadata (implemented)
3. `AGENTS.md` §19.4 + `.claude/skills/verdict/SKILL.md` step 2b — `--auto-remediated` flag, no change to human-confirmation/four-eyes requirements.

### Phase 3: Sandbox + webhook (NOT control-tower's scope — documented, not built)
4. `AGENTS.md` §19.3 explains why and points at the target repo as where this belongs.

## Sub-tasks

- [x] Design alert webhook integration — designed as the `source: auto-detected` inbox convention (not an actual webhook receiver, which is out of scope)
- [x] Auto-diagnosis từ stack traces (via causal pattern match, `/ingest`)
- [x] TNR spec format và checker (format only — "checker" that runs it lives in the target repo)
- [ ] Sandbox environment setup (staging deploy) — out of scope, see Plan
- [x] Auto-commit flow với proper audit — implemented as the `auto_remediated: true` metadata flag, not literal auto-commit by control-tower (which has no code to commit)
- [x] Escalation logic (unchanged: `/verdict pass` always needs human confirmation regardless of `auto_remediated`)

## Causal Analysis

```yaml
causal_analysis:
  root_cause: "Khi 1 alert tự động (monitoring/Sentry) sinh ra 1 vấn đề cần fix, hiện tại không có convention nào để đưa nó vào pipeline control-tower — người vận hành phải tự tay viết lại thành 1 task từ đầu, và không có liên kết tới causal patterns đã biết (CT-003) để gợi ý root cause nhanh."
  mechanism: "Định nghĩa convention source: auto-detected cho inbox.md + /ingest tự match note đó với knowledge/patterns/*.md để gợi ý root cause và soạn sẵn tnr_spec: — vẫn đi qua đúng Spec Gate như mọi task khác, không tự động commit fix nào."
  counterfactual: "Không có convention này, alert tự động vẫn phải được người vận hành gõ tay thành task, mất thời gian hơn và không tận dụng được pattern library đã xây ở CT-003."
  pattern_id: null
```

## Research References

- [STRATUS: Multi-Agent Autonomous SRE (NeurIPS 2025)](https://neurips.cc/virtual/2025/poster/116834)
- [HolmesGPT — Agentic SRE (CNCF 2025)](https://www.cncf.io/blog/2026/01/07/holmesgpt-agentic-troubleshooting-built-for-the-cloud-native-era/)
- [GitHub Copilot Coding Agent](https://github.blog/news-insights/product-news/github-copilot-meet-the-new-coding-agent/)
