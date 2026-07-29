---
id: CTV2-089
task_path: projects/control-tower-v2/tasks/CTV2-089-orchestration-driver-advance-task.md
project: control-tower-v2
result_ref: b49f829
executor: @claude-sonnet-medium
reviewer: @claude-opus
status: completed
issued: 2026-07-27
verdict: pass
verdict_date: 2026-07-27
---

# Phiếu Review: CTV2-089 — Orchestration Driver: dramatiq actor advance_task (event-driven, 0 token)

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-089-orchestration-driver-advance-task.md`
- Result-ref: b49f829
- Executor: @claude-sonnet-medium
- Reviewer: @claude-opus
- Ngày phát phiếu: 2026-07-27

## Acceptance Criteria cần verify
## Tiêu chí nghiệm thu (AC)

- [x] Actor `advance_task(task_id, trigger)` thực thi bảng quyết định §3.1: `todo` (đủ AC) → chọn executor + dispatch; `awaiting-review` → chọn reviewer + `request_review`; `in-review` (review run xong) → `request_verdict`; `changes-requested` → replan trong hạn vòng; gate `pending` → dừng + thông báo
- [x] Event-driven, KHÔNG polling: `advance_task.send()` được kích hoạt sau `run_agent` kết thúc, sau khi gate được approve, sau khi review run xong, và sau verdict `changes`
- [x] Mọi chuyển trạng thái đi qua `TaskOrchestrationService` (FSM authoritative) — driver không tự set field trạng thái
- [x] Chặn vòng lặp: `advance_task` cho cùng task có trần số vòng và không tự gọi lại khi trạng thái không đổi; vượt trần → escalate cho user, không quay vòng im lặng
- [x] **Fail-closed khi thiếu AC**: task `todo` không có `acceptance_criteria` → driver **dừng và escalate**, tuyệt đối không dispatch. Có test khẳng định điều này ngay cả khi CTV2-091 chưa hoàn tất
- [x] Driver tôn trọng kill switch + trần chi phí của CTV2-103: autonomy tắt toàn cục → không đẩy task nào; chạm trần chi phí/số run đồng thời → dừng và báo
- [x] Gate `pending` → driver dừng đúng chỗ, không tự approve
- [x] Actor idempotent: gọi trùng cho cùng (task, trigger) không tạo run trùng

## Definition of Done (AGENTS.md mục 3)
- [x] Toàn bộ AC pass
- [x] Test liên quan xanh 100%: backend/tests/unit/test_agent_runner.py, backend/tests/test_task_orchestration.py, backend/tests/integration/test_full_flow.py (75/75 passed)
- [x] Không regression (test khác trong module vẫn xanh)
- [x] Reviewer khác executor (xác nhận reviewer @claude-opus ≠ executor @claude-sonnet-medium)

## Test gợi ý chạy trong repo code
- `backend/tests/unit/test_agent_runner.py`
- `backend/tests/test_task_orchestration.py`
- `backend/tests/integration/test_full_flow.py`

## Câu hỏi rủi ro (từ code-review-graph, tĩnh — không thay thế việc tự đọc diff)
- *(LLM/coordinator bổ sung từ graph nếu có; script không đọc diff và không gọi graph.)*

## Review Toolchain
Chạy theo toolchain của repo đích; preflight các tool đã đăng ký trước khi review.

## Trả kết quả
`/verdict CTV2-089 <pass|changes> --reviewer @claude-opus [--commit <hash>] [--notes "..."]`

## Review Notes

**Verdict: PASS** — Reviewed by @claude-opus on 2026-07-27

### Implementation Summary

The `advance_task` dramatiq actor (agent_runner.py:489-527) correctly implements the §3.1 decision table:
- Status routing via `_advance_task_step` → `_advance_todo`, `_advance_awaiting_review`, `_advance_changes_requested`
- Event-driven: `_nudge_driver()` calls after run completion (3 points) and gate approval (dispatch.py)
- All transitions go through `TaskOrchestrationService` methods (`request_dispatch`, `request_review`, `reopen_for_replan`)
- Loop prevention: `_advance_task_stalled()` + `AUTO_MAX_ROUNDS` cap with escalation
- Fail-closed: explicit AC check in `_advance_todo` → escalate if missing
- Brakes: `service.check_brakes()` before all actions
- Gate pending: early return when `task.awaiting_approval`
- Idempotency: round-scoped keys (`advance:{task_id}:dispatch:r{round_}`)

The `in-review` → `request_verdict` path is handled by `run_agent` line 995 after parsing review output, which is the correct design (verdict is derived from run output, not a driver decision).

### Test Coverage

75/75 tests pass including specific coverage for:
- `test_advance_task_todo_missing_ac_escalates_fail_closed`
- `test_advance_task_respects_autonomy_kill_switch`
- `test_advance_task_changes_requested_escalates_at_round_cap`
- `test_advance_task_dispatch_idempotency_key_prevents_duplicate_run`
- `test_advance_task_stalled_actionable_status_escalates_instead_of_looping`
