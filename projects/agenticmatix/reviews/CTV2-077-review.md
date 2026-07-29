---
id: CTV2-077
task_path: projects/control-tower-v2/tasks/CTV2-077-tool-registry-ssot.md
project: control-tower-v2
result_ref: 46e2aee
executor: @claude-sonnet-medium
reviewer: "@claude-opus"
status: passed
issued: 2026-07-27
verdict: pass
verdict_date: 2026-07-27
---

# Phiếu Review: CTV2-077 — Tool Registry: Single Source of Truth cho toàn bộ tool system

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-077-tool-registry-ssot.md`
- Result-ref: 46e2aee
- Executor: @claude-sonnet-medium
- Reviewer: @claude-opus
- Ngày phát phiếu: 2026-07-27

## Acceptance Criteria cần verify
## Tiêu chí nghiệm thu (AC)

- [ ] Module mới `backend/app/services/tool_registry.py` với `ToolSpec` (name, description, parameters, handler, tier, permission, entity, slash_alias, group) — mỗi tool khai báo đúng 1 lần
- [ ] 7 tool hiện có (pm_create_task→`create_task`, get_status, dispatch_task, record_verdict, approve_gate, cancel_task, compact_context) chuyển vào registry, giữ nguyên hành vi (behavior-preserving)
- [ ] `get_tool_definitions()` trở thành projection từ registry (OpenAI function format)
- [ ] `CommandRouter.parse/execute` tra cứu qua `slash_alias` trong registry; bảng dịch tay trong `execute_tool` bị xoá
- [ ] Endpoint `GET /api/tools` trả registry dump (name, description, slash_alias, tier, group) cho UI/`/help`
- [ ] `pm_create_task` giữ như alias deprecated trỏ về `create_task` (không phá session cũ)

## Definition of Done (AGENTS.md mục 3)
- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: backend/tests/test_command_router.py, backend/tests/test_coordinator.py, backend/tests/test_tool_registry.py
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (xác nhận reviewer @claude-opus ≠ executor @claude-sonnet-medium)

## Test gợi ý chạy trong repo code
- `backend/tests/test_command_router.py`
- `backend/tests/test_coordinator.py`
- `backend/tests/test_tool_registry.py`

## Câu hỏi rủi ro (từ code-review-graph, tĩnh — không thay thế việc tự đọc diff)
- *(LLM/coordinator bổ sung từ graph nếu có; script không đọc diff và không gọi graph.)*

## Review Toolchain
Chạy theo toolchain của repo đích; preflight các tool đã đăng ký trước khi review.

## Trả kết quả
`/verdict CTV2-077 <pass|changes> --reviewer @claude-opus [--commit <hash>] [--notes "..."]`
