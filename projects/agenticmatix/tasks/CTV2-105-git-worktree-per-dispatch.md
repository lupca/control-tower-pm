---
id: CTV2-105
title: "Git worktree riêng cho mỗi dispatch — gỡ ràng buộc tuần tự của một working tree"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: high
risk: high
deadline: null
executor: "@claude-sonnet-medium"
reviewer: "@claude-opus"
result_ref: "051cb61"
depends_on: []
files:
  - backend/app/services/cli_dispatcher.py
  - backend/app/services/command_builder.py
  - backend/app/workers/agent_runner.py
  - backend/app/services/process_manager.py
flows: []
tests:
  - backend/tests/unit/test_agent_runner.py
  - backend/tests/unit/test_command_builder.py
  - backend/tests/unit/test_process_manager.py
  - backend/tests/integration/test_dispatch_flow.py
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: medium
prediction_factors:
  score: 0.6
  deductions:
    - "hub node: run_agent (53), ProcessManager (47), run_with_streaming (69) (-0.2)"
    - "đụng vòng đời git bên ngoài process — dọn dẹp và lỗi phần dở là điểm dễ vỡ (-0.2)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-105: Một worktree cho mỗi dispatch

> Dự án: [[projects/control-tower-v2/control-tower-v2]]
> User duyệt 2026-07-27. Nguồn: ràng buộc quan sát được khi chạy wave 1 (xem `docs/handoff-2026-07-27-autonomous-coordination.md` §6.1)

## Bối cảnh — bằng chứng từ vận hành thật

Wave 1 gồm các task `depends_on` rỗng, lẽ ra chạy song song. Thực tế **phải tuần tự hoàn toàn**, vì mọi agent dùng chung một working tree:

- Hai executor commit đồng thời → đua `.git/index.lock`.
- Executor commit trong lúc reviewer chạy test → HEAD dịch chuyển giữa lượt review → verdict có thể sai.
- Batch A (3 task) chạy được song song **chỉ vì** chúng tình cờ không đụng file nhau, và điều đó phải tính tay bằng ma trận chồng lấn trước khi spawn.

Ràng buộc này đã chặn điều phối **4 lần trong một phiên**. Với Orchestration Driver (CTV2-089) chạy tự chủ, nó sẽ thành nút thắt cứng: driver không thể đẩy hai task cùng lúc dù chúng độc lập hoàn toàn.

## Tiêu chí nghiệm thu (AC)

- [x] Mỗi `AgentRun` chạy trong `git worktree` riêng, tạo từ commit base xác định; hai run đồng thời trên cùng repo KHÔNG chạm chung `.git/index.lock`
- [x] Commit của executor nằm trên worktree của nó; `result_ref` trả về là commit **trong** worktree đó, và điều hoà được về repo chính (merge/cherry-pick hoặc branch riêng) — nêu rõ chiến lược đã chọn trong Plan
- [x] Worktree được **dọn sau khi run kết thúc**, kể cả khi run `failed`/`timeout`/`cancelled`; không để worktree mồ côi tích tụ
- [x] Run bị hủy giữa chừng không để lại lock hay worktree treo — có test cho đường hủy
- [x] Reviewer đọc đúng phạm vi diff của run mình review, không bị lẫn commit của run song song
- [x] Test đồng thời: 2 executor chạy song song trên cùng repo, mỗi bên commit, cả hai `result_ref` đều hợp lệ và không mất commit nào
- [x] Có đường tắt: repo không hỗ trợ worktree (hoặc cấu hình tắt) → rơi về chế độ tuần tự hiện tại **có log rõ**, không im lặng

## Verification

- `pytest backend/tests/unit/test_agent_runner.py backend/tests/integration/test_dispatch_flow.py -v` → xanh
- Test đồng thời thật: spawn 2 run song song trên cùng repo → `git worktree list` cho 2 entry trong lúc chạy, 0 entry sau khi xong
- Sau một run `failed`: `git worktree list` không còn entry mồ côi; `.git/index.lock` không tồn tại
- `git log --all` sau 2 run song song: đủ cả 2 commit, không mất

## Plan

*(điền ở Plan Gate)*

## Sub-tasks

- [ ] Tạo/huỷ worktree quanh vòng đời `AgentRun`
- [ ] Chiến lược điều hoà commit về repo chính
- [ ] Dọn dẹp cho mọi đường kết thúc (success/failed/timeout/cancelled)
- [ ] Fallback tuần tự có log khi worktree không dùng được
- [ ] Test đồng thời + test đường hủy
