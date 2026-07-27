---
id: CTV2-090
task_path: projects/control-tower-v2/tasks/CTV2-090-research-tools-graph-mcp-wiring.md
project: control-tower-v2
result_ref: 0e2bfbd
executor: @claude-sonnet-medium
reviewer: @claude-opus
status: completed
issued: 2026-07-27
verdict: pass
verdict_date: 2026-07-27
---

# Phiếu Review: CTV2-090 — Nối MCPClient/GraphClient vào registry (group research) — coordinator hết mù source code

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-090-research-tools-graph-mcp-wiring.md`
- Result-ref: 0e2bfbd
- Executor: @claude-sonnet-medium
- Reviewer: @claude-opus
- Ngày phát phiếu: 2026-07-27

## Acceptance Criteria cần verify
## Tiêu chí nghiệm thu (AC)

- [x] Group `research` trong registry với ít nhất `get_minimal_context` và `get_impact_radius`, tier deferred (nạp qua `load_tools`)
- [x] Handler gọi `GraphClient`/`MCPClient` thật, luôn truyền `repo_root` tuyệt đối lấy từ `Project.repo_root` — không auto-detect theo cwd của backend
- [x] Graph chưa build / MCP lỗi → trả lỗi có cấu trúc để LLM biết đường xử lý, KHÔNG trả rỗng giả vờ thành công
- [x] Kết quả đi qua compression hiện có trước khi vào context (không bịa thêm lớp nén mới)
- [x] Tool read-only: không có đường nào ghi/refactor code từ coordinator

## Definition of Done (AGENTS.md mục 3)
- [x] Toàn bộ AC pass
- [x] Test liên quan xanh 100%: backend/tests/test_mcp.py, backend/tests/test_graph_client_compression.py, backend/tests/test_tool_registry.py, backend/tests/test_command_router.py (80 passed)
- [x] Không regression (test khác trong module vẫn xanh)
- [x] Reviewer khác executor (xác nhận reviewer @claude-opus ≠ executor @claude-sonnet-medium)

## Test gợi ý chạy trong repo code
- `backend/tests/test_mcp.py`
- `backend/tests/test_graph_client_compression.py`
- `backend/tests/test_tool_registry.py`
- `backend/tests/test_command_router.py`

## Câu hỏi rủi ro (từ code-review-graph, tĩnh — không thay thế việc tự đọc diff)
- *(LLM/coordinator bổ sung từ graph nếu có; script không đọc diff và không gọi graph.)*

## Review Toolchain
Chạy theo toolchain của repo đích; preflight các tool đã đăng ký trước khi review.

## Trả kết quả
`/verdict CTV2-090 <pass|changes> --reviewer @claude-opus [--commit <hash>] [--notes "..."]`

## Review Notes (2026-07-27)

**Verdict: PASS**

Implementation correctly wires `GraphClient`/`MCPClient` into runtime via:
- `_research_repo_root()` resolves absolute path from `Project.repo_root` (not cwd)
- `_research_error()` returns structured payload with `status`, `reason`, `detail`, `suggestion`
- Handlers pass `compress_output=True` → uses existing `compress_for_prompt`
- Both tools have `permission="read"`, `tier="deferred"`, `group="research"`

Test coverage comprehensive: 80 tests pass including new research group tests for repo_root resolution, structured error path, and compression.
