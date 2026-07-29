---
id: CTV2-088
task_path: projects/control-tower-v2/tasks/CTV2-088-idempotency-key-attempt-nonce.md
project: control-tower-v2
result_ref: da3ba47
executor: @claude-sonnet-high
reviewer: "@claude-opus"
status: passed
issued: 2026-07-27
verdict: pass
verdict_date: 2026-07-27
---

# Phiếu Review: CTV2-088 — Sửa idempotency: attempt/nonce vào command key + kiểm tra trạng thái trước khi trả record

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-088-idempotency-key-attempt-nonce.md`
- Result-ref: da3ba47
- Executor: @claude-sonnet-high
- Reviewer: @claude-opus
- Ngày phát phiếu: 2026-07-27

## Acceptance Criteria cần verify
## Tiêu chí nghiệm thu (AC)

- [ ] Command key gồm attempt/nonce (ví dụ `chat:{session}:{action}:{hash}:{attempt}`) — retry có chủ đích sinh key mới
- [ ] **(viết lại vòng 3)** Bất biến cần đạt, KHÔNG quy định cách sắp xếp dòng lệnh: không bao giờ trả
  `applied=True` khi trạng thái task hiện tại không cho phép hành động đó. Reviewer vòng 2 đã phán xử rằng
  yêu cầu cũ ("đảo `_assert_status` lên trước khi trả record idempotent") là **không implement được theo
  nghĩa đen** — nó phá một test idempotent-replay đang xanh; lý do executor đưa ra đã được verify và chấp nhận.
  Cách đạt bất biến do executor chọn, nhưng phải chứng minh bằng test ở **cả hai** mode `bypass` và `supervised`
- [ ] Khi record cũ trỏ tới AgentRun đã terminal (`success`/`timeout`/`cancelled`, hoặc `failed` với `attempt >= max_attempts`) → không trả về như thành công, mà tạo run mới hoặc báo lỗi rõ ràng
- [ ] Chống double-dispatch thật sự vẫn giữ: hai lần gọi song song cùng args trong cùng một chu kỳ chỉ tạo **một** run (có test đua)
- [ ] Không còn đường nào để `dispatch` trả về "thành công" mà không có run nào ở trạng thái chạy được

## Definition of Done (AGENTS.md mục 3)
- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: backend/tests/test_command_router.py, backend/tests/test_gate_transitions.py, backend/tests/integration/test_failure_recovery.py
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (xác nhận reviewer @claude-opus ≠ executor @claude-sonnet-high)

## Test gợi ý chạy trong repo code
- `backend/tests/test_command_router.py`
- `backend/tests/test_gate_transitions.py`
- `backend/tests/integration/test_failure_recovery.py`

## Câu hỏi rủi ro (từ code-review-graph, tĩnh — không thay thế việc tự đọc diff)
- *(LLM/coordinator bổ sung từ graph nếu có; script không đọc diff và không gọi graph.)*

## Review Toolchain
Chạy theo toolchain của repo đích; preflight các tool đã đăng ký trước khi review.

## Trả kết quả
`/verdict CTV2-088 <pass|changes> --reviewer @claude-opus [--commit <hash>] [--notes "..."]`

## Ghi chú từ điều phối — vòng 3 (không thay việc bạn tự verify)

Bạn là **reviewer thứ hai** trên task này. `rejections` = 2 nên quy tắc xoay vòng bắt buộc góc nhìn mới — hai vòng trước do `@claude-opus-5-medium` review. **Đừng chỉ kiểm những gì reviewer trước đã liệt kê**; nếu bạn thấy vấn đề ở chỗ họ đã cho qua, đó chính là lý do bạn được gọi vào.

Lịch sử ngắn:
- **Vòng 1** (`e24561e`, executor `@claude-sonnet-medium`): 7 finding. Executor tự chế một guard hẹp thay cho AC2, và chính guard đó chặn luồng approve ở mode supervised.
- **Vòng 2** (`3b1cbba`, executor `@claude-sonnet-high`): gỡ guard sai, sửa 4/7 finding. Reviewer phán xử **AC2 không implement được theo nghĩa đen** và chấp nhận lý do của executor → **AC2 đã được viết lại thành bất biến** (xem AC trong task). Còn sót: guard soi pending parent record trong khi `_result_for_record` đi xuống child approved decision, nên ở supervised guard bị vô hiệu.
- **Vòng 3** (`da3ba47`, đang review): resolve pending → child trước khi check status; parametrize 3 test staleness qua cả `bypass` lẫn `supervised`; tách test truncation khỏi thân `test_command_router_parse`. Full suite 336 passed.

Hai điểm cần bạn soi kỹ nhất:

1. **Bất biến của AC2 (bản viết lại) có thực sự đạt không** — không phải "có comment giải thích" là đủ. Bất biến là: không bao giờ trả `applied=True` khi trạng thái task hiện tại không cho phép hành động đó. Hãy tự tìm đường phá nó, đừng chỉ đọc test của executor.
2. **Test có thật sự chứng minh điều nó tuyên bố không.** Bug ở vòng 1–2 sống sót vì mọi test staleness chỉ chạy `mode="bypass"` — nhánh không có bug. Executor báo đã parametrize và các case supervised fail trước khi sửa; hãy kiểm chứng lại điều đó (ví dụ revert phần sửa và xem test có đỏ thật không). Xem `knowledge/patterns/vacuous-acceptance-test.md`.

Bối cảnh: `supervised` là mode **mặc định** mà Orchestration Driver (CTV2-089) sẽ chạy dưới, nên lỗi ở nhánh này nghiêm trọng hơn ở `bypass`.

Ngoài phạm vi: commit `15bfe3e` (Token Telemetry route + UI) là commit tay của user.
