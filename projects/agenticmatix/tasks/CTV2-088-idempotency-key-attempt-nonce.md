---
id: CTV2-088
title: "Sửa idempotency: attempt/nonce vào command key + kiểm tra trạng thái trước khi trả record"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: urgent
risk: high
deadline: null
executor: "@claude-sonnet-high"
reviewer: "@claude-opus"
result_ref: "da3ba47"
depends_on: []
files:
  - backend/app/services/command_router.py
  - backend/app/services/task_orchestration.py
flows: []
tests:
  - backend/tests/test_command_router.py
  - backend/tests/test_gate_transitions.py
  - backend/tests/integration/test_failure_recovery.py
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: medium
prediction_factors:
  score: 0.65
  deductions:
    - "hub node: execute_tool (36), TaskOrchestrationService (43) (-0.2)"
    - "đổi semantics idempotency có thể mở lại lỗi double-dispatch nếu làm ẩu (-0.15)"
created: 2026-07-27
updated: 2026-07-27
rejections: 2
---

# CTV2-088: Sửa idempotency — chặn "kẹt im lặng"

> Dự án: [[projects/control-tower-v2/control-tower-v2]]
> Nguồn: `docs/research/autonomous-coordination-gap-analysis.md` §5.3 (G12), lộ trình #2b

**Phải làm trước khi bật driver tự chủ.** `_command_key` = `sha256(args)[:24]` + session + action, không nonce. Trong `_request_gate`, `_idempotent_record` chạy **trước** `_assert_status`, nên lần gọi lại trả `applied=True` kèm AgentRun **cũ đã terminal** → coordinator tin việc đã giao, thực tế không run nào chạy. Dưới automation lỗi này sẽ bị che hoàn toàn.

## Tiêu chí nghiệm thu (AC)

- [x] Command key gồm attempt/nonce (ví dụ `chat:{session}:{action}:{hash}:{attempt}`) — retry có chủ đích sinh key mới
- [x] **(viết lại vòng 3)** Bất biến cần đạt, KHÔNG quy định cách sắp xếp dòng lệnh: không bao giờ trả
  `applied=True` khi trạng thái task hiện tại không cho phép hành động đó. Reviewer vòng 2 đã phán xử rằng
  yêu cầu cũ ("đảo `_assert_status` lên trước khi trả record idempotent") là **không implement được theo
  nghĩa đen** — nó phá một test idempotent-replay đang xanh; lý do executor đưa ra đã được verify và chấp nhận.
  Cách đạt bất biến do executor chọn, nhưng phải chứng minh bằng test ở **cả hai** mode `bypass` và `supervised`
- [x] Khi record cũ trỏ tới AgentRun đã terminal (`success`/`timeout`/`cancelled`, hoặc `failed` với `attempt >= max_attempts`) → không trả về như thành công, mà tạo run mới hoặc báo lỗi rõ ràng
- [x] Chống double-dispatch thật sự vẫn giữ: hai lần gọi song song cùng args trong cùng một chu kỳ chỉ tạo **một** run (có test đua)
- [x] Không còn đường nào để `dispatch` trả về "thành công" mà không có run nào ở trạng thái chạy được

## Verification

- `pytest backend/tests/test_command_router.py backend/tests/test_gate_transitions.py backend/tests/integration/test_failure_recovery.py -v` → xanh
- Test hồi quy: dispatch → run fail terminal → dispatch lại cùng args → có run MỚI (không phải record cũ)
- Test đua: 2 lời gọi đồng thời cùng args → đúng 1 AgentRun

## Plan

1. Viết test **đỏ** trước: dispatch → làm run fail terminal → dispatch lại cùng args → hiện tại trả `applied=True` với run cũ. Test này là bằng chứng lỗi tồn tại.
2. Đổi `_command_key` thành `{session}:{action}:{hash}:{attempt}` — attempt lấy từ số lần thử của task/gate, không phải timestamp (giữ tính tất định để resume được).
3. Trong `_request_gate`, chuyển `_assert_status` lên **trước** `_idempotent_record`; record idempotent chỉ được trả khi trạng thái hiện tại vẫn hợp lệ cho hành động đó.
4. Khi record cũ trỏ run terminal → coi như không có record: tạo run mới hoặc raise lỗi rõ ràng, không bao giờ trả "thành công" rỗng.
5. Giữ chống double-dispatch: thêm test đua 2 lời gọi đồng thời → đúng 1 AgentRun (dựa vào khoá DB hiện có, không nới `with_for_update`).

## Sub-tasks

- [ ] Đổi cấu trúc `_command_key`
- [ ] Đảo thứ tự kiểm tra trạng thái vs idempotent record
- [ ] Xử lý record trỏ run terminal
- [ ] Tests: hồi quy kẹt im lặng + test đua

## Ghi chú vòng 2

Executor đổi từ `@claude-sonnet-medium` sang `@claude-sonnet-high` (chỉ định của user, 2026-07-27).
Lý do: vòng 1 không làm AC2 theo spec mà tự thay bằng một guard hẹp hơn, và chính guard đó đẻ ra
regression chặn luồng approve. Đây là lỗi phán đoán về phạm vi, không phải lỗi cú pháp — cần effort cao hơn.

**Bắt buộc vòng này:** làm ĐÚNG việc đảo thứ tự ở AC2 (status check trước khi trả idempotent record),
không thay bằng phương án khác. Nếu thấy phương án đảo thứ tự có vấn đề thì BÁO LẠI thay vì tự đổi hướng.

## Ghi chú vòng 3

**Reviewer vòng 3 đổi sang `@claude-opus` (Opus 4.5)** — `rejections` = 2 nên quy tắc xoay vòng reviewer
bắt buộc góc nhìn thứ ba (`review-order` skill, Step 2). Executor giữ nguyên `@claude-sonnet-high`: vòng 2
không làm sai, lỗi còn lại rất hẹp và đã có đường sửa cụ thể.

