---
id: CTV2-077
title: "Tool Registry: Single Source of Truth cho toàn bộ tool system"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: high
risk: normal
deadline: null
executor: "@claude-sonnet-medium"
reviewer: "@claude-opus"
result_ref: "46e2aee"
depends_on: []
files:
  - backend/app/services/tool_registry.py
  - backend/app/services/tool_definitions.py
  - backend/app/services/command_router.py
  - backend/app/api/chat.py
flows: []
tests:
  - backend/tests/test_command_router.py
  - backend/tests/test_coordinator.py
  - backend/tests/test_tool_registry.py
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: high
prediction_factors:
  score: 0.85
  deductions:
    - "refactor chạm nhiều call site (-0.1)"
    - "cần test mới cho registry (-0.05)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-077: Tool Registry — Single Source of Truth (ADR-001 Phase 1a)

> Dự án: [[projects/control-tower-v2/control-tower-v2]]
> Thiết kế: `docs/adr/ADR-001-unified-tool-architecture.md` §D1

## Tiêu chí nghiệm thu (AC)

- [x] Module mới `backend/app/services/tool_registry.py` với `ToolSpec` (name, description, parameters, handler, tier, permission, entity, slash_alias, group) — mỗi tool khai báo đúng 1 lần
- [x] 7 tool hiện có (pm_create_task→`create_task`, get_status, dispatch_task, record_verdict, approve_gate, cancel_task, compact_context) chuyển vào registry, giữ nguyên hành vi (behavior-preserving)
- [x] `get_tool_definitions()` trở thành projection từ registry (OpenAI function format)
- [x] `CommandRouter.parse/execute` tra cứu qua `slash_alias` trong registry; bảng dịch tay trong `execute_tool` bị xoá
- [x] Endpoint `GET /api/tools` trả registry dump (name, description, slash_alias, tier, group) cho UI/`/help`
- [x] `pm_create_task` giữ như alias deprecated trỏ về `create_task` (không phá session cũ)

## Verification

- `pytest backend/tests/test_command_router.py backend/tests/test_coordinator.py backend/tests/test_tool_registry.py -v` → xanh
- `curl localhost:8000/api/tools` → JSON liệt kê đủ 7 tool với canonical name
- Slash command `/pm test --project x` và tool call `create_task` cho cùng kết quả DB

## Plan

1. Định nghĩa `ToolSpec` dataclass + `TOOL_REGISTRY` dict với 7 tool hiện có.
2. Viết projection `to_openai_tools(specs)` thay thân `get_tool_definitions()` (giữ chữ ký cũ).
3. Refactor `CommandRouter`: `COMMANDS` dict + bảng dịch `execute_tool` sinh từ registry; handlers giữ nguyên.
4. Thêm `GET /api/tools` (router mới hoặc trong chat.py).
5. Test: registry invariants (tên duy nhất, schema hợp lệ), parity slash-vs-tool.

## Sub-tasks

- [ ] ToolSpec + registry module
- [ ] Projection get_tool_definitions
- [ ] CommandRouter shim
- [ ] GET /api/tools
- [ ] Tests + parity check
