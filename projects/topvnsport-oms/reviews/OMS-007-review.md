---
id: OMS-007
task_path: projects/topvnsport-oms/tasks/OMS-007-fix-race-conditions.md
project: topvnsport-oms
result_ref: 3924217f6a03c3b3f3ebfd78a1e3c417cd5c331b
executor: "@antigravity-3.6-high"
reviewer: "@claude-opus-5"
status: passed
issued: 2026-07-26
verdict: pass
verdict_date: 2026-07-26
---

# Phiếu Review: OMS-007 — Fix race conditions: order number, inventory allocation, OTP consumption

- Dự án: topvnsport-oms (`/home/lupca/projects/topvnsport`)
- Task gốc: `projects/topvnsport-oms/tasks/OMS-007-fix-race-conditions.md`
- Result-ref: 3924217f6a03c3b3f3ebfd78a1e3c417cd5c331b
- Executor: @antigravity-3.6-high
- Ngày phát phiếu: 2026-07-26

## Acceptance Criteria cần verify
- [x] Tạo order concurrency không sinh trùng order number
- [x] Verify OTP concurrency không bị dùng nhiều lần (lock row)
- [x] `confirm_order` check lại kho/inventory (lock atomic) trước khi chuyển trạng thái
- [x] Script giả lập 10 concurrent requests (order_number/otp) không bị lỗi hay tạo sai

## Definition of Done (AGENTS.md mục 3)
- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: OMS/backend/test_main.py, OMS/backend/tests/test_concurrency.py
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (bạn đang review, hãy xác nhận bạn ≠ @antigravity-3.6-high)

## Test gợi ý chạy trong repo code
docker compose -f OMS/docker-compose.yml exec api pytest OMS/backend/test_main.py OMS/backend/tests/test_concurrency.py

## Review Toolchain
Chạy review theo repo's toolchain:
  cat .claude/review-toolchain.md
Repo PHẢI khai báo toolchain. Với mỗi tool trong pipeline:
  - Preflight theo knowledge/tools/tool-registry.md (health_check → install nếu cần → re-check)
  - Tool required=hard mà preflight fail sau install → BLOCK + escalate, không review với partial tools
  - /code-review là baseline tool trong registry, chạy cùng (không thay thế) các tools khác
Chạy tất cả tools trong pipeline, aggregate kết quả,
rồi verify từng AC item.

## Trả kết quả
Sau khi review xong, báo lại cho control-tower bằng lệnh:
`/verdict OMS-007 <pass|changes> --reviewer @<tên bạn> [--commit <hash>] [--notes "..."]`