**AC2 đã được viết lại** (xem AC ở trên) theo phán xử của reviewer vòng 2: yêu cầu cũ quy định cách sắp xếp
dòng lệnh chứ không quy định bất biến, và cách đó không khả thi. Đây là lỗi của người viết AC, không phải
của executor — vòng 2 báo lại đúng cách và đã được ghi nhận.

**Lỗi còn lại rất hẹp, đã có đường sửa rõ ràng từ reviewer:** `_reject_if_stale_dispatch_record`
(`task_orchestration.py:793`) early-return khi `record.status != "approved"`, nên ở mode `supervised` nó soi
PENDING PARENT record; trong khi `_result_for_record` (`:818-826`) lại đi tiếp xuống child approved decision
và trả `applied=True` kèm run của child. Hai bên nhìn vào hai record khác nhau nên guard bị vô hiệu.
Sửa: resolve pending → child TRƯỚC khi check status, mirror đúng `_result_for_record`.

**Bắt buộc:** mọi test staleness phải parametrize CẢ `bypass` LẪN `supervised`. Toàn bộ test hiện có chỉ dùng
`bypass` — đó chính là lý do lỗi này xanh giả qua hai vòng. `supervised` là mode mặc định mà driver tự chủ
(CTV2-089) sẽ chạy dưới, nên đây là mode quan trọng nhất chứ không phải trường hợp biên.

**Dọn:** `test_command_key_truncation_preserves_attempt_discriminator` đang bị chèn vào TRONG thân
`test_command_router_parse` (`test_command_router.py:32`) — tách ra, đặt lại tên cho đúng thứ mỗi test kiểm.

## Findings từ reviewer
- [ ] AC2 chưa implement: _assert_status vẫn chạy SAU khi trả idempotent record (task_orchestration.py:506-511), plan step 3 yêu cầu đảo thứ tự — thứ tự cũ còn nguyên ở decide_gate, record_execution_success, record_execution_failure, record_dispatch_queue_failure
- [ ] Regression BLOCKING mới ở decide_gate: _reject_if_stale_dispatch_record áp lên approve key (không có attempt component) nên approve-replay ở mode supervised sau khi run success trở thành hard error vĩnh viễn, không có đường phục hồi, và thông báo lỗi hướng dẫn caller làm việc bất khả thi
- [ ] POST /gates/{id}/decision replay từ 200 thành lỗi
- [ ] Stale-guard unreachable trên router path: attempt bump đổi key nên stale record không bao giờ được tra ra — lần dispatch thứ hai fail ở _assert_status chứ không phải StaleIdempotencyRecordError, cần làm nó reachable hoặc bỏ như dead code
- [ ] Coi failed là terminal vô điều kiện, AC yêu cầu failed chỉ terminal khi attempt >= max_attempts
- [ ] Truncation [:100] áp SAU khi nối :{attempt} nên session_id dài sẽ cắt mất discriminator — phải cắt trước khi nối
- [ ] Thiếu regression test cho re-dispatch sau run terminal success/timeout/cancelled — test hiện có chỉ phủ đường queue-failure

## Findings từ reviewer
- [ ] AC2: reviewer PHÁN XỬ là không thể implement theo nghĩa đen — lý do executor đưa ra đã được verify và chấp nhận
- [ ] AC2 cần VIẾT LẠI, không phải executor làm sai
- [ ] AC5 FAIL trong mode supervised (đúng mode mà driver tự chủ sẽ chạy): _reject_if_stale_dispatch_record early-return khi record.status != approved (task_orchestration.py:793) nên nó soi PENDING PARENT record, trong khi _result_for_record lại đi tiếp xuống child approved decision (:818-826) và trả applied=True kèm run của child — guard và result-resolution nhìn vào hai record khác nhau, guard bị vô hiệu hoàn toàn
- [ ] reviewer tái hiện bằng probe thật: supervised dispatch to approve to run terminal to replay cùng key trả applied=True với run success/timeout/cancelled, không tạo run mới — ĐÚNG lỗi kẹt im lặng mà task này sinh ra để đóng, vẫn còn sống
- [ ] Nguyên nhân lọt lưới: TẤT CẢ test staleness hiện có đều dùng mode=bypass nên xanh giả
- [ ] Fix nhỏ: resolve pending to child record TRƯỚC khi check status, mirror đúng _result_for_record, và parametrize hai test staleness thêm mode supervised
- [ ] Secondary: test_command_key_truncation_preserves_attempt_discriminator bị chèn VÀO TRONG thân test_command_router_parse (test_command_router.py:32) nên dòng 48-56 (assertion /help và unknown-command) nay nằm trong thân test mới — assertion vẫn chạy, không mất coverage, nhưng cả hai test đều sai tên so với thứ chúng kiểm

## Causal Analysis
- **Root cause**: Toàn bộ test staleness chỉ chạy mode=bypass, nên guard hỏng ở mode supervised xanh giả qua 2 vòng review — bug không khó, chỉ là chưa từng được test ở nhánh có nó
- **Mechanism**: _reject_if_stale_dispatch_record early-return khi record.status != approved nên soi PENDING PARENT record, trong khi _result_for_record đi tiếp xuống child approved decision và trả applied=True kèm run của child; hai bên nhìn vào hai record khác nhau nên guard bị vô hiệu hoàn toàn ở supervised
- **Counterfactual**: Nếu test staleness được parametrize qua cả bypass lẫn supervised ngay từ vòng 1 thì lỗi lộ ra ở vòng đầu, không mất 3 vòng review và 2 lần đổi executor
- **Pattern**: [[vacuous-acceptance-test]]
