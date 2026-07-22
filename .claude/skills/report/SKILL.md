---
name: report
description: Scan all of projects/*/tasks/*.md, count tasks by status frontmatter, update <project-name>.md (the file matching the project's folder name) + index.md, and update knowledge/_index.md. Activate when the user types /report or asks about overall project progress.
allowed-tools: Read, Edit, Glob, Grep
---

## Report — update progress into index.md + the knowledge index

### Process

1. List every file under `projects/*/tasks/*.md` (Glob).
2. For each file, read `status:` from the frontmatter. Count per project: `done`, `todo`, `ready`, `dispatched`, `in-review`, `changes-requested`. Total = sum of all statuses.
3. Update the "Tiến độ" table in each project's `projects/<name>/<name>.md` (task count per status).
3b. **Regenerate the `## Tasks` section** in each `<name>.md`: re-list every `- [[<ID>-<slug>]] — <title> (<status>)` for every file under `tasks/*.md` (reading `id`/`title`/`status` from the frontmatter). This is a self-healing step — overwrite this entire section on every run, don't append, so it automatically reflects new tasks created by `/pm`/`/ingest` or tasks that were deleted. If `tasks/` is empty, write `*(chưa có task nào)*`.
4. Update the "BẢN ĐỒ TIẾN ĐỘ DỰ ÁN" table in `index.md` (§3): the Progress column (Done/Total), and Status (🔄 Đang chạy if tasks remain unfinished, ✅ Hoàn tất if Done == Total > 0, ⏳ Tạm dừng if Total == 0).
5. Update "Thời gian cập nhật cuối" (§1) to the current time.
6. Glob `knowledge/**/*.md` + `projects/*/docs/*.md`, read `type:` from the frontmatter, group by type. Update `knowledge/_index.md` (the cross-project table by `decisions/domains/conventions/research`, the per-project table by project) and the "KNOWLEDGE MAP" table in `index.md` (§6).
7. Write 1 entry to `log.md` (COLLABORATIVE): summarizing what was updated for each project + knowledge.
8. Show the updated progress table to the user right in the chat, not just written to a file.

### Notes
- `/report` only reads and aggregates numbers — it must never edit task content on its own (never change `status:` on the user's behalf, never delete a task).
- If a task has clearly been open for a long time (`deadline:` overdue) and is still not `done`, it's fine to call that out as a warning note in the report to the user, but don't fix it yourself.
