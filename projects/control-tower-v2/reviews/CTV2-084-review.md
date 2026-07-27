---
id: CTV2-084
task_path: projects/control-tower-v2/tasks/CTV2-084-fastmcp-cli-projection.md
project: control-tower-v2
result_ref: 45a4bfa
executor: @claude-sonnet-medium
reviewer: "@claude-opus"
status: passed
issued: 2026-07-27
verdict: pass
verdict_date: 2026-07-27
---

# Phiếu Review: CTV2-084 — FastMCP projection: CT tools cho coordinator chat CLI (không đụng executor dispatch CLI)

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-084-fastmcp-cli-projection.md`
- Result-ref: 45a4bfa
- Executor: @claude-sonnet-medium
- Reviewer: @claude-opus
- Ngày phát phiếu: 2026-07-27

## Acceptance Criteria cần verify
## Tiêu chí nghiệm thu (AC)

- [ ] MCP stdio server (FastMCP, Python, cùng repo): `python -m app.mcp_server --api-url http://localhost:8000` expose toàn bộ tool từ registry (cùng canonical name, cùng schema)
- [ ] Handlers gọi REST API với scoped token; permission/gate enforce server-side (CLI không thể bypass four-eyes)
- [ ] MCP config mẫu cho claude / codex / agy được sinh ra + doc setup trong README
- [ ] `cli_dispatcher` (đường coordinator chat) truyền MCP config vào CLI khi spawn (theo cơ chế từng CLI); đường `agent_runner` dispatch executor KHÔNG bị chạm
- [ ] Tool gọi qua MCP và qua API mode cho kết quả DB giống nhau (parity test)

## Definition of Done (AGENTS.md mục 3)
- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: backend/tests/test_mcp_server.py, backend/tests/test_cli_coordinator.py
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (xác nhận reviewer @claude-opus ≠ executor @claude-sonnet-medium)

## Test gợi ý chạy trong repo code
- `backend/tests/test_mcp_server.py`
- `backend/tests/test_cli_coordinator.py`

## Câu hỏi rủi ro (từ code-review-graph, tĩnh — không thay thế việc tự đọc diff)
- *(LLM/coordinator bổ sung từ graph nếu có; script không đọc diff và không gọi graph.)*

## Review Toolchain
Chạy theo toolchain của repo đích; preflight các tool đã đăng ký trước khi review.

## Trả kết quả
`/verdict CTV2-084 <pass|changes> --reviewer @claude-opus [--commit <hash>] [--notes "..."]`
