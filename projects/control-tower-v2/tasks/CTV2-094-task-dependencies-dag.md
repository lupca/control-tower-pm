---
id: CTV2-094
title: "Bảng task_dependencies + kiểm tra dependency trong driver trước khi dispatch"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: high
risk: high
deadline: null
executor: "@claude-sonnet-medium"
reviewer: "@claude-opus"
result_ref: "d30aeca"
depends_on:
  - CTV2-089
files:
  - backend/app/db/models.py
  - backend/app/services/task_orchestration.py
  - backend/app/schemas/task.py
  - backend/alembic/versions/018_task_dependencies.py
flows: []
tests:
  - backend/tests/test_db_v2.py
  - backend/tests/test_task_orchestration.py
  - backend/tests/test_api_tasks.py
dispatched: null
in_review: 2026-07-27
predicted_success: medium
prediction_factors:
  score: 0.6
  deductions:
    - "hub node: Task (127) (-0.2)"
    - "migration + phát hiện chu trình là logic mới (-0.2)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-094: Task DAG — Epic → sub-tasks chạy đúng thứ tự

> Dự án: [[projects/control-tower-v2/control-tower-v2]]
> Nguồn: `docs/research/autonomous-coordination-gap-analysis.md` §5.4 (G13), lộ trình #5b

Model `Task` không có `parent_task_id`, không `depends_on` (`parent_id` trong `schemas/task.py` là chuỗi gate của `GateRecord`, không phải quan hệ task). Thứ tự phụ thuộc chỉ tồn tại trong context window — mà context lại bị cắt cụt → driver sẽ dispatch loạn thứ tự.

## Tiêu chí nghiệm thu (AC)

- [x] Bảng `task_dependencies(task_id, depends_on_task_id)` + migration 020 có `downgrade()`
- [x] Từ chối chu trình phụ thuộc (tự trỏ hoặc vòng) ở tầng service, có thông báo rõ
- [x] Driver chỉ dispatch task khi **mọi** dependency đã `done`; dependency ở trạng thái khác → task chờ, không bị bỏ quên (được đánh thức khi dependency đóng)
- [x] Dependency bị `failed`/`cancelled` → task phụ thuộc không treo vô hạn, escalate cho user
- [x] API/tool tạo task nhận được danh sách dependency

## Verification

- `cd backend && alembic upgrade head && alembic downgrade -1 && alembic upgrade head` → sạch
- `pytest backend/tests/test_db_v2.py backend/tests/test_task_orchestration.py backend/tests/test_api_tasks.py -v` → xanh
- Test: A depends_on B; B chưa done → driver không dispatch A; B done → A được đánh thức và dispatch
- Test: tạo chu trình A→B→A → bị từ chối

## Plan

1. Migration `018_task_dependencies`: bảng `(task_id, depends_on_task_id)` với PK kép + FK cascade phù hợp + `downgrade()`.
2. Service: `add_dependency` kiểm tra chu trình (DFS trên tập cạnh hiện có) trước khi ghi; tự trỏ chính mình cũng bị chặn.
3. Driver: trước dispatch, truy vấn dependency chưa `done` → nếu còn thì để task ở trạng thái chờ và **đăng ký đánh thức**: khi một task đóng, `advance_task.send()` cho mọi task phụ thuộc nó.
4. Dependency `failed`/`cancelled` → escalate task phụ thuộc thay vì treo im lặng.
5. Mở đường tạo dependency qua tool/API tạo task; tests theo từng AC.

## Sub-tasks

- [x] Migration 020 + model
- [x] Cycle detection ở service layer
- [x] Driver gate theo dependency + đánh thức khi dependency done
- [x] Xử lý dependency failed
- [x] Tests per AC
