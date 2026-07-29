---
id: CTV2-097
task_path: projects/control-tower-v2/tasks/CTV2-097-sub-session-per-task.md
project: control-tower-v2
result_ref: 802eba3
executor: @gpt-5.6-luna
reviewer: @gemini-2.5-pro
status: completed
verdict: pass
verdict_date: 2026-07-27
---

# Phiếu Review: CTV2-097 — Sub-session per task: driver chạy task ở session context_level=task, global chỉ giữ 1 dòng

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-097-sub-session-per-task.md`
- Result-ref: 802eba3
- Executor: @gpt-5.6-luna
- Reviewer: @gemini-2.5-pro
- Ngày phát phiếu: 2026-07-27
- Ngày hoàn thành: 2026-07-27

## Acceptance Criteria cần verify
## Tiêu chí nghiệm thu (AC)

- [x] Driver chạy mỗi task trong session riêng `context_level='task'`, liên kết `task_id`
- [x] Session global chỉ nhận **1 dòng rollup mỗi task** (trạng thái + kết quả + link), không nhận toàn bộ trace
- [x] Mở lại task → truy xuất được sub-session đầy đủ (không mất lịch sử, chỉ là không nằm trong global)
- [x] API/UI liệt kê được sub-session theo task
- [x] Không hồi quy cho chat thủ công của user ở cấp global/project

## Definition of Done (AGENTS.md mục 3)
- [x] Toàn bộ AC pass
- [x] Test liên quan xanh 100%: backend/tests/test_context_hierarchy.py, backend/tests/test_api_sessions.py, backend/tests/integration/test_chat_context.py (32/32 passed)
- [x] Không regression (toàn bộ 443 test suite backend passed)
- [x] Reviewer khác executor (xác nhận reviewer @gemini-2.5-pro ≠ executor @gpt-5.6-luna)

## Test Kết quả Execution
- `pytest backend/tests/test_context_hierarchy.py backend/tests/test_api_sessions.py backend/tests/integration/test_chat_context.py -v`: **32 PASSED**
- `pytest backend/tests/ -v`: **443 PASSED**

## Đánh giá Chi tiết & Ghi chú Reviewer
- Commit `802eba3` triển khai sạch sẽ việc cách ly session cho từng task via `get_or_create_task_session` trong `CoordinatorService`.
- `record_task_rollup` giải quyết bài toán token optimization bằng việc upsert duy nhất 1 dòng message dạng `kind="task_rollup"` vào global session cho mỗi task.
- API và DB query hỗ trợ lọc sub-session chính xác theo `task_id` và `context_level='task'`.

## Kết quả Verdict
`/verdict CTV2-097 pass --reviewer @gemini-2.5-pro --commit 802eba3 --notes "Task sessions isolated with context_level=task and compact single-line rollups recorded in global session. All 443 tests passing."`
