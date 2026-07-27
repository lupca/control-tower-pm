---
id: CTV2-087
title: "request_review tool + Review Run thật (/code-review) + chặn coordinator tự ký verdict"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: urgent
risk: high
deadline: null
executor: "@claude-sonnet-medium"
reviewer: "@claude-opus"
result_ref: "dc0145e"
depends_on:
  - CTV2-086
  - CTV2-099
  - CTV2-102
files:
  - backend/app/services/tool_registry.py
  - backend/app/services/command_router.py
  - backend/app/services/task_orchestration.py
  - backend/app/services/command_builder.py
  - backend/app/workers/agent_runner.py
flows: []
tests:
  - backend/tests/test_command_router.py
  - backend/tests/test_task_orchestration.py
  - backend/tests/unit/test_command_builder.py
  - backend/tests/integration/test_dispatch_flow.py
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: medium
prediction_factors:
  score: 0.6
  deductions:
    - "hub node: run_agent (53), execute_tool (36), TaskOrchestrationService (43) (-0.2)"
    - "phụ thuộc 3 task (086 schema, 099 base/head, 102 schema kết quả) (-0.2)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-087: request_review tool + Review Run + khoá quyền tự ký verdict

> Dự án: [[projects/control-tower-v2/control-tower-v2]]
> Nguồn: `docs/research/autonomous-coordination-gap-analysis.md` §1.1, §3.3, §5.1, lộ trình #1

Nối lại **chỗ đứt vật lý** của vòng đời: task xong execute nằm `awaiting-review` vĩnh viễn vì registry không có tool nào đưa nó đi tiếp (chỉ có `POST /api/tasks/{id}/review`).

## Tiêu chí nghiệm thu (AC)

- [x] Tool `request_review(task_id, reviewer?)` có trong `TOOL_REGISTRY`, group `task_lifecycle`, đi qua gate `review_order`
- [x] Reviewer được chọn tự động (AgentMatcher) khi không truyền, luôn ≠ `task.executor`; không tìm được reviewer độc lập → trả lỗi rõ, không tự hạ chuẩn
- [x] Tạo `AgentRun(kind=review)` và spawn CLI chạy `/code-review` trong `repo_root`, phạm vi diff `--from <base> --to <head>` lấy từ cặp base/head do CTV2-099 ghi — KHÔNG tự suy ra base
- [x] Review run **ghi structured output ra file JSON** theo schema đã chốt ở CTV2-102; task này chỉ đọc file đúng schema, không parse text tự do
- [x] File kết quả thiếu/sai schema → task về trạng thái cần người xử lý, KHÔNG mặc định pass
- [x] `record_verdict` bị chặn khi không tồn tại review run terminal tương ứng — coordinator không còn ký verdict thay reviewer (`actor` lấy từ review run, không phải `task.reviewer` do LLM truyền)
- [x] Đường REST `POST /api/tasks/{id}/review` vẫn hoạt động cho người dùng ký tay

## Verification

- `pytest backend/tests/test_command_router.py backend/tests/test_task_orchestration.py backend/tests/integration/test_dispatch_flow.py -v` → xanh
- Test: task `awaiting-review` → `request_review` → status `in-review` + AgentRun `kind=review` tồn tại
- Test: gọi `record_verdict` khi chưa có review run → bị từ chối
- Test: reviewer == executor → từ chối

## Plan

1. Đăng ký `request_review` vào `TOOL_REGISTRY` (group `task_lifecycle`, gate `review_order`) + handler ở `command_router`, đi qua `TaskOrchestrationService.request_review` sẵn có.
2. Chọn reviewer: gọi AgentMatcher với ràng buộc `!= task.executor`; không có ứng viên → trả lỗi có cấu trúc, không tự hạ chuẩn.
3. Review run: `command_builder` dựng lệnh `/code-review --from <base> --to <result_ref>` trong `repo_root`; `agent_runner` phân nhánh theo `AgentRun.kind` (CTV2-086) để chọn command builder và post-processing.
4. Đọc file JSON kết quả (schema từ CTV2-102) → `ac_results`. Validate schema; thiếu/sai → không suy diễn pass, đưa task sang đường cần người xử lý.
5. Khoá tự ký: `record_verdict` yêu cầu tồn tại review run terminal cho task; `actor` lấy từ run đó, bỏ fallback `f"chat:{session_id}"`. REST ký tay vẫn giữ đường riêng.
6. Tests theo từng AC, gồm cả test khẳng định coordinator không ký được verdict.

## Sub-tasks

- [ ] `request_review` trong registry + handler ở command_router
- [ ] Chọn reviewer qua AgentMatcher + four-eyes guard
- [ ] Review run: command_builder dựng lệnh `/code-review`, agent_runner phân nhánh theo `kind`
- [ ] Đọc + validate file kết quả JSON (schema CTV2-102)
- [ ] Guard `record_verdict` phải có review run
- [ ] Tests per AC
