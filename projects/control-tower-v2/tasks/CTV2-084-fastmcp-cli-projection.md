---
id: CTV2-084
title: "FastMCP projection: CT tools cho coordinator chat CLI (không đụng executor dispatch CLI)"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: medium
risk: normal
deadline: null
executor: "@claude-sonnet-medium"
reviewer: "@claude-opus"
result_ref: "45a4bfa"
depends_on:
  - CTV2-082
files:
  - backend/app/mcp_server.py
  - backend/app/services/tool_registry.py
  - backend/app/services/cli_dispatcher.py
flows: []
tests:
  - backend/tests/test_mcp_server.py
  - backend/tests/test_cli_coordinator.py
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: medium
prediction_factors:
  score: 0.75
  deductions:
    - "tích hợp MCP config cho 3 CLI khác nhau (claude/codex/agy) (-0.15)"
    - "cần scoped API token mới (-0.1)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-084: FastMCP Projection cho Coordinator Chat CLI (ADR-001 Phase 3)

> Dự án: [[projects/control-tower-v2/control-tower-v2]]
> Thiết kế: `docs/adr/ADR-001-unified-tool-architecture.md` §D5

## Phạm vi — 2 loại CLI, chỉ loại (2) trong scope

1. **Executor dispatch CLI** (`agent_runner` chạy CLI trong target repo để viết code): GIỮ NGUYÊN — dùng built-in tools của CLI, không nhận CT CRUD tools, contract vẫn là "làm việc, trả result-ref".
2. **Coordinator chat CLI** (turn chat UI route sang CLI thay vì OpenAI API): hiện KHÔNG có CT tool nào (P4) — đây là đích của task này.

## Tiêu chí nghiệm thu (AC)

- [x] MCP stdio server (FastMCP, Python, cùng repo): `python -m app.mcp_server --api-url http://localhost:8000` expose toàn bộ tool từ registry (cùng canonical name, cùng schema)
- [x] Handlers gọi REST API với scoped token; permission/gate enforce server-side (CLI không thể bypass four-eyes)
- [x] MCP config mẫu cho claude / codex / agy được sinh ra + doc setup trong README
- [x] `cli_dispatcher` (đường coordinator chat) truyền MCP config vào CLI khi spawn (theo cơ chế từng CLI); đường `agent_runner` dispatch executor KHÔNG bị chạm
- [x] Tool gọi qua MCP và qua API mode cho kết quả DB giống nhau (parity test)

## Verification

- `pytest backend/tests/test_mcp_server.py backend/tests/test_cli_coordinator.py -v` → xanh
- Manual/E2E: 1 turn chat CLI gọi `create_task` qua MCP → task xuất hiện trong DB với audit log
- `git diff backend/app/workers/agent_runner.py` → rỗng (out of scope)

## Plan

1. `app/mcp_server.py`: FastMCP, iterate registry → register tools, handler = HTTP call.
2. Scoped API token (env/DB) + middleware check.
3. Config generation + wiring vào coordinator CLI spawn path.
4. Parity + E2E tests (theo quy ước E2E-over-browser).

## Sub-tasks

- [ ] FastMCP server từ registry
- [ ] Scoped token + server-side enforcement
- [ ] CLI config wiring (chat path only)
- [ ] Parity/E2E tests
