---
name: verdict
description: Record a reviewer's verdict through the mode-controlled Verdict Gate — pass closes the task, changes reopens with findings. Enforces four-eyes before mode is considered. Only Markdown, never code/tests. Activate on /verdict.
argument-hint: "<task path/ID> <pass|changes> --reviewer @id [--commit <hash>] [--notes ...]"
allowed-tools: Read, Edit, Write, Glob, Bash
---

## Verdict — record review outcome, enforce four-eyes

Never checks AC, runs tests, or reads diffs — only records the outcome an outside reviewer already determined.

**Coordinator style:** 1–2 terse sentences, no long explanations.

### Step 1 — Parse & locate
1. Read `AGENTS.md` §1, §3, §4 if not already read this session.
2. Glob `projects/*/tasks/<ID>-*.md` to find the task.
3. Parse: verdict (`pass`/`changes`), `--reviewer @id` (required), `--commit <hash>` (required if pass), `--notes "..."` (required if changes).
4. Check `status:` is `in-review`. If not → stop, tell User.

### Step 2 — Four-eyes (MANDATORY)
Compare `--reviewer` vs `executor:` in frontmatter. If same → **REFUSE
immediately without prompting for an override**, regardless of mode. If
different → continue.

### Step 3 — Verdict Gate

Read `state/mode.md` fresh; a missing/invalid value means `supervised`.

- `plan-only`: block without changing the task, review sheet, metrics, or stats.
- `supervised`: show the parsed verdict/reviewer/commit or notes, then stop for
  explicit User confirmation.
- `bypass`: continue immediately and include `auto-approved: verdict` in the
  verdict audit entry.

The hard four-eyes check above always runs before this Gate. The Gate decides
only stop/continue: once permitted, every branch-specific side effect below
(review sheet, task state, AC ticks/findings, audit, prediction outcome, and both
agent-stat updates) must run exactly once.

### Step 4a — `pass`
1. Update `projects/<name>/reviews/<ID>-review.md`: `reviewer`, `status: passed`, `verdict: pass`, `verdict_date: <today>`.
2. Require real `--commit <hash>` (never invent). Ask if missing.
3. The Verdict Gate supplies confirmation in `supervised`; an explicitly
   selected `bypass` mode supplies pre-authorization. Neither can override
   four-eyes or required commit/causal-analysis inputs.
4. **Causal analysis** — `risk: high`: required (prompt for `root_cause`, `mechanism`, `counterfactual`, `pattern_id`; refuse to close without all four). `risk: normal`: prompt once, skip if declined. If provided, append `## Causal Analysis` to task body. If `pattern_id` matches `knowledge/patterns/<id>.md` → update `Past Instances` + `_index.md`. No match → propose new pattern (COLLABORATIVE, never create unilaterally).
5. Tick all AC and sub-tasks as `- [x]`.
6. Update frontmatter: `status: done`, `reviewer:`, `result_ref:`, `updated: <today>`.
7. If `depends_on:` → tell User which tasks may be unblocked.
8. Write 1 entry to `log.md` (format: `AGENTS-REFERENCE.md` §7). In `bypass`,
   include `auto-approved: verdict`.
9. Record prediction outcome in `knowledge/metrics/prediction-accuracy.md`.
10. **Update agent stats** — MUST run: `./scripts/update-agent-stats.sh <executor> executor pass` and `./scripts/update-agent-stats.sh <reviewer> reviewer pass`.
11. Summary to User: task closed, reviewer, commit, prediction accuracy.

### Step 4b — `changes`
1. Update `projects/<name>/reviews/<ID>-review.md`: `reviewer`, `status: changes-requested`, `verdict: changes`, `verdict_date: <today>`.
2. Require `--notes` (reject empty).
3. Add `## Findings từ reviewer` section — each point as `- [ ]`.
4. **Increment rejection counter**: Read `rejections:` from frontmatter (default 0), increment by 1, write back.
5. Update frontmatter: `status: changes-requested`, `rejections: <N>`, `updated: <today>`.
6. Write 1 entry to `log.md`. In `bypass`, include
   `auto-approved: verdict`.
7. Record prediction outcome in `knowledge/metrics/prediction-accuracy.md`.
8. **Update agent stats** — MUST run: `./scripts/update-agent-stats.sh <executor> executor changes` and `./scripts/update-agent-stats.sh <reviewer> reviewer changes`.
9. **If `rejections >= 2`**: Alert User — "Task đã bị reject 2+ lần. Cần đổi Reviewer hoặc nâng cấp Executor ở lần review sau."
10. Tell User: task reopened; executor fixes → `/review-order` again.

### Mistakes to avoid
- `pass` when reviewer == executor — always refuse.
- Inventing a commit hash.
- Running tests/reading diffs — trust the reviewer.
- Closing when `status:` ≠ `in-review`.
- `pass` on `risk: high` without all four causal-analysis fields.
- Creating `knowledge/patterns/*.md` without User confirmation.
