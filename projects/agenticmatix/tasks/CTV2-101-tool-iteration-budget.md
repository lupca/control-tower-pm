---
id: CTV2-101
title: "Ngân sách tool-iteration cho coordinator turn: bỏ trần cứng 5, dừng mềm thay vì RuntimeError"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: high
risk: normal
deadline: null
executor: "@gemini-3.6-flash"
reviewer: "@claude-opus"
result_ref: "5789a12"
depends_on: []
files:
  - backend/app/services/coordinator.py
  - backend/app/core/config.py
flows: []
tests:
  - backend/tests/test_coordinator.py
  - backend/tests/unit/test_tool_execution.py
  - backend/tests/integration/test_tool_chat.py
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: high
prediction_factors:
  score: 0.75
  deductions:
    - "hub node: CoordinatorService (43), complete_turn (63) (-0.2)"
    - "nới trần có thể tăng chi phí nếu thiếu chặn (-0.05)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-101: Trần tool-iteration đang chặn ngay chuỗi tự chủ đầu tiên

> Dự án: [[projects/control-tower-v2/control-tower-v2]]
> Nguồn: `docs/research/autonomous-coordination-gap-analysis.md` §1.2

`max_tool_iterations = 5`, vượt là `RuntimeError` → persist failure. Một chuỗi thực tế (`load_tools` → `create_task` → `update_task` → `dispatch_task` → `get_status`) chạm trần ngay ở task **đầu tiên**.

## Tiêu chí nghiệm thu (AC)

- [x] Trần lấy từ config (Settings/env), mặc định đủ cho một chuỗi tự chủ hoàn chỉnh, không hardcode 5
- [x] Chạm trần → dừng **mềm**: trả lời user kèm trạng thái đã làm được tới đâu và cách tiếp tục; KHÔNG `RuntimeError`, không persist failure cho cả turn
- [x] Có chặn chi phí: trần theo cả số vòng lẫn token đã tiêu trong turn
- [x] Phát hiện vòng lặp gọi trùng tool cùng args liên tiếp → dừng sớm, báo rõ
- [x] Telemetry ghi số vòng thực tế mỗi turn để hiệu chỉnh trần sau này

## Verification

- `pytest backend/tests/test_coordinator.py backend/tests/unit/test_tool_execution.py backend/tests/integration/test_tool_chat.py -v` → xanh
- Test: chuỗi 6 tool call liên tiếp → hoàn thành, không exception
- Test: gọi trùng tool cùng args 3 lần → dừng sớm với thông báo

## Plan

1. Đưa `max_tool_iterations` vào `core/config.py` (env/Settings), default đủ cho chuỗi `load_tools → create_task → update_task → dispatch_task → get_status` cộng biên.
2. Thêm trần token cho một turn song song với trần vòng — hết ngân sách nào trước thì dừng theo cái đó.
3. Chạm trần → dừng mềm: trả assistant message mô tả đã làm tới đâu + cách tiếp tục; bỏ `RuntimeError` và việc persist failure cho cả turn.
4. Phát hiện lặp: cùng tool + cùng args lặp liên tiếp (ngưỡng nhỏ) → dừng sớm kèm thông báo, tránh đốt ngân sách vô ích.
5. Telemetry số vòng/turn; tests theo AC.

## Sub-tasks

- [ ] Trần vào config + ngân sách token
- [ ] Dừng mềm thay RuntimeError
- [ ] Phát hiện lặp
- [ ] Telemetry + tests
