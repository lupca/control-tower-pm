---
id: CTV2-081
title: "load_tools meta-tool: deferred loading tương thích OpenAI"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: high
risk: normal
deadline: null
executor: "@claude-sonnet-medium"
reviewer: "@claude-opus"
result_ref: "24cbaf0"
depends_on:
  - CTV2-077
files:
  - backend/app/services/tool_registry.py
  - backend/app/services/coordinator.py
  - backend/app/prompts/global_context.md
flows: []
tests:
  - backend/tests/test_coordinator.py
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: high
prediction_factors:
  score: 0.8
  deductions:
    - "đụng tool-execution loop cả complete_turn lẫn stream_turn (-0.15)"
    - "cần giữ prefix ổn định giữa các turn (-0.05)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-081: load_tools Meta-tool (ADR-001 Phase 2b)

> Dự án: [[projects/control-tower-v2/control-tower-v2]]
> Thiết kế: `docs/adr/ADR-001-unified-tool-architecture.md` §D3, fix P1

## Bối cảnh

`defer_loading` + `tool_search_tool_regex` là Anthropic-only — trên OpenAI hiện là no-op, cả 7 tool luôn gửi eager. Cần cơ chế 2 tầng hoạt động thật trên OpenAI: baseline eager nhỏ + nạp nhóm theo yêu cầu trong phạm vi 1 turn.

## Tiêu chí nghiệm thu (AC)

- [x] Request baseline chỉ gồm eager tools (create_task, get_status, query_db) + `load_tools(group)`
- [x] `load_tools(group)` với group ∈ {task_lifecycle, admin, session}: handler trả danh sách schema của group, coordinator merge vào mảng `tools` cho các iteration còn lại của turn hiện tại (cả `complete_turn` và `stream_turn`)
- [x] Turn kế tiếp reset về eager set (prefix byte-stable giữa các turn)
- [x] Xoá `TOOL_SEARCH_TOOL` + flag `defer_loading` khỏi `tool_definitions.py` (thay bằng `tier`/`group` trong registry)
- [x] `global_context.md` thêm 1 dòng hint: "More tools via load_tools(group): task_lifecycle, admin, session"
- [x] Gọi tool thuộc group chưa load → error message hướng dẫn gọi `load_tools` trước (không crash loop)

## Verification

- `pytest backend/tests/test_coordinator.py -v` → xanh
- Test: turn có `load_tools("task_lifecycle")` → iteration sau gọi được `dispatch_task`; turn mới → tools array == baseline

## Plan

1. Registry: nhóm deferred tools theo `group`.
2. Coordinator loop: biến `active_tools` per-turn, merge khi thấy result của `load_tools`.
3. Cập nhật prompt + xoá cơ chế Anthropic cũ.
4. Tests cho cả 2 loop.

## Sub-tasks

- [x] Grouping trong registry
- [x] Merge logic trong 2 loop
- [x] Prompt hint + dọn tool_definitions
- [x] Tests
