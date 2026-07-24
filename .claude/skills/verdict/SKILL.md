---
name: verdict
description: Record a reviewer's verdict through the mode-controlled Verdict Gate — pass closes the task, changes reopens with findings. Enforces four-eyes before mode is considered. Only Markdown, never code/tests. Activate on /verdict.
argument-hint: "<task path/ID> <pass|changes> --reviewer @id [--commit <hash>] [--notes ...] [--dry-run]"
allowed-tools: Read, Edit, Write, Glob, Bash(python3 scripts/ct-verdict-apply.py*)
---

## Verdict — record review outcome, enforce four-eyes

Never checks AC, runs tests, or reads diffs — only records the outcome an outside reviewer already determined.

**Coordinator style:** 1–2 terse sentences, no long explanations.

### Step 1 — Parse & locate
1. Read `AGENTS.md` §1, §3, §4 if not already read this session.
2. Glob `projects/*/tasks/<ID>-*.md` to find the task.
3. Parse: verdict (`pass`/`changes`), `--reviewer @id` (required), `--commit <hash>` (required if pass), `--notes "..."` (required if changes), `--dry-run` (optional).
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

Steps 4a/4b below hand every mechanical mutation to `scripts/ct-verdict-apply.py`
(see `[[ADR-008-verdict-apply-script]]`). It re-checks four-eyes and `status:
in-review` itself before writing anything (defense in depth — refuses and
touches no files if either fails), so what's left for you here is exactly the
parts that need judgment: collecting `--commit`/`--notes`/causal-analysis
inputs from the User, then reading the JSON it prints to fill in `log.md` and
the summary. Never invent a `--commit` hash or causal-analysis content
yourself.

*Khuyến nghị:* Nên thêm cờ `--dry-run` để chạy thử 1 lần trước lần `pass` thật đầu tiên trên task thật để kiểm tra kết quả dự kiến mà không ghi bất kỳ file nào.

### Step 4a — `pass`
1. Require real `--commit <hash>` (never invent). Ask if missing.
2. **Causal analysis** — `risk: high`: required (prompt for `root_cause`,
   `mechanism`, `counterfactual`, `pattern_id`; refuse to close without all
   four). `risk: normal`: prompt once, skip if declined.
3. Run:
   ```
   python3 scripts/ct-verdict-apply.py <ID> pass --reviewer @<id> --commit <hash> \
     [--causal-root-cause "..." --causal-mechanism "..." --causal-counterfactual "..." --causal-pattern-id <id>] [--dry-run]
   ```
4. If it prints `"ok": false` → stop, tell the User the exact `error` (don't retry with different args on your own guess).
5. If `causal_analysis_added` is true and `pattern_bump` says the pattern wasn't found (no match) → propose a **new** pattern file to the User (COLLABORATIVE, never create unilaterally) instead of silently dropping the pattern reference.
6. If `depends_on` is non-empty → tell User which tasks may be unblocked.
7. Write 1 entry to `log.md` (format: `AGENTS-REFERENCE.md` §7), using the JSON's `checkboxes_ticked`/`prediction_accuracy.stats`/`agent_stats` to fill in what changed. In `bypass`, include `auto-approved: verdict`.
8. Summary to User: task closed, reviewer, commit, `prediction_accuracy.stats` (overall accuracy).

### Step 4b — `changes`
1. Require `--notes` (reject empty). Split multiple findings with `;` — each becomes its own `- [ ]` item.
2. Run:
   ```
   python3 scripts/ct-verdict-apply.py <ID> changes --reviewer @<id> --notes "finding one; finding two"
   ```
3. If it prints `"ok": false` → stop, tell the User the exact `error`.
4. Write 1 entry to `log.md` using the JSON's `findings_added`/`rejections`/`agent_stats`. In `bypass`, include `auto-approved: verdict`.
5. **If `reviewer_rotation_alert` is true** (`rejections >= 2`): Alert User — "Task đã bị reject 2+ lần. Cần đổi Reviewer hoặc nâng cấp Executor ở lần review sau."
6. Tell User: task reopened; executor fixes → `/review-order` again.

If `scripts/ct-verdict-apply.py` errors or is missing, fall back to the manual
process (edit both files, tick checkboxes, update `prediction-accuracy.md`,
call `update-agent-stats.sh` directly) rather than blocking `/verdict`
entirely.

### Mistakes to avoid
- `pass` when reviewer == executor — always refuse.
- Inventing a commit hash.
- Running tests/reading diffs — trust the reviewer.
- Closing when `status:` ≠ `in-review`.
- `pass` on `risk: high` without all four causal-analysis fields.
- Creating `knowledge/patterns/*.md` without User confirmation.
