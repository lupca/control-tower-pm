---
id: CTV2-105
task_path: projects/control-tower-v2/tasks/CTV2-105-git-worktree-per-dispatch.md
project: control-tower-v2
result_ref: 051cb61
executor: @claude-sonnet-medium
reviewer: "@claude-opus"
status: passed
issued: 2026-07-27
verdict: pass
verdict_date: 2026-07-27
---

# Phiếu Review: CTV2-105 — Git worktree riêng cho mỗi dispatch — gỡ ràng buộc tuần tự của một working tree

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-105-git-worktree-per-dispatch.md`
- Result-ref: 051cb61
- Executor: @claude-sonnet-medium
- Reviewer: @claude-opus
- Ngày phát phiếu: 2026-07-27

## Acceptance Criteria cần verify
## Tiêu chí nghiệm thu (AC)

- [ ] Mỗi `AgentRun` chạy trong `git worktree` riêng, tạo từ commit base xác định; hai run đồng thời trên cùng repo KHÔNG chạm chung `.git/index.lock`
- [ ] Commit của executor nằm trên worktree của nó; `result_ref` trả về là commit **trong** worktree đó, và điều hoà được về repo chính (merge/cherry-pick hoặc branch riêng) — nêu rõ chiến lược đã chọn trong Plan
- [ ] Worktree được **dọn sau khi run kết thúc**, kể cả khi run `failed`/`timeout`/`cancelled`; không để worktree mồ côi tích tụ
- [ ] Run bị hủy giữa chừng không để lại lock hay worktree treo — có test cho đường hủy
- [ ] Reviewer đọc đúng phạm vi diff của run mình review, không bị lẫn commit của run song song
- [ ] Test đồng thời: 2 executor chạy song song trên cùng repo, mỗi bên commit, cả hai `result_ref` đều hợp lệ và không mất commit nào
- [ ] Có đường tắt: repo không hỗ trợ worktree (hoặc cấu hình tắt) → rơi về chế độ tuần tự hiện tại **có log rõ**, không im lặng

## Definition of Done (AGENTS.md mục 3)
- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: backend/tests/unit/test_agent_runner.py, backend/tests/unit/test_command_builder.py, backend/tests/unit/test_process_manager.py, backend/tests/integration/test_dispatch_flow.py
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (xác nhận reviewer @claude-opus ≠ executor @claude-sonnet-medium)

## Test gợi ý chạy trong repo code
- `backend/tests/unit/test_agent_runner.py`
- `backend/tests/unit/test_command_builder.py`
- `backend/tests/unit/test_process_manager.py`
- `backend/tests/integration/test_dispatch_flow.py`

## Câu hỏi rủi ro (từ code-review-graph, tĩnh — không thay thế việc tự đọc diff)
- *(LLM/coordinator bổ sung từ graph nếu có; script không đọc diff và không gọi graph.)*

## Review Toolchain
Chạy theo toolchain của repo đích; preflight các tool đã đăng ký trước khi review.

## Trả kết quả
`/verdict CTV2-105 <pass|changes> --reviewer @claude-opus [--commit <hash>] [--notes "..."]`
