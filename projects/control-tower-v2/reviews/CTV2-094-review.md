---
id: CTV2-094
task_path: projects/control-tower-v2/tasks/CTV2-094-task-dependencies-dag.md
project: control-tower-v2
result_ref: d30aeca
executor: @claude-sonnet-medium
reviewer: @claude-opus
status: closed
issued: 2026-07-27
verdict: pass
verdict_date: 2026-07-27
---

# Phiếu Review: CTV2-094 — Bảng task_dependencies + kiểm tra dependency trong driver trước khi dispatch

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-094-task-dependencies-dag.md`
- Result-ref: d30aeca
- Executor: @claude-sonnet-medium
- Reviewer: @claude-opus
- Ngày phát phiếu: 2026-07-27

## Acceptance Criteria cần verify
## Tiêu chí nghiệm thu (AC)

- [ ] Bảng `task_dependencies(task_id, depends_on_task_id)` + migration 018 có `downgrade()`
- [ ] Từ chối chu trình phụ thuộc (tự trỏ hoặc vòng) ở tầng service, có thông báo rõ
- [ ] Driver chỉ dispatch task khi **mọi** dependency đã `done`; dependency ở trạng thái khác → task chờ, không bị bỏ quên (được đánh thức khi dependency đóng)
- [ ] Dependency bị `failed`/`cancelled` → task phụ thuộc không treo vô hạn, escalate cho user
- [ ] API/tool tạo task nhận được danh sách dependency

## Definition of Done (AGENTS.md mục 3)
- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: backend/tests/test_db_v2.py, backend/tests/test_task_orchestration.py, backend/tests/test_api_tasks.py
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (xác nhận reviewer @claude-opus ≠ executor @claude-sonnet-medium)

## Test gợi ý chạy trong repo code
- `backend/tests/test_db_v2.py`
- `backend/tests/test_task_orchestration.py`
- `backend/tests/test_api_tasks.py`

## Câu hỏi rủi ro (từ code-review-graph, tĩnh — không thay thế việc tự đọc diff)
- *(LLM/coordinator bổ sung từ graph nếu có; script không đọc diff và không gọi graph.)*

## Review Toolchain
Chạy theo toolchain của repo đích; preflight các tool đã đăng ký trước khi review.

## Trả kết quả
`/verdict CTV2-094 <pass|changes> --reviewer @claude-opus [--commit <hash>] [--notes "..."]`

## Verification Notes (2026-07-27)

### Tests
- `pytest tests/test_db_v2.py tests/test_task_orchestration.py tests/test_api_tasks.py tests/unit/test_agent_runner.py` — 67/67 passed

### Migration
- `alembic downgrade -1 && alembic upgrade head` — clean

### AC Checklist
- [x] `task_dependencies(task_id, depends_on_task_id)` — migration 020 with composite PK, FK cascades, self-loop check constraint, and working `downgrade()`
- [x] Cycle rejection — `DependencyCycleError` raised by `add_dependency` (self-ref + DFS transitive check)
- [x] Driver gates dispatch on all deps `done` — `_blocked_by_dependencies` in agent_runner.py; parked tasks woken by `wake_dependents`
- [x] Failed dep → escalate — `escalated_dependency_failed` outcome with `awaiting_approval=True`
- [x] API/tool accepts `depends_on` — TaskCreate schema, REST API, CommandRouter `--depends-on`, tool registry updated

### Four-Eyes
Executor `@claude-sonnet-medium` ≠ Reviewer `@claude-opus` ✓
