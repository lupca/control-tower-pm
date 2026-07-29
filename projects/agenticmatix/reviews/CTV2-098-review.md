---
id: CTV2-098
task_path: projects/control-tower-v2/tasks/CTV2-098-gate-notification-global-inbox.md
project: control-tower-v2
result_ref: 72d7ab4
executor: @gpt-5.6-luna
reviewer: "@gemini-2.5-pro"
status: passed
verdict: pass
verdict_date: 2026-07-27
---

# Phiếu Review: CTV2-098 — Thông báo gate pending vào global chat + WS event (inbox điều phối)

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-098-gate-notification-global-inbox.md`
- Result-ref: 72d7ab4
- Executor: @gpt-5.6-luna
- Reviewer: @gemini-2.5-pro
- Ngày phát phiếu: 2026-07-27
- Ngày hoàn thành: 2026-07-27

## Acceptance Criteria cần verify
## Tiêu chí nghiệm thu (AC)

- [x] Khi driver gặp gate pending hoặc cần user quyết định: ghi message `role="system"` vào **session global của user** kèm task ID + prompt duyệt
- [x] Phát WS/SSE event để UI đang mở nhận ngay, không cần refresh
- [x] User trả lời `/approve <task>` ngay trong luồng global → gate được xử lý đúng task
- [x] Không spam: mỗi (task, gate) chỉ thông báo một lần cho tới khi trạng thái đổi
- [x] Message rollup này nằm trong hạn mức của CTV2-097 (1 dòng, không kèm trace)

## Definition of Done (AGENTS.md mục 3)
- [x] Toàn bộ AC pass
- [x] Test liên quan xanh 100%: backend/tests/test_api_sessions.py, backend/tests/integration/test_streaming.py, backend/tests/test_gate_transitions.py, backend/tests/test_task_orchestration.py, backend/tests/test_command_router.py
- [x] Không regression (toàn bộ test suite backend passed)
- [x] Reviewer khác executor (xác nhận reviewer @gemini-2.5-pro ≠ executor @gpt-5.6-luna)

## Test gợi ý chạy trong repo code
- `pytest backend/tests/test_api_sessions.py backend/tests/integration/test_streaming.py backend/tests/test_gate_transitions.py backend/tests/test_task_orchestration.py backend/tests/test_command_router.py -v`

## Đánh giá Chi tiết & Ghi chú Reviewer
- Commit `72d7ab4` triển khai cơ chế thông báo gate pending vào global inbox session và phát WS event qua `publish_event`.
- Trong `TaskOrchestrationService._notify_gate_pending`:
  - Lấy session global của user thông qua `CoordinatorService.get_or_create_global_session()`.
  - Ghi/cập nhật message với `role="system"`, `kind="gate_notification"`, `notification_state="pending"`, chứa `task.id` và `approval_prompt`.
  - Phát WS event với `type="gate_pending"`.
  - Đảm bảo chống trùng lặp (nếu message với `notification_state=="pending"` đã tồn tại cho cặp `(task_id, gate)` thì bỏ qua).
- Khi gate được quyết định (`decide_gate`), `_resolve_gate_notification` chuyển `notification_state` sang trạng thái kết quả (`approved`/`rejected`), cho phép các lần pending tiếp theo (nếu có) thông báo lại.
- Trong `CommandRouter._handle_approve_gate`:
  - Hỗ trợ `/approve <task_id>` khi tham số đầu tiên không phải số nguyên bằng cách query `GateRecord` pending mới nhất của `task_id`.

## Kết quả Verdict
`/verdict CTV2-098 pass --reviewer @gemini-2.5-pro --commit 72d7ab4 --notes "Gate pending global inbox notification & WS broadcast implemented cleanly with anti-spam check and /approve <task_id> routing."`
