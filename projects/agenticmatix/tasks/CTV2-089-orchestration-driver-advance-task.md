---
id: CTV2-089
title: "Orchestration Driver: dramatiq actor advance_task (event-driven, 0 token)"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: urgent
risk: high
deadline: null
executor: "@claude-sonnet-medium"
reviewer: "@claude-opus"
result_ref: "b49f829"
depends_on:
  - CTV2-087
  - CTV2-088
  - CTV2-091
  - CTV2-103
files:
  - backend/app/workers/agent_runner.py
  - backend/app/services/task_orchestration.py
  - backend/app/services/agent_matcher.py
  - backend/app/api/dispatch.py
flows: []
tests:
  - backend/tests/unit/test_agent_runner.py
  - backend/tests/test_task_orchestration.py
  - backend/tests/integration/test_full_flow.py
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: medium
prediction_factors:
  score: 0.55
  deductions:
    - "hub node: run_agent (53), TaskOrchestrationService (43) (-0.2)"
    - "actor mới đẩy state machine — nguy cơ vòng lặp vô hạn nếu thiếu chặn (-0.25)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-089: Orchestration Driver `advance_task`

> Dự án: [[projects/control-tower-v2/control-tower-v2]]
> Nguồn: `docs/research/autonomous-coordination-gap-analysis.md` §2 (G1), §3.1, lộ trình #2

Trục chính của autonomy. Hiện toàn backend chỉ có **một** actor (`run_agent`); khi nó xong thì không ai được đánh thức. Driver là bánh đà: mọi bước máy móc chạy **0 token**, LLM chỉ được gọi ở 2–3 điểm cho cả vòng đời task.

## Tiêu chí nghiệm thu (AC)

- [x] Actor `advance_task(task_id, trigger)` thực thi bảng quyết định §3.1: `todo` (đủ AC) → chọn executor + dispatch; `awaiting-review` → chọn reviewer + `request_review`; `in-review` (review run xong) → `request_verdict`; `changes-requested` → replan trong hạn vòng; gate `pending` → dừng + thông báo
- [x] Event-driven, KHÔNG polling: `advance_task.send()` được kích hoạt sau `run_agent` kết thúc, sau khi gate được approve, sau khi review run xong, và sau verdict `changes`
- [x] Mọi chuyển trạng thái đi qua `TaskOrchestrationService` (FSM authoritative) — driver không tự set field trạng thái
- [x] Chặn vòng lặp: `advance_task` cho cùng task có trần số vòng và không tự gọi lại khi trạng thái không đổi; vượt trần → escalate cho user, không quay vòng im lặng
- [x] **Fail-closed khi thiếu AC**: task `todo` không có `acceptance_criteria` → driver **dừng và escalate**, tuyệt đối không dispatch. Có test khẳng định điều này ngay cả khi CTV2-091 chưa hoàn tất
- [x] Driver tôn trọng kill switch + trần chi phí của CTV2-103: autonomy tắt toàn cục → không đẩy task nào; chạm trần chi phí/số run đồng thời → dừng và báo
- [x] Gate `pending` → driver dừng đúng chỗ, không tự approve
- [x] Actor idempotent: gọi trùng cho cùng (task, trigger) không tạo run trùng

## Verification

- `pytest backend/tests/unit/test_agent_runner.py backend/tests/test_task_orchestration.py backend/tests/integration/test_full_flow.py -v` → xanh
- Test end-to-end (mode auto): tạo task đủ AC → chạy hết `dispatched → awaiting-review → in-review → done` mà không có lời gọi LLM coordinator nào ở các bước máy móc
- Test: trạng thái không tiến triển → driver dừng sau trần vòng, có bản ghi escalate

## Plan

1. Actor `advance_task(task_id, trigger)` trong `app/workers/`: đọc `(status, mode, risk, round)` dưới khoá, tra bảng quyết định §3.1, gọi `TaskOrchestrationService` — driver **không** tự set field trạng thái.
2. Gắn trigger: cuối `run_agent` (cả success và failure), sau khi gate được approve, sau khi review run kết thúc, sau verdict `changes`. Mỗi trigger chỉ `advance_task.send()`, không xử lý logic tại chỗ.
3. Chặn vòng: lưu `(task_id, status, round)` của lần chạy trước; trạng thái không đổi sau một vòng → không tự gọi lại, ghi escalate. Trần `auto_max_rounds` đọc tạm từ hằng số, sẽ chuyển sang policy ở CTV2-093.
4. Gate `pending` → dừng, để CTV2-098 lo thông báo (ở task này chỉ ghi log/audit). Nhánh `todo` thiếu AC → escalate, **không** rơi vào nhánh dispatch: automation dispatch task rỗng ở quy mô lớn là chế độ hỏng tệ nhất.
5. Kiểm kill switch + ngân sách (CTV2-103) ở đầu mỗi lần `advance_task` chạy, trước mọi quyết định khác.
6. Tests: end-to-end tự chạy hết vòng đời không cần LLM ở bước máy móc; test chặn vòng; test idempotent khi cùng trigger gửi 2 lần; test fail-closed task thiếu AC; test kill switch tắt.

## Sub-tasks

- [ ] Actor `advance_task` + bảng quyết định
- [ ] Trigger points (sau run_agent, sau approve gate, sau review run, sau verdict changes)
- [ ] Chặn vòng lặp + escalate
- [ ] Tests: end-to-end tự chạy + test chặn vòng
