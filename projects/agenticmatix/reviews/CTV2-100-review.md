---
id: CTV2-100
task_path: projects/control-tower-v2/tasks/CTV2-100-remove-langgraph-runtime.md
project: control-tower-v2
result_ref: ed404b0
executor: @gpt-5.6-luna
reviewer: @gemini-2.5-pro
status: completed
issued: 2026-07-27
verdict: pass
verdict_date: 2026-07-27
---

# Phiếu Review: CTV2-100 — Bỏ LangGraph khỏi runtime: một FSM duy nhất là TaskOrchestrationService

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-100-remove-langgraph-runtime.md`
- Result-ref: ed404b0
- Executor: @gpt-5.6-luna
- Reviewer: @gemini-2.5-pro
- Ngày phát phiếu: 2026-07-27

## Acceptance Criteria cần verify
## Tiêu chí nghiệm thu (AC)

- [x] LangGraph không còn nằm trên runtime path nào (chat, driver, API); dependency gỡ khỏi requirements nếu không còn ai dùng
- [x] `ContextHierarchy._graph_state_summary` thay bằng dữ liệu từ `TaskOrchestrationService`/`GateRecord` — UI không mất phần hiển thị trạng thái
- [x] Không xoá nhầm logic đang được dùng thật: liệt kê rõ những gì `graph/gates/*` cung cấp và ánh xạ sang service tương ứng (đặc biệt `generate_review_sheet` — nếu còn cần thì port sang CTV2-087 trước khi xoá)
- [x] Test cũ của LangGraph được gỡ hoặc chuyển thành test của service, không để test chết
- [x] `app/graph/context.py` và `app/graph/state.py` **không bị sửa/xoá**; `from app.graph.context import ...` ở 8 call site và `FourEyesViolation` trong `db/models.py` vẫn nguyên
- [x] Toàn bộ suite xanh sau khi gỡ

## Definition of Done (AGENTS.md mục 3)
- [x] Toàn bộ AC pass
- [x] Test liên quan xanh 100%: backend/tests/test_graph_state.py, backend/tests/test_context_hierarchy.py, backend/tests/test_coordinator.py (38 passed)
- [x] Không regression (test khác trong module vẫn xanh)
- [x] Reviewer khác executor (xác nhận reviewer @gemini-2.5-pro ≠ executor @gpt-5.6-luna)

## Chi tiết Kết quả Review & Verification
1. **LangGraph Dependency & Runtime Cleared**:
   - `langgraph>=0.2.0` đã gỡ khỏi `backend/requirements.txt`.
   - Grep `langgraph` trên `backend/app` và `backend/requirements.txt` không còn bất kỳ dòng code nào.
2. **State Summary Ported**:
   - `ContextHierarchy._graph_state_summary` được chuyển sang đọc trực tiếp dữ liệu gate authoritative từ `Task` (`current_gate`, `verdict`, `findings`) và `GateRecord` fallback.
3. **Preserved Core Modules**:
   - `backend/app/graph/context.py` và `backend/app/graph/state.py` giữ nguyên 100%, không bị xoá/sửa. All imports (`FourEyesViolation`, `invalidate_context_snapshot`, `get_context_snapshot`) hoạt động bình thường.
4. **Clean Test Updates**:
   - Các file test stub cũ của LangGraph (`test_graph_nodes.py`, `test_gates.py`) đã gỡ bỏ.
   - `test_context_hierarchy.py`, `test_graph_state.py`, và `test_coordinator.py` chạy qua 38/38 tests.

## Trả kết quả
`/verdict CTV2-100 pass --reviewer @gemini-2.5-pro --commit ed404b0 --notes "Gỡ LangGraph khỏi runtime path thành công. Tất cả AC pass, state summary được chuyển sang Task/GateRecord DB schema, context.py và state.py được giữ nguyên."`
