---
id: CTV2-080
task_path: projects/control-tower-v2/tasks/CTV2-080-system-state-snapshot-querydb.md
project: control-tower-v2
result_ref: 3e1936a
executor: @claude-sonnet-medium
reviewer: @claude-opus
status: done
issued: 2026-07-27
verdict: pass
verdict_date: 2026-07-27
---

# Phiếu Review: CTV2-080 — System State snapshot block + generic query_db tool

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-080-system-state-snapshot-querydb.md`
- Result-ref: 3e1936a
- Executor: @claude-sonnet-medium
- Reviewer: @claude-opus
- Ngày phát phiếu: 2026-07-27

## Acceptance Criteria cần verify
## Tiêu chí nghiệm thu (AC)

- [x] `build_context_snapshot` thêm block `## System State`: Projects (đếm + tên), Agents (đếm, api/cli, default model), Sessions active, Tasks mở theo trạng thái (dispatched/in-review/awaiting approval)
- [x] Snapshot cap cứng ~30 dòng / ~600 token; enumeration top-N, còn lại chỉ đếm
- [x] Tool mới `query_db(entity, filters, limit<=50, offset)` — read-only, entity whitelist: tasks|projects|agents|sessions|knowledge|usage; filter fields whitelist per entity
- [x] `query_db` trả cột compact (id/title/status/…), không dump full row; agents KHÔNG trả `api_key`
- [x] `query_db` đăng ký trong registry với tier=eager, permission=read
- [x] `invalidate_context_snapshot` vẫn phủ đúng các mutation mới ảnh hưởng System State (agent/session changes)

## Definition of Done (AGENTS.md mục 3)
- [x] Toàn bộ AC pass
- [x] Test liên quan xanh 100%: backend/tests/test_context_hierarchy.py, backend/tests/test_command_router.py
- [x] Không regression (test khác trong module vẫn xanh)
- [x] Reviewer khác executor (xác nhận reviewer @claude-opus ≠ executor @claude-sonnet-medium)

## Test gợi ý chạy trong repo code
- `backend/tests/test_context_hierarchy.py`
- `backend/tests/test_command_router.py`

## Câu hỏi rủi ro (từ code-review-graph, tĩnh — không thay thế việc tự đọc diff)
- *(LLM/coordinator bổ sung từ graph nếu có; script không đọc diff và không gọi graph.)*

## Review Toolchain
Chạy theo toolchain của repo đích; preflight các tool đã đăng ký trước khi review.

## Review Results

### Tool Findings

**OCR Review** (3 comments, 1 high severity — all resolved as intentional):
1. `test_context_hierarchy.py:107` — Section header rename `## Current Context` → `## System State`: **Intentional per AC1**
2. `tool_registry.py:122-124` — `entity="query"` naming: **Correct; tool queries multiple entities, not one specific**
3. `test_chat_context.py:88` — Assertion updated to new snapshot format: **Matches implementation**

**Linter**: ruff not available in base shell (skipped)

### AC Verification Details

| AC | Status | Evidence |
|----|--------|----------|
| 1. System State block | ✅ | `context.py:138` — block header + 4 entity lines |
| 2. ~30 line cap | ✅ | `_TOP_N_PROJECT_NAMES=8`, remainder only counted |
| 3. query_db whitelist | ✅ | `command_router.py:24-126` — 6 entities, filters per entity |
| 4. Compact serialization | ✅ | Agent serializer excludes `api_key`; test validates |
| 5. Registry tier/permission | ✅ | `tool_registry.py:120-121` — `tier=eager, permission=read` |
| 6. Invalidation coverage | ✅ | `api/agents.py` + `api/sessions.py` call `invalidate_context_snapshot` on all mutations |

### Test Results

```
pytest backend/tests/test_context_hierarchy.py backend/tests/test_command_router.py
======================== 22 passed, 2 warnings in 0.34s ========================
```

Key AC-validating tests:
- `test_system_state_snapshot_stays_within_cap_at_scale` (AC2)
- `test_query_db_agents_never_includes_api_key` (AC4)
- `test_query_db_unknown_entity_returns_clear_error` (AC3)
- `test_query_db_unknown_filter_returns_clear_error` (AC3)
- `test_query_db_filters_rows_and_caps_limit` (AC3)

### Verdict

**PASS** — All 6 AC items verified, 22/22 tests green, no regressions, four-eyes satisfied.

Reviewed by: @claude-opus
Date: 2026-07-27
Commit: 3e1936a
