---
id: CTV2-072
task_path: projects/control-tower-v2/tasks/CTV2-072-prompt-tool-refactor.md
project: control-tower-v2
result_ref: bf047f0
executor: @gpt-5.6-luna
reviewer: "@claude-opus"
status: passed
issued: 2026-07-27
verdict: pass
verdict_date: 2026-07-27
---

# Phiếu Review: CTV2-072 — Refactor Prompt System + Tool Execution Loop for API Mode

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-072-prompt-tool-refactor.md`
- Result-ref: bf047f0
- Executor: @gpt-5.6-luna
- Reviewer: @claude-opus
- Ngày phát phiếu: 2026-07-27

## Acceptance Criteria cần verify
## Tiêu chí nghiệm thu (AC)

### Part A: Prompt System
- [ ] AC1: Tạo `backend/app/prompts/global_context.md` với nội dung đầy đủ:
  - Role definition (Control Tower V2 coordinator)
  - Gate rules (Spec/Plan/Dispatch/Review/Verdict)
  - Tool usage instructions (khi nào dùng tool nào)
  - Output format guidelines
  - KHÔNG reference paths không tồn tại
- [ ] AC2: Tool definitions trong prompt phải match `tool_definitions.py`
- [ ] AC3: Context hierarchy inject prompt đúng thứ tự với cache_control

### Part B: Tool Execution Loop
- [ ] AC4: `coordinator.py` implement tool execution loop cho API mode:
  - Nhận `response.tool_calls` từ adapter
  - Execute tools via `CommandRouter`
  - Append tool results vào messages
  - Gọi lại LLM với tool results
  - Repeat until LLM trả text without tool_calls
- [ ] AC5: `chat.py` stream tool execution progress (không chỉ final text)
- [ ] AC6: Tool results được persist vào session.messages với role="tool"

### Part C: Testing
- [ ] AC7: Unit test cho tool execution loop
- [ ] AC8: Integration test: user hỏi "có project nào?" → LLM gọi `get_status` → execute → trả lời đúng

## Definition of Done (AGENTS.md mục 3)
- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: backend/tests/test_coordinator.py, backend/tests/unit/test_context_hierarchy.py
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (xác nhận reviewer @claude-opus ≠ executor @gpt-5.6-luna)

## Test gợi ý chạy trong repo code
- `backend/tests/test_coordinator.py`
- `backend/tests/unit/test_context_hierarchy.py`

## Câu hỏi rủi ro (từ code-review-graph, tĩnh — không thay thế việc tự đọc diff)
- *(LLM/coordinator bổ sung từ graph nếu có; script không đọc diff và không gọi graph.)*

## Review Toolchain
Chạy theo toolchain của repo đích; preflight các tool đã đăng ký trước khi review.

## Trả kết quả
`/verdict CTV2-072 <pass|changes> --reviewer @claude-opus [--commit <hash>] [--notes "..."]`
