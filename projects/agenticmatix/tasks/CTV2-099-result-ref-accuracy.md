---
id: CTV2-099
title: "result_ref chính xác: so HEAD trước/sau run, chặn verdict trên diff rỗng"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: high
risk: normal
deadline: null
executor: "@claude-sonnet-medium"
reviewer: "@claude-opus"
result_ref: "6575ba4"
depends_on: []
files:
  - backend/app/services/task_orchestration.py
  - backend/app/workers/agent_runner.py
flows: []
tests:
  - backend/tests/unit/test_agent_runner.py
  - backend/tests/test_task_orchestration.py
  - backend/tests/integration/test_dispatch_flow.py
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: high
prediction_factors:
  score: 0.75
  deductions:
    - "hub node: run_agent (53) (-0.2)"
    - "phạm vi nhỏ, logic rõ ràng (-0.05)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-099: Chặn một lớp verdict giả

> Dự án: [[projects/control-tower-v2/control-tower-v2]]
> Nguồn: `docs/research/autonomous-coordination-gap-analysis.md` §2 (G4), lộ trình #9

> **Là prerequisite của CTV2-087**, không phải việc dọn dẹp làm sau: review run cần cặp `base..head` do task này sinh ra. Chạy 087 trước sẽ khiến review run đầu tiên diff sai phạm vi (hoặc diff rỗng vì executor không commit) → "không thấy gì sai" → verdict pass giả ngay lần tự chủ đầu tiên.

`_parse_result_ref` chạy `git rev-parse HEAD` sau khi CLI kết thúc. Executor không commit ⇒ trả về commit cũ (thường chính là baseline) ⇒ review diff nhầm phạm vi và có thể pass một task **chưa hề có code**.

## Tiêu chí nghiệm thu (AC)

- [ ] Ghi lại HEAD **trước** khi spawn run và HEAD **sau** khi run kết thúc; `result_ref` mang cả base và head
- [ ] HEAD không đổi và không có commit mới → run không được ghi `execution_success` mặc nhiên; đánh dấu "không có thay đổi" và chuyển sang đường xử lý lỗi/escalate
- [ ] Executor báo result-ref tường minh (nếu có) thì ưu tiên giá trị đó, nhưng vẫn phải nằm trong khoảng base..head thực tế
- [ ] Review run (CTV2-087) dùng đúng cặp base/head này để giới hạn diff
- [ ] Có xử lý cho repo bẩn (uncommitted changes) — không im lặng bỏ qua

## Verification

- `pytest backend/tests/unit/test_agent_runner.py backend/tests/integration/test_dispatch_flow.py -v` → xanh
- Test: giả lập run không commit → task KHÔNG chuyển `awaiting-review` với result_ref = baseline
- Test: run có commit → result_ref chứa base + head đúng

## Plan

1. Ghi `base_ref` = `git rev-parse HEAD` **trước** khi spawn run, lưu trên `AgentRun`.
2. Sau run: đọc HEAD mới; `result_ref` mang cặp `base..head`.
3. `head == base` và không có commit mới → không ghi `execution_success` mặc nhiên; đánh dấu "no changes" và đi đường escalate/retry theo policy.
4. Executor báo result-ref tường minh thì ưu tiên, nhưng validate nó nằm trong `base..head` thực tế.
5. Truyền cặp base/head sang review run (CTV2-087) để giới hạn diff; xử lý repo bẩn (uncommitted) bằng cảnh báo rõ, không im lặng.
6. Tests: run không commit; run có commit; executor báo ref ngoài range.

## Sub-tasks

- [ ] Ghi HEAD trước run
- [ ] So sánh sau run + đường xử lý "không có thay đổi"
- [ ] Truyền base/head cho review run
- [ ] Tests per AC
