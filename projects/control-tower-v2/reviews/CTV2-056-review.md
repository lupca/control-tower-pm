---
id: CTV2-056
task_path: projects/control-tower-v2/tasks/CTV2-056-chat-backend-schema.md
project: control-tower-v2
result_ref: cb66c05
executor: "@claude-sonnet"
reviewer: "@claude-opus"
status: passed
issued: 2026-07-27
verdict: pass
verdict_date: 2026-07-27
---

# Phiếu Review: CTV2-056 — Chat UI Phase 1: Backend Schema + API

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-056-chat-backend-schema.md`
- Result-ref: cb66c05 (Round 2 - fixes F1-F5)
- Executor: @claude-sonnet
- Reviewer: @claude-opus
- Ngày phát phiếu: 2026-07-27

## Acceptance Criteria cần verify

- [ ] Session model có: `context_level` (enum: global/project/task), `project_id` (FK), `title`, `status` (enum: active/archived/closed), `pinned`, `message_count`, `last_activity_at`
- [ ] Alembic migration với backfill: existing sessions với task_id → context_level='task', derive project_id từ task
- [ ] Check constraints: `ck_sessions_task_requires_project`, `ck_sessions_context_level_consistency`
- [ ] Composite index: `ix_sessions_context_listing` (context_level, project_id, status, last_activity_at)
- [ ] API: GET /sessions với filter `?context_level=&project_id=&status=`
- [ ] API: POST /sessions với context_level, project_id, title
- [ ] API: PATCH /sessions/{id} với title, status, pinned

## Definition of Done (AGENTS.md mục 3)

- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: `backend/tests/test_api_sessions.py`, `backend/tests/test_db.py`
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (bạn đang review, hãy xác nhận bạn ≠ @claude-sonnet)

## Test gợi ý chạy trong repo code

```bash
cd /home/lupca/projects/control-tower-v2
pytest backend/tests/test_api_sessions.py -v
pytest backend/tests/test_db.py -v
alembic upgrade head && alembic downgrade -1 && alembic upgrade head
```

## Review Toolchain

Chạy review theo repo's toolchain:
  cat .claude/review-toolchain.md

## Trả kết quả

Sau khi review xong, báo lại cho control-tower bằng lệnh:
`/verdict CTV2-056 <pass|changes> --reviewer @claude-opus [--commit <hash>] [--notes "..."]`
