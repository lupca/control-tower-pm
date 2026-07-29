---
id: CTV2-090
title: "Nối MCPClient/GraphClient vào registry (group research) — coordinator hết mù source code"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: high
risk: normal
deadline: null
executor: "@claude-sonnet-medium"
reviewer: "@claude-opus"
result_ref: "0e2bfbd"
depends_on: []
files:
  - backend/app/services/tool_registry.py
  - backend/app/services/command_router.py
  - backend/app/services/graph_client.py
  - backend/app/services/mcp.py
flows: []
tests:
  - backend/tests/test_mcp.py
  - backend/tests/test_graph_client_compression.py
  - backend/tests/test_tool_registry.py
  - backend/tests/test_command_router.py
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: high
prediction_factors:
  score: 0.8
  deductions:
    - "hub node: execute_tool (36) (-0.2)"
created: 2026-07-27
updated: 2026-07-27
rejections: 1
---

# CTV2-090: Research tools — nối dây code-review-graph vào coordinator

> Dự án: [[projects/control-tower-v2/control-tower-v2]]
> Nguồn: `docs/research/autonomous-coordination-gap-analysis.md` §5.2 (G11), lộ trình #3b

`MCPClient` và `GraphClient` chỉ được export trong `services/__init__.py`, **không được gọi từ bất kỳ đâu trong runtime path**. Toàn bộ tích hợp code-review-graph (CTV2-005) và Headroom compression (CTV2-065) đang là dead code. Đây là chi phí thấp nhất trên mỗi đơn vị chất lượng: hạ tầng đã trả tiền xây, chỉ thiếu dây.

## Tiêu chí nghiệm thu (AC)

- [ ] Group `research` trong registry với ít nhất `get_minimal_context` và `get_impact_radius`, tier deferred (nạp qua `load_tools`)
- [ ] Handler gọi `GraphClient`/`MCPClient` thật, luôn truyền `repo_root` tuyệt đối lấy từ `Project.repo_root` — không auto-detect theo cwd của backend
- [ ] Graph chưa build / MCP lỗi → trả lỗi có cấu trúc để LLM biết đường xử lý, KHÔNG trả rỗng giả vờ thành công
- [ ] Kết quả đi qua compression hiện có trước khi vào context (không bịa thêm lớp nén mới)
- [ ] Tool read-only: không có đường nào ghi/refactor code từ coordinator

## Verification

- `pytest backend/tests/test_mcp.py backend/tests/test_graph_client_compression.py backend/tests/test_tool_registry.py -v` → xanh
- Test: `load_tools(group="research")` → schema xuất hiện; gọi `get_impact_radius` với project có repo_root thật → trả file list; với repo không có graph → lỗi có cấu trúc
- `grep -rn "GraphClient\|MCPClient" backend/app --include=*.py | grep -v "services/__init__"` → có call site trong runtime path

## Plan

1. Thêm group `research` vào registry với `get_minimal_context` và `get_impact_radius`, tier deferred (nạp qua `load_tools`).
2. Handler mỏng gọi `GraphClient`/`MCPClient` đã có — không viết lại client, không thêm lớp nén mới (dùng `compress_for_prompt` sẵn có).
3. `repo_root` resolve từ `Project.repo_root` của task/session, truyền tuyệt đối; không để MCP auto-detect theo cwd của backend.
4. Error path: graph chưa build / MCP timeout → trả payload lỗi có cấu trúc (`status`, `reason`, gợi ý build) để LLM xử lý được; cấm trả list rỗng như thể thành công.
5. Tests: `load_tools(group="research")` lộ schema; call thật trên repo có graph; call trên repo không graph → lỗi có cấu trúc; grep khẳng định client đã nằm trên runtime path.

## Sub-tasks

- [ ] Registry entries group `research`
- [ ] Handlers + resolve repo_root từ Project
- [ ] Error path có cấu trúc
- [ ] Tests per AC

## Findings từ reviewer
- [x] Missing tests: test_mcp.py, test_graph_client_compression.py, test_tool_registry.py, test_command_router.py need tests for research group tools — addressed in 0e2bfbd (80 tests pass)
