---
id: CTV2-097
title: "Sub-session per task: driver chạy task ở session context_level=task, global chỉ giữ 1 dòng"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: high
risk: normal
deadline: null
executor: "@gpt-5.6-luna"
reviewer: "@gemini-2.5-pro"
result_ref: "802eba3"
depends_on:
  - CTV2-089
  - CTV2-095
files:
  - backend/app/services/context_hierarchy.py
  - backend/app/db/models.py
  - backend/app/api/sessions.py
  - backend/app/services/coordinator.py
flows: []
tests:
  - backend/tests/test_context_hierarchy.py
  - backend/tests/test_api_sessions.py
  - backend/tests/integration/test_chat_context.py
dispatched: null
in_review: 2026-07-27
completed: 2026-07-27
predicted_success: high
prediction_factors:
  score: 0.7
  deductions:
    - "hub node: Session (41), CoordinatorService (43) (-0.2)"
    - "phụ thuộc driver đã chạy được (-0.1)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-097: Sub-session per task — khoản tiết kiệm token lớn nhất

> Dự án: [[projects/control-tower-v2/control-tower-v2]]
> Nguồn: `docs/research/autonomous-coordination-gap-analysis.md` §3.6

Hiện công việc của 10 task dồn hết vào một history duy nhất và bị tính tiền lại mỗi turn. Tách ra thì mỗi task chỉ trả tiền cho context của chính nó.

## Tiêu chí nghiệm thu (AC)

- [x] Driver chạy mỗi task trong session riêng `context_level='task'`, liên kết `task_id`
- [x] Session global chỉ nhận **1 dòng rollup mỗi task** (trạng thái + kết quả + link), không nhận toàn bộ trace
- [x] Mở lại task → truy xuất được sub-session đầy đủ (không mất lịch sử, chỉ là không nằm trong global)
- [x] API/UI liệt kê được sub-session theo task
- [x] Không hồi quy cho chat thủ công của user ở cấp global/project

## Verification

- `pytest backend/tests/test_context_hierarchy.py backend/tests/test_api_sessions.py backend/tests/integration/test_chat_context.py -v` → xanh
- Test: driver chạy 3 task → global session tăng đúng 3 message rollup, mỗi sub-session giữ trace riêng
- Đo: token của global session sau 3 task nhỏ hơn rõ rệt so với baseline gộp chung

## Plan

1. Driver tạo/lookup session `context_level='task'` gắn `task_id` khi bắt đầu xử lý một task; mọi LLM call của task chạy trong session đó.
2. Rollup: khi task đổi trạng thái đáng kể (dispatched/done/escalate), ghi đúng **1 dòng** vào session global (trạng thái + kết quả + task ID), không kèm trace.
3. API `GET /api/sessions?task_id=` để UI mở được sub-session; không xoá dữ liệu, chỉ đổi nơi hiển thị.
4. Đảm bảo chat thủ công của user ở cấp global/project không bị định tuyến nhầm vào sub-session.
5. Tests + đo token global session sau 3 task so với baseline gộp chung.

## Sub-tasks

- [x] Tạo/lookup sub-session theo task
- [x] Rollup 1 dòng vào global
- [x] API liệt kê sub-session
- [x] Tests + đo token

