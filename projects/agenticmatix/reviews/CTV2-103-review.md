---
id: CTV2-103
task_path: projects/control-tower-v2/tasks/CTV2-103-kill-switch-cost-budget.md
project: control-tower-v2
result_ref: 3f26949
executor: @claude-sonnet-medium
reviewer: @claude-opus
status: completed
issued: 2026-07-27
verdict: pass
verdict_date: 2026-07-27
---

# Phiếu Review: CTV2-103 — Kill switch autonomy + trần chi phí mỗi task + trần run đồng thời

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-103-kill-switch-cost-budget.md`
- Result-ref: 3f26949
- Executor: @claude-sonnet-medium
- Reviewer: @claude-opus
- Ngày phát phiếu: 2026-07-27

## Acceptance Criteria cần verify
## Tiêu chí nghiệm thu (AC)

- [x] **Kill switch toàn cục**: `autonomy_enabled` setting disables all autonomous progression immediately; task left alone or cancelled with control, new tasks not dispatched. Toggle via `update_settings` tool without restart.
- [x] **Trần chi phí mỗi task**: `max_cost_usd_per_task` cap checked against `LLMUsage.cost_usd` ledger → stops task, sets `awaiting_approval=True`, no retry.
- [x] **Trần run đồng thời**: `max_concurrent_runs` cap → run queued, no process spawned. Fixed: now locks individual rows ordered by id and counts in Python (Postgres compat).
- [x] **Trần thời gian**: `run_timeout_seconds` is configurable via settings.
- [x] **Audit + escalate**: `_record_brake()` logs to `AuditLog` with `brake:<code>` action and sets `awaiting_approval=True` for hard brakes.
- [x] **Kill switch accessible**: `update_settings` tool exposes all four brake settings in `SETTINGS_WHITELIST`.

## Definition of Done (AGENTS.md mục 3)
- [x] Toàn bộ AC pass
- [x] Test liên quan xanh 100%: 54 tests passed (test_task_orchestration.py, unit/test_agent_runner.py, test_llm_usage.py)
- [x] Không regression (test khác trong module vẫn xanh)
- [x] Reviewer khác executor (xác nhận reviewer @claude-opus ≠ executor @claude-sonnet-medium)

## Test gợi ý chạy trong repo code
- `backend/tests/test_task_orchestration.py`
- `backend/tests/unit/test_agent_runner.py`
- `backend/tests/test_llm_usage.py`

## Câu hỏi rủi ro (từ code-review-graph, tĩnh — không thay thế việc tự đọc diff)
- *(LLM/coordinator bổ sung từ graph nếu có; script không đọc diff và không gọi graph.)*

## Review Toolchain
Chạy theo toolchain của repo đích; preflight các tool đã đăng ký trước khi review.

## Trả kết quả
`/verdict CTV2-103 <pass|changes> --reviewer @claude-opus [--commit <hash>] [--notes "..."]`
