---
id: CTV2-056
title: "Chat UI Phase 1: Backend Schema + API"
status: done
priority: high
risk: normal
deadline: null
executor: "@claude-sonnet-medium"
reviewer: "@claude-opus"
result_ref: "cb66c05"
depends_on: [CTV2-053]
files:
  - backend/app/db/models.py
  - backend/alembic/versions/
  - backend/app/api/sessions.py
  - backend/app/schemas/session.py
flows: []
tests:
  - backend/tests/test_api_sessions.py
  - backend/tests/test_db.py
dispatched: 2026-07-27
in_review: null
predicted_success: high
prediction_factors:
  score: 0.75
  deductions:
    - "touches Session model (-0.15)"
    - "migration complexity (-0.1)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-056: Chat UI Phase 1: Backend Schema + API

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Reference

Architecture: `docs/chat-ui-architecture.md` (CTV2-055)

## Tiêu chí nghiệm thu (AC)

- [x] Session model có: `context_level` (enum: global/project/task), `project_id` (FK), `title`, `status` (enum: active/archived/closed), `pinned`, `message_count`, `last_activity_at`
- [x] Alembic migration với backfill: existing sessions với task_id → context_level='task', derive project_id từ task
- [x] Check constraints: `ck_sessions_task_requires_project`, `ck_sessions_context_level_consistency`
- [x] Composite index: `ix_sessions_context_listing` (context_level, project_id, status, last_activity_at)
- [x] API: GET /sessions với filter `?context_level=&project_id=&status=`
- [x] API: POST /sessions với context_level, project_id, title
- [x] API: PATCH /sessions/{id} với title, status, pinned

## Verification

- `pytest backend/tests/test_api_sessions.py -v` → 100% pass
- `pytest backend/tests/test_db.py -v` → migration tests pass
- `alembic upgrade head` → no errors
- Manual: create session with context_level='project', verify project_id required

## Review Findings (Round 1)

- [x] F1 (High): message_count/last_activity_at not maintained by CoordinatorService.append_message or context_hierarchy compaction
- [x] F2 (High): ON DELETE SET NULL on sessions.project_id violates ck_sessions_context_level_consistency, making projects undeletable
- [x] F3 (Medium): POST /sessions with only task_id returns 422 (should infer context_level)
- [x] F4 (Low): PATCH task_id silently no-ops instead of rejecting
- [x] F5 (Low): ix_sessions_context_listing omits pinned (leading sort key)

## Plan

1. Create enums: `ContextLevel`, `SessionStatus`
2. Update `Session` model với new fields + constraints
3. Create Alembic migration với backfill SQL
4. Update `SessionCreate`, `SessionUpdate`, `SessionResponse` schemas
5. Update `api/sessions.py` với filter + new fields
6. Write tests
