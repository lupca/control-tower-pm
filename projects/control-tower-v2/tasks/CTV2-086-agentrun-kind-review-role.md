---
id: CTV2-086
title: "AgentRun.kind/agent_role + nới expected_status cho review dispatch"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: urgent
risk: high
deadline: null
executor: "@claude-sonnet-medium"
reviewer: "@claude-opus"
result_ref: "9447d7f"
depends_on:
  - CTV2-088
files:
  - backend/app/db/models.py
  - backend/app/services/task_orchestration.py
  - backend/app/schemas/task.py
  - backend/alembic/versions/017_agent_run_kind.py
flows: []
tests:
  - backend/tests/test_task_orchestration.py
  - backend/tests/test_db_v2.py
  - backend/tests/unit/test_agent_runner.py
dispatched: 2026-07-27
in_review: 2026-07-27
reviewed: 2026-07-27
predicted_success: medium
prediction_factors:
  score: 0.65
  deductions:
    - "hub node: AgentRun (total_degree 53), Task (127) (-0.2)"
    - "migration schema mới trên bảng đang chạy (-0.15)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-086: AgentRun.kind + agent_role, nới expected_status cho review dispatch

> Dự án: [[projects/control-tower-v2/control-tower-v2]]
> Nguồn: `docs/research/autonomous-coordination-gap-analysis.md` §3.3, §5.1, lộ trình #1b

Nền móng dữ liệu để review trở thành **một loại agent run** thay vì một nhánh riêng. Không có task này thì CTV2-087 không tạo được review run.

> **Thứ tự:** phải chạy **sau CTV2-088**. Cả hai cùng sửa `task_orchestration.py` ở vùng `_request_gate`/`_apply_gate`; 088 đổi semantics idempotency nên làm trước để tránh xung đột trực tiếp và tránh viết test trên nền hành vi sai.

## Tiêu chí nghiệm thu (AC)

- [x] `AgentRun.kind` enum `{execute, review}`, default `execute`; migration 018 backfill toàn bộ row cũ = `execute`
- [x] `AgentRun.agent_role` lưu `executor|reviewer` (hoặc suy ra từ `kind`) — truy vấn được "run nào do reviewer chạy"
- [x] `request_dispatch` nhận `expected_status` tham số hoá; dispatch cho review run chấp nhận `awaiting-review` mà KHÔNG nới lỏng cho execute run (`todo` vẫn là mặc định)
- [x] `_apply_gate` ghi `task.reviewer` khi `kind=review`, ghi `task.executor` khi `kind=execute` — không lẫn field
- [x] Four-eyes vẫn cứng: tạo review run với reviewer == executor → raise, không có cờ override
- [x] Migration có `downgrade()` chạy sạch

## Verification

- `cd backend && alembic upgrade head && alembic downgrade -1 && alembic upgrade head` → không lỗi
- `pytest backend/tests/test_task_orchestration.py backend/tests/test_db_v2.py -v` → xanh
- Test mới: dispatch review run khi task ở `awaiting-review` → tạo AgentRun `kind=review`; dispatch execute run ở `awaiting-review` → vẫn `TransitionConflictError`

## Plan

1. Migration `017_agent_run_kind`: thêm `kind` (enum/varchar + CHECK) và `agent_role`, backfill `execute` cho mọi row, viết `downgrade()` đối xứng. Chạy upgrade→downgrade→upgrade trên DB thật trước khi đi tiếp.
2. Model `AgentRun` + schema Pydantic: thêm field, giữ default `execute` để mọi call site cũ không đổi hành vi.
3. `request_dispatch`: đưa `expected_status` thành tham số có default `"todo"`; call site review truyền `"awaiting-review"`. Không nới `_assert_status` toàn cục.
4. `_apply_gate`: phân nhánh theo `kind` — ghi `task.executor` (execute) hoặc `task.reviewer` (review); giữ nguyên four-eyes assert, không thêm cờ bỏ qua.
5. Tests: migration cycle, dispatch review ở `awaiting-review` OK, dispatch execute ở `awaiting-review` vẫn conflict, reviewer==executor raise.

## Sub-tasks

- [x] Migration 018 (kind + agent_role, backfill, downgrade)
- [x] Model + schema
- [x] `request_dispatch` expected_status tham số hoá + `_apply_gate` phân nhánh field
- [x] Tests per AC
