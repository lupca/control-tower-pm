---
id: CTV2-079
task_path: projects/control-tower-v2/tasks/CTV2-079-remove-legacy-sdk-adapters.md
project: control-tower-v2
result_ref: 3e1936a
executor: @claude-sonnet-medium
reviewer: "@claude-opus"
status: passed
issued: 2026-07-27
verdict: pass
verdict_date: 2026-07-27
---

# Phiếu Review: CTV2-079 — Xoá legacy SDK adapters (Anthropic/Google) + compatibility seam

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-079-remove-legacy-sdk-adapters.md`
- Result-ref: 3e1936a
- Executor: @claude-sonnet-medium
- Reviewer: @claude-opus
- Ngày phát phiếu: 2026-07-27

## Acceptance Criteria cần verify
## Tiêu chí nghiệm thu (AC)

- [ ] Xoá `providers/anthropic_adapter.py`, `providers/google_adapter.py`
- [ ] `ProviderRouter` chỉ resolve OpenAIAdapter (từ Agent DB record); anthropic/google model → luôn đi đường CLI qua `route_model`
- [ ] Xoá seam `_explicit_provider_compatibility` và nhánh legacy trong `_resolve_selection`
- [ ] `DEFAULT_CONTEXT_WINDOWS` bổ sung entry mặc định cho OpenAI-compatible models (không rơi về min ngầm định)
- [ ] Không còn import `anthropic`/`google.genai` SDK trong backend (trừ requirements nếu CLI cần — kiểm tra và dọn requirements.txt)

## Definition of Done (AGENTS.md mục 3)
- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: backend/tests/test_providers.py, backend/tests/test_coordinator.py, backend/tests/test_cli_coordinator.py
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (xác nhận reviewer @claude-opus ≠ executor @claude-sonnet-medium)

## Test gợi ý chạy trong repo code
- `backend/tests/test_providers.py`
- `backend/tests/test_coordinator.py`
- `backend/tests/test_cli_coordinator.py`

## Câu hỏi rủi ro (từ code-review-graph, tĩnh — không thay thế việc tự đọc diff)
- *(LLM/coordinator bổ sung từ graph nếu có; script không đọc diff và không gọi graph.)*

## Review Toolchain
Chạy theo toolchain của repo đích; preflight các tool đã đăng ký trước khi review.

## Trả kết quả
`/verdict CTV2-079 <pass|changes> --reviewer @claude-opus [--commit <hash>] [--notes "..."]`
