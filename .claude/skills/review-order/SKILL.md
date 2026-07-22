---
name: review-order
description: Generate a review sheet for a task the executor has reported done — gathering AC, DoD, tests, result-ref, and risk questions (from the graph, read-only) to hand to an independent reviewer (a different human/AI than the executor). Does NOT review itself, does NOT run tests, does NOT read the actual diff. Activate when the user types /review-order.
argument-hint: "<task path/ID> --ref <branch|commit|PR>"
allowed-tools: Read, Edit, Write, Grep, Glob, mcp__code-review-graph__get_suggested_questions_tool, mcp__code-review-graph__get_affected_flows_tool
---

## Review Order — issue the review sheet, don't review it yourself

You're in control-tower, NOT the target code repo. This skill **never reads the executor's actual diff** and **never runs tests** — it only aggregates existing information (the task + static graph data) into a self-contained review sheet.

### Step 1 — Locate the task

1. Read `AGENTS.md` (especially §1, §4) and `AGENTS-REFERENCE.md` §5 (handoff artifacts) and `index.md` §2 (PROJECT REGISTRY) if not already read this session.
2. Find the task by ID/path in `$ARGUMENTS`: Glob `projects/*/tasks/<ID>-*.md` if the User gave an ID (e.g. `PMI-001`), or by the full path if the User specified it directly.
3. Read the frontmatter, check the task's current `status:`:
   - If `status: dispatched` → valid, continue.
   - If `status` is anything else (`todo`, `ready`, `in-review`, `done`, `changes-requested`) → stop, tell the User: the task isn't ready for a review sheet (e.g. not dispatched yet, or already in review) — don't change the state yourself.
4. Get `--ref <branch|commit|PR>` from `$ARGUMENTS`. If missing, ask the User (never invent a result-ref).

### Step 2 — Record the result-ref, change state

1. Write `result_ref: "<the --ref value>"` into the frontmatter.
2. Update `status: in-review`, `in_review: <today's date>`, `updated: <today's date>`.

### Step 3 — Enrich with risk questions (read-only, optional)

Look up the project's `repo_root` in the PROJECT REGISTRY, then (if the graph is available):

1. `get_suggested_questions_tool(repo_root=...)` — priority questions: bridge node missing tests, uncovered hub node, unexpected coupling.
2. `get_affected_flows_tool(changed_files=<the files: list ALREADY RECORDED in the task from the Spec Gate>, repo_root=...)` — reuse the file list locked in when the task was written, **never** read the executor's new git diff (this boundary keeps it static, not a real review).

If the graph returns nothing useful or errors out, skip this step — the review sheet is still valid with just the task's AC/DoD/tests.

### Step 4 — Generate the review sheet

Write the file `projects/<name>/reviews/<ID>-review.md` (e.g. `projects/topvnsport-pmi/reviews/PMI-001-review.md`) — `<name>` comes from the task path found in Step 1. Create the `reviews/` directory if that project doesn't have one yet.

```markdown
# Phiếu Review: <ID> — <title>

- Dự án: <tên dự án> (`<repo_root>`)
- Task gốc: `projects/<tên>/tasks/<ID>-<slug>.md`
- Result-ref: <branch/commit/PR từ --ref>
- Executor: <executor: của task>
- Ngày phát phiếu: <hôm nay>

## Acceptance Criteria cần verify
<copy nguyên khối "## Tiêu chí nghiệm thu (AC)" từ task>

## Definition of Done (AGENTS.md mục 3)
- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: <danh sách tests: từ task>
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (bạn đang review, hãy xác nhận bạn ≠ <executor>)

## Test gợi ý chạy trong repo code
<lệnh test theo CLAUDE.md/Project Gates của dự án đó, vd docker compose exec pytest ...>

## Câu hỏi rủi ro (từ code-review-graph, tĩnh — không thay thế việc bạn tự đọc diff)
<liệt kê kết quả get_suggested_questions_tool / get_affected_flows_tool nếu có>

## Gợi ý công cụ
Repo code đích có thể có sẵn skill `/code-review` (hoặc tương đương) — khuyến khích dùng để đọc diff + chạy test một cách có cấu trúc.

## Trả kết quả
Sau khi review xong, báo lại cho control-tower bằng lệnh:
`/verdict <ID> <pass|changes> --reviewer @<tên bạn> [--commit <hash>] [--notes "..."]`
```

### Step 5 — Close out

1. Write 1 entry to `log.md` (`operation: review-order`, format in `AGENTS-REFERENCE.md` §7) — stating the path of the review sheet just generated.
2. Tell the User: the sheet is ready at `projects/<name>/reviews/<ID>-review.md`, hand it to an independent reviewer (**must differ from** the task's `executor:` — restate the four-eyes rule).

### Common mistakes to avoid
- Reviewing/scoring the AC yourself right in this step — that's the outside reviewer's job, not `/review-order`'s.
- Reading the executor's git diff/log yourself to "help" fill in questions — only use static data already recorded in the task, or graph data that doesn't require a diff.
- Issuing a sheet for a task that isn't `dispatched` yet, or is already `in-review`/`done`.
