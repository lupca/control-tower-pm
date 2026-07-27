---
id: CTV2-092
title: "create_task: project scope thật + sinh ID an toàn + global session scope cho snapshot"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: high
risk: high
deadline: null
executor: "@claude-sonnet-medium"
reviewer: "@claude-opus"
result_ref: "49dd71a"
depends_on: []
files:
  - backend/app/services/command_router.py
  - backend/app/services/context_hierarchy.py
  - backend/app/db/models.py
  - backend/app/graph/context.py
flows: []
tests:
  - backend/tests/test_command_router.py
  - backend/tests/test_context_hierarchy.py
  - backend/tests/unit/test_context_snapshot.py
  - backend/tests/integration/test_chat_context.py
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: medium
prediction_factors:
  score: 0.6
  deductions:
    - "hub node: Task (127), Session (41), build_context_snapshot (39) (-0.2)"
    - "sinh ID đổi cách → nguy cơ đụng dữ liệu cũ (-0.2)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-092: Sửa bước đầu tiên của flow — project scope + task ID

> Dự án: [[projects/control-tower-v2/control-tower-v2]]
> Nguồn: `docs/research/autonomous-coordination-gap-analysis.md` §2 (G5), lộ trình #4

Ba lỗi vận hành nằm ngay bước đầu tiên: `project = 'default'` hardcode (FK tới `projects.id` → `IntegrityError` hoặc task rơi nhầm chỗ), task ID sinh bằng `COUNT(*) + 1` (race + tái dùng ID sau khi xoá), và session global (`context_level='global'`, `project_id=None`) làm `_scope_project_id` trả None nên snapshot **không** liệt kê recent task — đúng ngữ cảnh user chat nhiều nhất lại nghèo nhất.

## Tiêu chí nghiệm thu (AC)

- [x] `create_task` không còn hardcode `'default'`: suy project từ session scope, hoặc từ tham số, hoặc hỏi lại user — không bao giờ ghi vào project không tồn tại
- [x] Sinh task ID không dùng `COUNT(*)`: dùng sequence/counter per project có khoá, chạy song song 20 lần → 20 ID duy nhất, không tái dùng ID đã xoá
- [x] Session `context_level='global'` vẫn có snapshot liệt kê task gần đây trên **mọi project** (không rỗng như hiện tại)
- [x] Không hồi quy cho session cấp project: vẫn scope đúng project đó

## Verification

- `pytest backend/tests/test_command_router.py backend/tests/test_context_hierarchy.py backend/tests/unit/test_context_snapshot.py -v` → xanh
- Test đua: tạo 20 task song song → 20 ID khác nhau
- Test: `create_task` không `--project` từ session global → không `IntegrityError`, project được xác định rõ
- Test: snapshot của session global chứa recent tasks

## Plan

1. Resolve project theo thứ tự: tham số `--project` → `session.project_id` → nếu session global và không suy được thì trả lỗi hỏi lại user. Bỏ hẳn hằng `'default'`.
2. Sinh ID: thay `COUNT(*) + 1` bằng counter per project có khoá (cột `next_task_seq` trên `projects` cập nhật trong cùng transaction, hoặc sequence). Không tái dùng ID của task đã xoá.
3. `_scope_project_id`: session global trả "mọi project" thay vì None; `build_context_snapshot` liệt kê recent tasks cross-project có giới hạn số dòng.
4. Tests: đua 20 task song song → 20 ID; create_task từ session global; snapshot global khác rỗng; hồi quy session cấp project vẫn scope đúng.

## Sub-tasks

- [x] Resolve project cho create_task
- [x] Sinh ID an toàn (khoá/sequence) + test đua
- [x] Snapshot cho session global
- [x] Tests per AC
