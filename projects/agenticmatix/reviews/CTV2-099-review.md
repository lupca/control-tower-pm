---
id: CTV2-099
task_path: projects/control-tower-v2/tasks/CTV2-099-result-ref-accuracy.md
project: control-tower-v2
result_ref: 6575ba4
executor: @claude-sonnet-medium
reviewer: @claude-opus
status: completed
issued: 2026-07-27
verdict: pass
verdict_date: 2026-07-27
---

# Phiếu Review: CTV2-099 — result_ref chính xác: so HEAD trước/sau run, chặn verdict trên diff rỗng

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-099-result-ref-accuracy.md`
- Result-ref: 6575ba4
- Executor: @claude-sonnet-medium
- Reviewer: @claude-opus
- Ngày phát phiếu: 2026-07-27

## Acceptance Criteria cần verify
## Tiêu chí nghiệm thu (AC)

- [x] Ghi lại HEAD **trước** khi spawn run và HEAD **sau** khi run kết thúc; `result_ref` mang cả base và head
- [x] HEAD không đổi và không có commit mới → run không được ghi `execution_success` mặc nhiên; đánh dấu "không có thay đổi" và chuyển sang đường xử lý lỗi/escalate
- [x] Executor báo result-ref tường minh (nếu có) thì ưu tiên giá trị đó, nhưng vẫn phải nằm trong khoảng base..head thực tế
- [x] Review run (CTV2-087) dùng đúng cặp base/head này để giới hạn diff
- [x] Có xử lý cho repo bẩn (uncommitted changes) — không im lặng bỏ qua

## Definition of Done (AGENTS.md mục 3)
- [x] Toàn bộ AC pass
- [x] Test liên quan xanh 100%: backend/tests/unit/test_agent_runner.py, backend/tests/test_task_orchestration.py, backend/tests/integration/test_dispatch_flow.py (56 passed)
- [x] Không regression (test khác trong module vẫn xanh)
- [x] Reviewer khác executor (xác nhận reviewer @claude-opus ≠ executor @claude-sonnet-medium)

## Test gợi ý chạy trong repo code
- `backend/tests/unit/test_agent_runner.py`
- `backend/tests/test_task_orchestration.py`
- `backend/tests/integration/test_dispatch_flow.py`

## Câu hỏi rủi ro (từ code-review-graph, tĩnh — không thay thế việc tự đọc diff)
- *(LLM/coordinator bổ sung từ graph nếu có; script không đọc diff và không gọi graph.)*

## Review Toolchain
Chạy theo toolchain của repo đích; preflight các tool đã đăng ký trước khi review.

## Trả kết quả
`/verdict CTV2-099 <pass|changes> --reviewer @claude-opus [--commit <hash>] [--notes "..."]`
