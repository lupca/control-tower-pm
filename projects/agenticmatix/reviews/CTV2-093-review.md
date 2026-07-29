---
id: CTV2-093
task_path: projects/control-tower-v2/tasks/CTV2-093-autonomy-policy.md
project: control-tower-v2
result_ref: 173b85f
executor: @gpt-5.6-luna
reviewer: @gemini-2.5-pro
status: completed
issued: 2026-07-27
verdict: pass
verdict_date: 2026-07-27
---

# Phiếu Review: CTV2-093 — Autonomy policy: Settings + project override quyết định Task.mode theo risk

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-093-autonomy-policy.md`
- Result-ref: 173b85f
- Executor: @gpt-5.6-luna
- Reviewer: @gemini-2.5-pro
- Ngày phát phiếu: 2026-07-27

## Acceptance Criteria cần verify
## Tiêu chí nghiệm thu (AC)

- [x] Policy có 3 khoá: `autonomy: plan-only|supervised|auto`, `auto_max_risk: low|normal`, `auto_max_rounds: <int>`
- [x] Thứ tự ưu tiên: project override > Settings toàn cục > mặc định an toàn (`supervised`)
- [x] Driver đọc policy để set `Task.mode` khi tạo task, thay cho mặc định cứng
- [x] Task có risk vượt `auto_max_risk` **luôn** rơi về `supervised`, kể cả khi autonomy = `auto`
- [x] `auto_max_rounds` là trần cứng cho vòng `changes-requested`; vượt → escalate
- [x] Hành động protected (xoá, bulk) không bao giờ được policy tự duyệt

## Definition of Done (AGENTS.md mục 3)
- [x] Toàn bộ AC pass
- [x] Test liên quan xanh 100%: backend/tests/test_task_orchestration.py, backend/tests/test_gate_transitions.py, backend/tests/test_api_projects.py, backend/tests/unit/test_agent_runner.py (123 passed)
- [x] Không regression (test khác trong module vẫn xanh)
- [x] Reviewer khác executor (xác nhận reviewer @gemini-2.5-pro ≠ executor @gpt-5.6-luna)

## Test gợi ý chạy trong repo code
- `backend/tests/test_task_orchestration.py`
- `backend/tests/test_gate_transitions.py`
- `backend/tests/test_api_projects.py`
- `backend/tests/unit/test_agent_runner.py`

## Review Toolchain
Chạy theo toolchain của repo đích; preflight các tool đã đăng ký trước khi review.

## Trả kết quả
`/verdict CTV2-093 pass --reviewer @gemini-2.5-pro`

## Review Notes

**Verdict: PASS** — Reviewed by @gemini-2.5-pro on 2026-07-27

### Implementation Summary
1. **Autonomy Policy Schema & Resolution**:
   - `TaskOrchestrationService.resolve_autonomy(project)` correctly resolves configuration keys (`autonomy`, `auto_max_risk`, `auto_max_rounds`).
   - Resolution hierarchy: Project override (`Project.autonomy_policy`) > Global settings (`Setting` KV table) > Safe default (`supervised`, `normal`, `3`).
   - Unknown or corrupted settings fail-safe gracefully to safe defaults.
2. **Task Mode Calculation**:
   - `TaskOrchestrationService.mode_for_task` evaluates risk vs `auto_max_risk`. Higher risk tasks (`high > normal`) revert to `supervised` mode even under `auto` policy.
   - `CommandRouter._handle_create_task`, `api/tasks.create_task`, and `write_spec_plan` utilize `mode_for_task` to dynamically resolve `Task.mode`.
3. **Escalation Cap**:
   - `agent_runner._advance_changes_requested` respects project policy `auto_max_rounds` for replan round caps.
4. **Project Overrides**:
   - `Project` DB model, Pydantic schemas (`ProjectCreate`, `ProjectUpdate`, `Project`), and migration `021_project_autonomy_policy` support `autonomy_policy` JSON overrides.

### Testing
- Added unit tests for autonomy policy resolution, matrix tests (`autonomy` × `risk`), project overrides over global settings, `write_spec_plan` mode resolution, `auto_max_rounds` policy escalation, and project REST API endpoints.
- Executed 123/123 unit & integration tests across affected modules (`test_task_orchestration.py`, `test_gate_transitions.py`, `test_api_projects.py`, `test_agent_runner.py`) — 100% PASS.

