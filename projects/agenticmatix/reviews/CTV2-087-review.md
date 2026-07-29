---
id: CTV2-087
task_path: projects/control-tower-v2/tasks/CTV2-087-request-review-tool-review-run.md
project: control-tower-v2
result_ref: dc0145e
executor: @claude-sonnet-medium
reviewer: "@claude-opus"
status: passed
issued: 2026-07-27
verdict: pass
verdict_date: 2026-07-27
---

# Phiếu Review: CTV2-087 — request_review tool + Review Run thật (/code-review) + chặn coordinator tự ký verdict

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-087-request-review-tool-review-run.md`
- Result-ref: dc0145e
- Executor: @claude-sonnet-medium
- Reviewer: @claude-opus
- Ngày phát phiếu: 2026-07-27

## Acceptance Criteria cần verify
## Tiêu chí nghiệm thu (AC)

- [ ] Tool `request_review(task_id, reviewer?)` có trong `TOOL_REGISTRY`, group `task_lifecycle`, đi qua gate `review_order`
- [ ] Reviewer được chọn tự động (AgentMatcher) khi không truyền, luôn ≠ `task.executor`; không tìm được reviewer độc lập → trả lỗi rõ, không tự hạ chuẩn
- [ ] Tạo `AgentRun(kind=review)` và spawn CLI chạy `/code-review` trong `repo_root`, phạm vi diff `--from <base> --to <head>` lấy từ cặp base/head do CTV2-099 ghi — KHÔNG tự suy ra base
- [ ] Review run **ghi structured output ra file JSON** theo schema đã chốt ở CTV2-102; task này chỉ đọc file đúng schema, không parse text tự do
- [ ] File kết quả thiếu/sai schema → task về trạng thái cần người xử lý, KHÔNG mặc định pass
- [ ] `record_verdict` bị chặn khi không tồn tại review run terminal tương ứng — coordinator không còn ký verdict thay reviewer (`actor` lấy từ review run, không phải `task.reviewer` do LLM truyền)
- [ ] Đường REST `POST /api/tasks/{id}/review` vẫn hoạt động cho người dùng ký tay

## Definition of Done (AGENTS.md mục 3)
- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: backend/tests/test_command_router.py, backend/tests/test_task_orchestration.py, backend/tests/unit/test_command_builder.py, backend/tests/integration/test_dispatch_flow.py
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (xác nhận reviewer @claude-opus ≠ executor @claude-sonnet-medium)

## Test gợi ý chạy trong repo code
- `backend/tests/test_command_router.py`
- `backend/tests/test_task_orchestration.py`
- `backend/tests/unit/test_command_builder.py`
- `backend/tests/integration/test_dispatch_flow.py`

## Câu hỏi rủi ro (từ code-review-graph, tĩnh — không thay thế việc tự đọc diff)
- *(LLM/coordinator bổ sung từ graph nếu có; script không đọc diff và không gọi graph.)*

## Review Toolchain
Chạy theo toolchain của repo đích; preflight các tool đã đăng ký trước khi review.

## Trả kết quả
`/verdict CTV2-087 <pass|changes> --reviewer @claude-opus [--commit <hash>] [--notes "..."]`
