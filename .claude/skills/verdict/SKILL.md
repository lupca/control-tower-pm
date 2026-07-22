---
name: verdict
description: Record an independent reviewer's verdict into control-tower — pass closes the task (needs human confirmation), changes reopens it with findings. Checks four-eyes (reviewer must differ from executor). Only updates Markdown, never touches code, never runs tests itself. Activate when the user types /verdict.
argument-hint: "<task path/ID> <pass|changes> --reviewer @id [--commit <hash>] [--notes ...]"
allowed-tools: Read, Edit, Write, Glob
---

## Verdict — record the review outcome, enforce four-eyes

This skill **never checks the AC itself, never runs tests, never reads a diff** — it only records the outcome that an (outside-the-system) reviewer already determined, after checking the four-eyes constraint.

### Coordinator output style

Keep responses to 1–2 terse sentences with no long explanation. Batch adjacent confirmations as `Spec+Plan ok? Dispatch @agent? [y/n]`; after spawning a CLI process, report only pass/fail and the next action, without summarizing its output.

### Step 1 — Locate the task and parse arguments

1. Read `AGENTS.md` §1, §3, §4 if not already read this session (separation of duties, DoD, task lifecycle). For reputation/patterns/causal-analysis features, also read `AGENTS-EXPERIMENTAL.md` §12, §13.
2. Find the task by ID/path in `$ARGUMENTS`: Glob `projects/*/tasks/<ID>-*.md` if the User gave an ID (e.g. `PMI-001`), or by the full path.
3. Parse: verdict (`pass` or `changes`), `--reviewer @id` (required), `--commit <hash>` (required if `pass`), `--notes "..."` (required if `changes`), `--auto-remediated` (optional flag, §3a step 5).
4. Read the frontmatter, check the current `status:`: only accept a verdict for a task that's `status: in-review`. If it's anything else → stop, tell the User (e.g. the task hasn't gone through `/review-order` yet, or is already `done`).

### Step 2 — Check four-eyes (MANDATORY, never skip)

Compare `--reviewer` against the `executor:` recorded in the frontmatter:
- If **they match** (same human/same AI) → **REFUSE to record a `pass` verdict**. Tell the User: this violates separation of duties (`AGENTS.md` §1) — it needs a second reviewer's sign-off, independent of the executor. Never lower the bar to let it through.
- If **they differ** → continue.

### Step 3a — Verdict `pass`

0. **Update review sheet frontmatter**: Find `projects/<name>/reviews/<ID>-review.md`, update:
   - `reviewer: <--reviewer>`
   - `status: passed`
   - `verdict: pass`
   - `verdict_date: <today>`

1. Require a real `--commit <hash>` (the actual commit hash of the change, never invented). If missing, ask the User/reviewer instead of guessing or leaving it blank.
2. **This is still a human decision** (`AGENTS.md` §3, §4: "A PASS verdict is only valid once a human confirms it"). If this `/verdict` command was typed directly by the User in the current session, treat that as confirmation. If you (the agent) are proposing to run `/verdict pass` yourself rather than the User typing it directly, you MUST stop and ask for explicit confirmation before recording it.
2a. **Formal spec DoD substitution** (`AGENTS-EXPERIMENTAL.md` §20.3) — if the task frontmatter has `formal_spec:` and the reviewer reports the proof kernel passed (noted in `result_ref`/`--notes`), the reviewer may substitute "proof kernel passed" for "ran the test suite" on that specific AC in the DoD (§3). The reviewer still must confirm the spec matches the AC's intent — this never skips human confirmation from step 2.
2b. **Auto-remediated flag** (`AGENTS-EXPERIMENTAL.md` §19.4) — if `--auto-remediated` was passed, record `auto_remediated: true` in the frontmatter. This is metadata about how the fix was validated in the target repo; it changes nothing else about this flow — human confirmation (step 2) and four-eyes (Step 2 above) still apply with no exception.
3. **Causal analysis** (`AGENTS-EXPERIMENTAL.md` §13) — prompt the reviewer for `root_cause`, `mechanism`, `counterfactual`, and `pattern_id`:
   - If `risk: high` → **required**. Ask for all four fields and refuse to proceed to step 4 until they're provided — do not record `pass` without them.
   - If `risk: normal` → optional. Prompt once; if the reviewer declines or doesn't answer, skip this step entirely (no `## Causal Analysis` section gets added).
   - If provided, append a `## Causal Analysis` section to the task body with the yaml block (format in `AGENTS.md` §2.1b).
   - If `pattern_id` is set: Glob `knowledge/patterns/<pattern_id>.md`.
     - **Match found** → append `- [[<task ID>]] — <1-line summary from root_cause>` to that file's `## Past Instances` section, bump `updated:` in its frontmatter, and increment its row's instance count in `knowledge/patterns/_index.md`.
     - **No match** → this is COLLABORATIVE (`AGENTS.md` §1, `AGENTS-PLAYBOOK.md` §11.6: never invent knowledge content unilaterally) — propose the new pattern file (schema in `AGENTS-EXPERIMENTAL.md` §13.1) to the User and stop for confirmation before writing it. If the User declines, still record `pattern_id` in the task's `causal_analysis` block, just skip creating the pattern file.
4. **Cross-repo pattern learning** (`AGENTS-EXPERIMENTAL.md` §14.4) — if the task's project has `patterns_exportable: true` (`index.md` §2), check informationally whether the fix looks generic enough to apply to another `patterns_exportable` project; if so, suggest to the User "this may apply to `<other project>` too" — never auto-files a task for it.
5. Mark every related AC and sub-task in the body as `- [x]`.
6. Update the frontmatter: `status: done`, `reviewer: "<--reviewer>"`, `result_ref:` (keep as-is or update to the real commit), `updated: <today>`.
7. If the task declares `depends_on:` (see `AGENTS.md` §2.2): tell the User which tasks might now be unblocked, since there's no automatic parsing/unblocking mechanism yet — don't infer it yourself.
8. Write 1 entry to `log.md` (`operation: verdict`, format in `AGENTS-REFERENCE.md` §7), with the `Commit:` field = the real hash just received.
9. Record prediction outcome into `knowledge/metrics/prediction-accuracy.md`: read `predicted_success` from the task's frontmatter, log entry with outcome `pass` (Success), update accuracy metrics. If the task has `confidence_interval:` (`AGENTS-EXPERIMENTAL.md` §16.4), also record whether the actual outcome fell inside the interval, in a `confidence_interval` column alongside the existing ones.
10. **Update Agent Reputation Profiles via script** (zero token overhead):
    ```bash
    ./scripts/update-agent-stats.sh <executor> executor pass
    ./scripts/update-agent-stats.sh <reviewer> reviewer pass
    ```
    Script auto-updates: `total_tasks_executed/reviewed`, `success_rate`, `recent_trend`, `last_active`. Creates profile if missing.
11. Give the User a summary: which task closed, who reviewed it, which commit, causal analysis captured (and pattern matched/created, if any), updated prediction/confidence accuracy, and updated agent profile stats.

### Step 3b — Verdict `changes`

0. **Update review sheet frontmatter**: Find `projects/<name>/reviews/<ID>-review.md`, update:
   - `reviewer: <--reviewer>`
   - `status: changes-requested`
   - `verdict: changes`
   - `verdict_date: <today>`

1. Require `--notes` describing specifically what needs fixing (don't accept an empty "changes" — ask again if missing).
2. Add a `## Findings từ reviewer` section to the task's body (under `## Plan` or at the end of the file), turning each point in `--notes` into a rework sub-task in `- [ ]` form.
3. Update the frontmatter: `status: changes-requested`, `updated: <today>`. Keep `executor:` unchanged (by default the same executor will fix it) unless the User says to reassign.
4. Write 1 entry to `log.md` (`operation: verdict`, `Trạng thái: Chờ duyệt` or a description of the rework, `Commit: n/a`).
5. Record prediction outcome into `knowledge/metrics/prediction-accuracy.md`: read `predicted_success` from the task's frontmatter, log entry with outcome `changes` (Rework/Fail), update accuracy metrics.
6. **Update Agent Reputation Profiles via script** (zero token overhead):
   ```bash
   ./scripts/update-agent-stats.sh <executor> executor changes
   ./scripts/update-agent-stats.sh <reviewer> reviewer changes
   ```
7. **Goal escalation** (`AGENTS-EXPERIMENTAL.md` §17.4, POC): Glob `projects/*/goals/GOAL-*.md`, check whether this task's ID appears in any `spawned_tasks:`. If so and this is the 2nd consecutive `changes-requested` verdict for a task spawned by that Goal (check `log.md` for the prior verdict on the same Goal's most recent spawned task), tell the User the Goal (`GOAL-<NNN>`) needs a human look rather than letting the User re-dispatch a third attempt unprompted.
8. Tell the User: the task has been reopened with findings; once the executor fixes it and reports back, `status: dispatched` needs to be updated (keeping or changing `executor:`), then `/review-order` run again with a new `--ref`.

### Common mistakes to avoid
- Recording a `pass` verdict when `reviewer:` == `executor:` — always refuse, no exceptions.
- Inventing a commit hash when the User/reviewer didn't provide one.
- Running tests or reading a diff yourself to "double-check" the AC — that's not `/verdict`'s job, trust the outcome the reviewer already reported.
- Closing a task when `status:` isn't `in-review` (e.g. a task that never went through `/review-order`).
- Recording `pass` on a `risk: high` task without collecting all four causal-analysis fields — required, not optional, for high-risk.
- Inventing a new `knowledge/patterns/<pattern_id>.md` file without stopping for User confirmation first (COLLABORATIVE, `AGENTS.md` §1, `AGENTS-PLAYBOOK.md` §11.6).
