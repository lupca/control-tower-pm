---
id: CTV2-091
task_path: projects/control-tower-v2/tasks/CTV2-091-spec-plan-step-real-gate.md
project: control-tower-v2
result_ref: 9015407
executor: @claude-sonnet-medium
reviewer: @claude-opus
status: completed
issued: 2026-07-27
verdict: pass
verdict_date: 2026-07-27
---

# Phiếu Review: CTV2-091 — Spec/Plan step thật: sinh AC + plan + files/tests từ graph, siết verdict theo số AC

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-091-spec-plan-step-real-gate.md`
- Result-ref: 9015407
- Executor: @claude-sonnet-medium
- Reviewer: @claude-opus
- Ngày phát phiếu: 2026-07-27

## Acceptance Criteria cần verify
## Tiêu chí nghiệm thu (AC)

- [x] Một LLM call sinh đủ `acceptance_criteria[]`, `plan`, `files[]`, `tests[]`, `risk` và ghi thẳng vào DB (không phải stub, không phải chỉ log)
  - `spec_plan_generator.py:64-132`: one LLM call with schema-validated retry
  - `write_spec_plan()` persists to DB via service layer
- [x] `files[]`/`flows[]` lấy từ research tools (CTV2-090) — có bằng chứng call graph trong bản ghi; LLM không được tự bịa đường dẫn
  - `semantic_search()` provides graph candidates
  - Unconfirmed files marked with `*(chưa xác nhận)*` suffix (L117-120)
  - Flows come only from `get_affected_flows()`, never LLM (L122-130)
- [x] Task không có AC thì **không được vào dispatch** (chặn ở service layer, không chỉ ở prompt)
  - `task_orchestration.py:146-149` raises `PrerequisiteError`
- [x] `_validate_verdict_prerequisites`: bỏ `max(1, ...)`; verdict `pass` yêu cầu đủ số kết quả bằng số AC, thiếu một AC → không pass
  - L1041-1044: `required_count = len(task.acceptance_criteria or [])` — no floor
- [x] Task cũ đang dở dang có đường di trú rõ ràng (backfill hoặc cờ legacy), không làm kẹt backlog hiện có
  - Migration `019_legacy_no_ac.py` adds column and backfills existing AC-less tasks
- [x] Spec/Plan là gate thật ở tầng dữ liệu, nhất quán với `GATED_ACTIONS`
  - `GATED_ACTIONS = {"spec_plan", "dispatch", "review_order", "verdict"}`

## Definition of Done (AGENTS.md mục 3)
- [x] Toàn bộ AC pass
- [x] Test liên quan xanh 100%: 45 tests pass (test_task_orchestration, test_spec_plan_generator, test_gates, test_full_flow)
- [x] Không regression (402 passed; 1 failed unrelated to commit — local config drift in timeout_seconds)
- [x] Reviewer khác executor (xác nhận reviewer @claude-opus ≠ executor @claude-sonnet-medium)

## Test gợi ý chạy trong repo code
- `backend/tests/test_command_router.py`
- `backend/tests/test_task_orchestration.py`
- `backend/tests/test_gates.py`
- `backend/tests/integration/test_full_flow.py`

## Câu hỏi rủi ro (từ code-review-graph, tĩnh — không thay thế việc tự đọc diff)
- *(LLM/coordinator bổ sung từ graph nếu có; script không đọc diff và không gọi graph.)*

## Review Toolchain
Chạy theo toolchain của repo đích; preflight các tool đã đăng ký trước khi review.

## Trả kết quả
`/verdict CTV2-091 <pass|changes> --reviewer @claude-opus [--commit <hash>] [--notes "..."]`
