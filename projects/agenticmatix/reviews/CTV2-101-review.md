---
id: CTV2-101
task_path: projects/control-tower-v2/tasks/CTV2-101-tool-iteration-budget.md
project: control-tower-v2
result_ref: 5789a12
executor: @gemini-3.6-flash
reviewer: @claude-opus
status: complete
issued: 2026-07-27
verdict: pass
verdict_date: 2026-07-27
---

# Phiếu Review: CTV2-101 — Ngân sách tool-iteration cho coordinator turn: bỏ trần cứng 5, dừng mềm thay vì RuntimeError

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-101-tool-iteration-budget.md`
- Result-ref: 5789a12
- Executor: @gemini-3.6-flash
- Reviewer: @claude-opus
- Ngày phát phiếu: 2026-07-27

## Acceptance Criteria cần verify
## Tiêu chí nghiệm thu (AC)

- [x] Trần lấy từ config (Settings/env), mặc định đủ cho một chuỗi tự chủ hoàn chỉnh, không hardcode 5
  - `config.py:19-21`: `COORDINATOR_MAX_TOOL_ITERATIONS=20`, `COORDINATOR_MAX_TURN_TOKENS=100_000`, `COORDINATOR_MAX_REPEATED_TOOL_CALLS=3`
- [x] Chạm trần → dừng **mềm**: trả lời user kèm trạng thái đã làm được tới đâu và cách tiếp tục; KHÔNG `RuntimeError`, không persist failure cho cả turn
  - `RuntimeError` thay bằng `ProviderResponse(stop_reason=...)` + `_persist_success()`. Tests confirm `status == "complete"`
- [x] Có chặn chi phí: trần theo cả số vòng lẫn token đã tiêu trong turn
  - Checks `accumulated_tokens >= max_turn_tokens` và `iteration >= max_tool_iterations` trong cả `complete_turn` và `stream_turn`
- [x] Phát hiện vòng lặp gọi trùng tool cùng args liên tiếp → dừng sớm, báo rõ
  - Tracks `(canonical_name, args_str)` signature; triggers at `max_repeated_tool_calls` consecutive identical calls
- [x] Telemetry ghi số vòng thực tế mỗi turn để hiệu chỉnh trần sau này
  - `tool_iterations` persisted to assistant message; `logger.info` logs iterations per turn

## Definition of Done (AGENTS.md mục 3)
- [x] Toàn bộ AC pass
- [x] Test liên quan xanh 100%: 16/16 tests passed
- [x] Không regression (test khác trong module vẫn xanh)
- [x] Reviewer khác executor (xác nhận reviewer @claude-opus ≠ executor @gemini-3.6-flash)

## Test gợi ý chạy trong repo code
- `backend/tests/test_coordinator.py`
- `backend/tests/unit/test_tool_execution.py`
- `backend/tests/integration/test_tool_chat.py`

## Câu hỏi rủi ro (từ code-review-graph, tĩnh — không thay thế việc tự đọc diff)
- *(LLM/coordinator bổ sung từ graph nếu có; script không đọc diff và không gọi graph.)*

## Review Toolchain
Chạy theo toolchain của repo đích; preflight các tool đã đăng ký trước khi review.

## Test Results
```
pytest tests/test_coordinator.py tests/unit/test_tool_execution.py tests/integration/test_tool_chat.py -v
======================== 16 passed, 2 warnings in 0.52s ========================
```

## Verdict
**PASS** — All AC criteria verified, tests pass, no regression, four-eyes rule satisfied.
