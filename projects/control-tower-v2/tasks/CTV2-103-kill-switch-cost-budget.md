---
id: CTV2-103
title: "Kill switch autonomy + trần chi phí mỗi task + trần run đồng thời"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: urgent
risk: high
deadline: null
executor: "@claude-sonnet-medium"
reviewer: "@claude-opus"
result_ref: "3f26949"
depends_on: []
files:
  - backend/app/services/task_orchestration.py
  - backend/app/workers/agent_runner.py
  - backend/app/db/models.py
  - backend/app/core/config.py
flows: []
tests:
  - backend/tests/test_task_orchestration.py
  - backend/tests/unit/test_agent_runner.py
  - backend/tests/test_llm_usage.py
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: medium
prediction_factors:
  score: 0.65
  deductions:
    - "hub node: run_agent (53), TaskOrchestrationService (43) (-0.2)"
    - "phải đúng ngay từ đầu: đây là lớp an toàn cho mọi task sau (-0.15)"
created: 2026-07-27
updated: 2026-07-27
rejections: 1
---

# CTV2-103: Ba cái phanh trước khi bật hệ tự chạy

> Dự án: [[projects/control-tower-v2/control-tower-v2]]
> Phải xong **cùng hoặc trước CTV2-089**. Driver không được bật khi chưa có phanh.

Không task nào trong lộ trình cấp ba thứ tối thiểu để vận hành an toàn một hệ tự chạy. CTV2-093 chỉ quyết định `Task.mode` theo risk — đó là chính sách, không phải phanh. Mỗi run hiện có `timeout_seconds = 14_400`: một vòng lặp hỏng có thể đốt **4 giờ CLI mỗi vòng** trước khi có người nhận ra. `LLMUsage` đã có ledger `cost_usd` nên trần chi phí làm được ngay, không cần hạ tầng mới.

## Tiêu chí nghiệm thu (AC)

- [ ] **Kill switch toàn cục**: một setting (`autonomy_enabled`) tắt được mọi tiến triển tự động ngay lập tức; task đang chạy dở được để yên hoặc hủy có kiểm soát, task mới không được đẩy. Tắt/bật không cần restart service
- [ ] **Trần chi phí mỗi task**: tổng `cost_usd` từ `LLMUsage` + chi phí run của một task vượt trần → dừng task, đánh dấu escalate, không thử tiếp
- [ ] **Trần run đồng thời**: số `AgentRun` đang chạy vượt trần → xếp hàng, không spawn thêm process
- [ ] Trần thời gian mỗi run hạ xuống giá trị hợp lý cho vòng tự chủ (mặc định 4 giờ hiện tại là quá dài cho một bước máy móc); giá trị cấu hình được
- [ ] Mọi lần chạm phanh đều ghi audit + escalate rõ ràng, không dừng im lặng
- [ ] Kill switch đọc được từ cả driver lẫn API; có endpoint/tool để bật tắt

## Verification

- `pytest backend/tests/test_task_orchestration.py backend/tests/unit/test_agent_runner.py backend/tests/test_llm_usage.py -v` → xanh
- Test: `autonomy_enabled=false` → `advance_task` không đẩy task nào, có bản ghi audit
- Test: task vượt trần `cost_usd` → dừng + escalate, không spawn run mới
- Test: vượt trần run đồng thời → run thứ N+1 xếp hàng, không có process thứ N+1

## Plan

1. Ba khoá trong Settings/config: `autonomy_enabled`, `max_cost_usd_per_task`, `max_concurrent_runs`, cộng `run_timeout_seconds` hạ mặc định.
2. Hàm `check_brakes(task) -> BrakeDecision` đặt ở service layer, gọi ở đầu `advance_task` và trước mọi lần spawn run.
3. Trần chi phí: cộng dồn `LLMUsage.cost_usd` theo task (dùng ledger sẵn có, không tạo bảng mới).
4. Trần đồng thời: đếm `AgentRun` đang chạy dưới khoá trước khi `run_agent.send()`.
5. Endpoint/tool bật tắt kill switch + audit mọi lần chạm phanh.
6. Tests theo từng AC.

## Sub-tasks

- [ ] Settings + config 4 khoá
- [ ] `check_brakes` ở service layer
- [ ] Trần chi phí từ LLMUsage
- [ ] Trần run đồng thời
- [ ] Endpoint/tool + audit
- [ ] Tests per AC

## Findings từ reviewer
- [x] P1: FOR UPDATE on aggregate fails PostgreSQL → fixed in 3f26949
- [x] queued count causes deadlock → fixed: order_by(id) before locking
- [x] brake before terminal guard breaks completed runs → fixed: terminal check moved first
