---
name: report
description: Scan all of projects/*/tasks/*.md, count tasks by status frontmatter, update <project-name>.md (the file matching the project's folder name) + index.md, and update knowledge/_index.md. Activate when the user types /report or asks about overall project progress.
allowed-tools: Read, Edit, Glob, Grep, Bash(python3 scripts/ct-report-stats.py*)
---

## Report — update progress into index.md + the knowledge index

### Process

1. Run `python3 scripts/ct-report-stats.py --apply` (see `[[ADR-007-report-stats-script]]`). This glob's `projects/*/tasks/*.md`, counts `status:` per project, and rewrites the `## Tiến độ` + `## Tasks` blocks in each `projects/<name>/<name>.md` in place — no manual Glob/Read/Edit needed for that part. It never touches task files, `index.md`, or `log.md`.
2. Parse the JSON it prints: each entry has `project`, `total`, `counts` (new), `old_counts` (before this run), `tasks` (id/slug/title/status). Report any status not in `done/todo/dispatched/in-review/changes-requested` as a legacy/invalid state instead of treating it as part of the active state machine. If an entry has a `warning` (missing `<name>.md`), flag it instead of guessing a fix.
3. Diff `counts` vs `old_counts` per project — this is what changed since last `/report`, useful for the summary in step 8.
4. Update the "BẢN ĐỒ TIẾN ĐỘ DỰ ÁN" table in `index.md` (§3): the Progress column (Done/Total), and Status (🔄 Đang chạy if tasks remain unfinished, ✅ Hoàn tất if Done == Total > 0, ⏳ Tạm dừng if Total == 0). The narrative "Ghi chú"/"Executor/Reviewer hiện tại" columns still need judgment (e.g. which task is stuck, who's assigned) — write those from the `tasks` list, not mechanically.
5. Update "Thời gian cập nhật cuối" (§1) to the current time.
6. Glob `knowledge/**/*.md` + `projects/*/docs/*.md`, read `type:` from the frontmatter, group by type. Update `knowledge/_index.md` (the cross-project table by `decisions/domains/conventions/research`, the per-project table by project) and the "KNOWLEDGE MAP" table in `index.md` (§6).
7. Write 1 entry to `log.md` (COLLABORATIVE): summarizing what was updated for each project + knowledge.
8. Show the updated progress table to the user right in the chat, not just written to a file.

### Notes
- `/report` only reads and aggregates numbers — it must never edit task content on its own (never change `status:` on the user's behalf, never delete a task). `ct-report-stats.py` enforces this too: it only ever writes the Tiến độ/Tasks blocks in `<name>.md`.
- If a task has clearly been open for a long time (`deadline:` overdue) and is still not `done`, it's fine to call that out as a warning note in the report to the user, but don't fix it yourself.
- If `scripts/ct-report-stats.py` errors or is missing, fall back to the manual process (Glob + read frontmatter + hand-edit the two blocks) rather than blocking `/report` entirely.
