---
id: CTV2-098
title: "Thông báo gate pending vào global chat + WS event (inbox điều phối)"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: medium
risk: normal
deadline: null
executor: "@gpt-5.6-luna"
reviewer: "@gemini-2.5-pro"
result_ref: "72d7ab4"
depends_on:
  - CTV2-089
files:
  - backend/app/services/task_orchestration.py
  - backend/app/api/ws.py
  - backend/app/api/stream.py
  - backend/app/services/context_hierarchy.py
flows: []
tests:
  - backend/tests/test_api_sessions.py
  - backend/tests/integration/test_streaming.py
  - backend/tests/test_gates.py
dispatched: null
in_review: 2026-07-27
predicted_success: high
prediction_factors:
  score: 0.75
  deductions:
    - "hub node: event_generator (51) (-0.2)"
    - "không có test WS notification hiện có (-0.05)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-098: Kênh xác nhận — "tự chạy" không được biến thành "đứng im không ai hay"

> Dự án: [[projects/control-tower-v2/control-tower-v2]]
> Nguồn: `docs/research/autonomous-coordination-gap-analysis.md` §2 (G8), §3.5, lộ trình #7

Gate pending hiện chỉ set `task.awaiting_approval=True` + `approval_prompt`, không đẩy đi đâu cả.

## Tiêu chí nghiệm thu (AC)

- [x] Khi driver gặp gate pending hoặc cần user quyết định: ghi message `role="system"` vào **session global của user** kèm task ID + prompt duyệt
- [x] Phát WS/SSE event để UI đang mở nhận ngay, không cần refresh
- [x] User trả lời `/approve <task>` ngay trong luồng global → gate được xử lý đúng task
- [x] Không spam: mỗi (task, gate) chỉ thông báo một lần cho tới khi trạng thái đổi
- [x] Message rollup này nằm trong hạn mức của CTV2-097 (1 dòng, không kèm trace)

## Verification

- `pytest backend/tests/integration/test_streaming.py backend/tests/test_gates.py -v` → xanh
- Test: dispatch ở mode supervised → global session có message system chứa task ID; WS client nhận event
- Test: driver chạy lại cùng gate → không sinh message thứ hai

## Plan

1. Notifier trong service layer: khi tạo GateRecord `pending`, ghi message `role="system"` vào session global của user kèm task ID + `approval_prompt`.
2. Phát WS/SSE event qua kênh có sẵn (`api/ws.py`, `api/stream.py`) để UI đang mở nhận ngay.
3. Chống trùng: khoá `(task_id, gate, state)` — chỉ thông báo lại khi trạng thái đổi.
4. Đảm bảo `/approve <task>` trả lời từ session global định tuyến đúng task.
5. Tests: dispatch supervised → có system message + WS event; chạy lại cùng gate → không có message thứ hai.

## Sub-tasks

- [ ] Notifier: ghi system message vào global session
- [ ] WS/SSE event
- [ ] Chống trùng thông báo
- [ ] Tests per AC
