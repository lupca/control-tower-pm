---
id: CTV2-091
title: "Spec/Plan step thật: sinh AC + plan + files/tests từ graph, siết verdict theo số AC"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: urgent
risk: high
deadline: null
executor: "@claude-sonnet-medium"
reviewer: "@claude-opus"
result_ref: "9015407"
depends_on:
  - CTV2-090
files:
  - backend/app/services/command_router.py
  - backend/app/services/task_orchestration.py
  - backend/app/services/coordinator.py
  - backend/app/db/models.py
flows: []
tests:
  - backend/tests/test_command_router.py
  - backend/tests/test_task_orchestration.py
  - backend/tests/test_gates.py
  - backend/tests/integration/test_full_flow.py
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: medium
prediction_factors:
  score: 0.55
  deductions:
    - "hub node: Task (127), CoordinatorService (43), TaskOrchestrationService (43) (-0.2)"
    - "siết verdict có thể chặn task cũ đang chạy — cần đường di trú (-0.25)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-091: Spec/Plan step + chặn cửa fake-done

> Dự án: [[projects/control-tower-v2/control-tower-v2]]
> Nguồn: `docs/research/autonomous-coordination-gap-analysis.md` §2 (G2), §3.2, lộ trình #3

**Đòn bẩy chất lượng lớn nhất, hiện đang trống hoàn toàn.** `_handle_create_task` tạo `Task(id, title, project, status='todo')` — không AC, không plan, không files, không tests. Executor nhận task chỉ có title. Đồng thời `_validate_verdict_prerequisites` dùng `max(1, len(acceptance_criteria))` nên AC rỗng ⇒ chỉ cần 1 kết quả là verdict pass hợp lệ ⇒ cửa fake-done mở toang.

## Tiêu chí nghiệm thu (AC)

- [x] Một LLM call sinh đủ `acceptance_criteria[]`, `plan`, `files[]`, `tests[]`, `risk` và ghi thẳng vào DB (không phải stub, không phải chỉ log)
- [x] `files[]`/`flows[]` lấy từ research tools (CTV2-090) — có bằng chứng call graph trong bản ghi; LLM không được tự bịa đường dẫn
- [x] Task không có AC thì **không được vào dispatch** (chặn ở service layer, không chỉ ở prompt)
- [x] `_validate_verdict_prerequisites`: bỏ `max(1, ...)`; verdict `pass` yêu cầu đủ số kết quả bằng số AC, thiếu một AC → không pass
- [x] Task cũ đang dở dang có đường di trú rõ ràng (backfill hoặc cờ legacy), không làm kẹt backlog hiện có
- [x] Spec/Plan là gate thật ở tầng dữ liệu, nhất quán với `GATED_ACTIONS`

## Verification

- `pytest backend/tests/test_gates.py backend/tests/test_task_orchestration.py backend/tests/integration/test_full_flow.py -v` → xanh
- Test: `create_task` → task có AC/plan/files/tests khác rỗng
- Test: dispatch task không AC → bị từ chối
- Test: verdict pass với 3 AC nhưng chỉ 2 ac_results → bị từ chối

## Plan

1. Spec/Plan step: một LLM call có tool `research` (CTV2-090) trong tay, output **structured** (`acceptance_criteria[]`, `plan`, `files[]`, `tests[]`, `risk`) — validate schema, retry khi lệch, ghi thẳng DB qua service layer.
2. `files[]`/`flows[]` bắt buộc kèm nguồn từ graph; giá trị LLM tự bịa mà graph không xác nhận thì đánh dấu `*(chưa xác nhận)*` thay vì ghi như sự thật.
3. Chặn dispatch khi `acceptance_criteria` rỗng — kiểm ở `TaskOrchestrationService`, không chỉ ở prompt.
4. `_validate_verdict_prerequisites`: bỏ `max(1, ...)`, yêu cầu `len(ac_results) == len(acceptance_criteria)` và mọi AC có kết luận. Thêm test cho đúng lỗ hổng fake-done.
5. Di trú task cũ: cờ `legacy_no_ac` (hoặc backfill AC từ title) để backlog đang chạy không bị kẹt; ghi rõ task nào được miễn.
6. Đồng bộ `GATED_ACTIONS` để spec/plan là gate thật ở tầng dữ liệu.

## Sub-tasks

- [x] Spec/Plan step gọi LLM + research tools, ghi DB
- [x] Chặn dispatch khi thiếu AC
- [x] Siết `_validate_verdict_prerequisites`
- [x] Đường di trú cho task cũ
- [x] Tests per AC
