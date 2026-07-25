---
project: topvnsport-oms
full_name: "TopVNSport - OMS (Order Management System)"
repo_root: /home/lupca/projects/topvnsport
task_prefix: OMS
next_task_id: 16
created: 2026-07-21
updated: 2026-07-25
---

# TopVNSport - OMS

Dự án này quản lý đơn hàng và hoàn tất đơn (fulfillment) cho hệ thống Top VNSport.

## Tiến độ
| Trạng thái | Số task |
|:---|---:|
| done | 11 |
| dispatched | 1 |
| todo | 3 |
*(Cập nhật bởi `/report`)*

## Tasks
*(Cập nhật bởi `/report` — mỗi lần chạy sẽ regenerate lại toàn bộ danh sách này từ `tasks/*.md`)*
- [[OMS-001-zalo-otp-replace-sms]] — Thay thế SMS OTP bằng Zalo OTP (ZBS Template Message) (done)
- [[OMS-002-frontend-zalo-otp]] — Frontend Zalo OTP - Chặn luồng khi SĐT không có Zalo (done)
- [[OMS-003-remove-bypass-otp-backdoor]] — Xóa BYPASS_OTP_TOKEN backdoor khỏi production (done)
- [[OMS-004-zalo-admin-config]] — Cập nhật trang cấu hình Admin: SMS → Zalo OTP (done)
- [[OMS-005-refactor-main-py]] — Refactor OMS/backend/main.py - tách file 1557 dòng thành modules (done)
- [[OMS-006-fix-security-critical]] — Fix Fernet secret fallback + wildcard CORS + gate test-OTP endpoint (done)
- [[OMS-007-fix-race-conditions]] — Fix race conditions: order number, inventory allocation, OTP consumption (todo)
- [[OMS-008-add-business-invariants]] — Add business invariants: block deletion với active orders, partial cancel handling (todo)
- [[OMS-009-add-input-validation]] — Add input validation (schema constraints) (todo)
- [[OMS-010-introduce-alembic-migrations]] — Đưa Alembic vào OMS backend (như PMI) + migration fix config_value schema drift (done)
- [[OMS-011-fix-fernet-key-continuity-prod]] — Luồng Zalo OTP sống được sau khi CI/CD deploy: FERNET_KEY continuity + preflight env + smoke check (done)
- [[OMS-012-rds-migration]] — Migrate OMS to RDS Aurora (done)
- [[OMS-013-provision-service-env-files]] — Deploy tự tạo .env.prod cho PMI/identity trên host + sửa endpoint cũ trong .env.prod.example (done)
- [[OMS-014-align-internal-service-token]] — Align INTERNAL_SERVICE_TOKEN across PMI/OMS/WMS so OMS→PMI service calls stop 401ing (done)
- [[OMS-015-fix-storefront-existing-customer-order]] — Storefront không đặt được đơn cho khách đã tồn tại (dispatched)

## Quy tắc phê duyệt riêng (Project Gates)
- Mọi thay đổi liên quan đến cấu trúc DB hoặc luồng thanh toán/hóa đơn bắt buộc phải có sự xác nhận của User trước khi executor (ngoài hệ) chạy migrate hoặc đụng tới logic tiền.
- Các task hoàn thành phải pass qua 100% test case trong file test tương ứng — reviewer độc lập xác nhận qua `/verdict pass` (`AGENTS.md` mục 3, 4) mới được đánh dấu `status: done`.
- Test chạy trong Docker: `docker compose -f OMS/docker-compose.yml exec api pytest ...` — do executor và reviewer tự chạy, không phải control-tower.

## References (tài liệu trong repo code — chỉ tham chiếu, KHÔNG copy)
| Tài liệu | Path | Mô tả |
|:---|:---|:---|
| CLAUDE.md | `CLAUDE.md` | Dev conventions, test commands |
