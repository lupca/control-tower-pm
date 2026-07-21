---
name: verdict
description: Record an independent reviewer's verdict into control-tower — pass closes the task (needs human confirmation), changes reopens it with findings. Checks four-eyes (reviewer must differ from executor). Only updates Markdown, never touches code, never runs tests itself. Activate when the user types /verdict.
argument-hint: "<task path/ID> <pass|changes> --reviewer @id [--commit <hash>] [--notes ...]"
allowed-tools: Read, Edit
---

## Verdict — record the review outcome, enforce four-eyes

This skill **never checks the AC itself, never runs tests, never reads a diff** — it only records the outcome that an (outside-the-system) reviewer already determined, after checking the four-eyes constraint.

### Step 1 — Locate the task and parse arguments

1. Read `AGENTS.md` §1, §3, §4 if not already read this session (separation of duties, DoD, task lifecycle).
2. Find the task by ID/path in `$ARGUMENTS`: Glob `projects/*/tasks/<ID>-*.md` if the User gave an ID (e.g. `PMI-001`), or by the full path.
3. Parse: verdict (`pass` or `changes`), `--reviewer @id` (required), `--commit <hash>` (required if `pass`), `--notes "..."` (required if `changes`).
4. Read the frontmatter, check the current `status:`: only accept a verdict for a task that's `status: in-review`. If it's anything else → stop, tell the User (e.g. the task hasn't gone through `/review-order` yet, or is already `done`).

### Step 2 — Check four-eyes (MANDATORY, never skip)

Compare `--reviewer` against the `executor:` recorded in the frontmatter:
- If **they match** (same human/same AI) → **REFUSE to record a `pass` verdict**. Tell the User: this violates separation of duties (`AGENTS.md` §1) — it needs a second reviewer's sign-off, independent of the executor. Never lower the bar to let it through.
- If **they differ** → continue.

### Step 3a — Verdict `pass`

1. Require a real `--commit <hash>` (the actual commit hash of the change, never invented). If missing, ask the User/reviewer instead of guessing or leaving it blank.
2. **This is still a human decision** (`AGENTS.md` §3, §4: "A PASS verdict is only valid once a human confirms it"). If this `/verdict` command was typed directly by the User in the current session, treat that as confirmation. If you (the agent) are proposing to run `/verdict pass` yourself rather than the User typing it directly, you MUST stop and ask for explicit confirmation before recording it.
3. Mark every related AC and sub-task in the body as `- [x]`.
4. Update the frontmatter: `status: done`, `reviewer: "<--reviewer>"`, `result_ref:` (keep as-is or update to the real commit), `updated: <today>`.
5. If the task declares `depends_on:` (see `AGENTS.md` §2.2): tell the User which tasks might now be unblocked, since there's no automatic parsing/unblocking mechanism yet — don't infer it yourself.
6. Write 1 entry to `log.md` (`operation: verdict`, format in `AGENTS.md` §7), with the `Commit:` field = the real hash just received.
7. Record prediction outcome into `knowledge/metrics/prediction-accuracy.md`: read `predicted_success` from the task's frontmatter, log entry with outcome `pass` (Success), update accuracy metrics.
8. Give the User a summary: which task closed, who reviewed it, which commit, and updated prediction accuracy.

### Step 3b — Verdict `changes`

1. Require `--notes` describing specifically what needs fixing (don't accept an empty "changes" — ask again if missing).
2. Add a `## Findings từ reviewer` section to the task's body (under `## Plan` or at the end of the file), turning each point in `--notes` into a rework sub-task in `- [ ]` form.
3. Update the frontmatter: `status: changes-requested`, `updated: <today>`. Keep `executor:` unchanged (by default the same executor will fix it) unless the User says to reassign.
4. Write 1 entry to `log.md` (`operation: verdict`, `Trạng thái: Chờ duyệt` or a description of the rework, `Commit: n/a`).
5. Record prediction outcome into `knowledge/metrics/prediction-accuracy.md`: read `predicted_success` from the task's frontmatter, log entry with outcome `changes` (Rework/Fail), update accuracy metrics.
6. Tell the User: the task has been reopened with findings; once the executor fixes it and reports back, `status: dispatched` needs to be updated (keeping or changing `executor:`), then `/review-order` run again with a new `--ref`.

### Common mistakes to avoid
- Recording a `pass` verdict when `reviewer:` == `executor:` — always refuse, no exceptions.
- Inventing a commit hash when the User/reviewer didn't provide one.
- Running tests or reading a diff yourself to "double-check" the AC — that's not `/verdict`'s job, trust the outcome the reviewer already reported.
- Closing a task when `status:` isn't `in-review` (e.g. a task that never went through `/review-order`).
