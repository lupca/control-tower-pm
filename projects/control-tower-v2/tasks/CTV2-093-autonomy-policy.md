---
id: CTV2-093
title: "Autonomy policy: Settings + project override quyết định Task.mode theo risk"
repo_root: /home/lupca/projects/control-tower-v2
status: completed
priority: high
risk: normal
deadline: null
executor: "@gpt-5.6-luna"
reviewer: "@gemini-2.5-pro"
result_ref: "173b85f"
depends_on:
  - CTV2-089
files:
  - backend/app/services/task_orchestration.py
  - backend/app/services/command_router.py
  - backend/app/db/models.py
  - backend/app/api/projects.py
flows: []
tests:
  - backend/tests/test_task_orchestration.py
  - backend/tests/test_gates.py
  - backend/tests/test_api_projects.py
dispatched: null
in_review: 2026-07-27
completed_at: 2026-07-27T22:53:18+07:00
predicted_success: high
prediction_factors:
  score: 0.7
  deductions:
    - "hub node: Task (127), Project (51) (-0.2)"
    - "hạ tầng Settings KV đã có sẵn từ CTV2-083 (+0)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-093: Autonomy policy — "chỉ dừng khi cần" thay vì dừng ở mọi gate

> Dự án: [[projects/control-tower-v2/control-tower-v2]]
> Nguồn: `docs/research/autonomous-coordination-gap-analysis.md` §2 (G6), §3.4, lộ trình #5

`Task.mode` default `'supervised'` và **không có chỗ nào set nó khi tạo task** → mọi dispatch/verdict đều dừng ở gate pending. Dùng hạ tầng Settings KV đã có (CTV2-083).

## Tiêu chí nghiệm thu (AC)

- [x] Policy có 3 khoá: `autonomy: plan-only|supervised|auto`, `auto_max_risk: low|normal`, `auto_max_rounds: <int>`
- [x] Thứ tự ưu tiên: project override > Settings toàn cục > mặc định an toàn (`supervised`)
- [x] Driver đọc policy để set `Task.mode` khi tạo task, thay cho mặc định cứng
- [x] Task có risk vượt `auto_max_risk` **luôn** rơi về `supervised`, kể cả khi autonomy = `auto`
- [x] `auto_max_rounds` là trần cứng cho vòng `changes-requested`; vượt → escalate
- [x] Hành động protected (xoá, bulk) không bao giờ được policy tự duyệt

## Verification

- `pytest backend/tests/test_task_orchestration.py backend/tests/test_gates.py backend/tests/test_api_projects.py -v` → xanh
- Test ma trận: (autonomy=auto, risk=low) → chạy thẳng; (autonomy=auto, risk=high) → dừng gate; (autonomy=plan-only) → chặn dispatch
- Test: project override thắng setting toàn cục

## Plan

1. Định nghĩa 3 khoá policy trong Settings KV (CTV2-083) + cột override trên `Project`.
2. Resolver `resolve_autonomy(project) -> Policy` theo thứ tự project → global → mặc định `supervised`; giá trị lạ/thiếu → fail safe về `supervised`.
3. Driver (CTV2-089) dùng resolver để set `Task.mode` khi tạo task và để quyết định dừng/tiếp ở gate; trần vòng lấy `auto_max_rounds` thay hằng số tạm.
4. Guard: `risk > auto_max_risk` ép `supervised`; protected action (xoá, bulk) không bao giờ auto-approve dù policy = `auto`.
5. Tests ma trận (autonomy × risk) + test project override thắng global.

## Sub-tasks

- [x] Schema policy trong Settings + project override field
- [x] Resolver theo thứ tự ưu tiên
- [x] Driver dùng policy khi tạo task/quyết định gate
- [x] Tests ma trận

