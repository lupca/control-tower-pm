---
id: OMS-001
task_path: projects/topvnsport-oms/tasks/OMS-001-zalo-otp-replace-sms.md
project: topvnsport-oms
result_ref: topvnsport@main
executor: "@gpt-5.6-sol"
reviewer: null
status: pending
issued: 2026-07-23
verdict: null
verdict_date: null
---

# Phiếu Review: OMS-001 — Thay thế SMS OTP bằng Zalo OTP (ZBS Template Message)

- Dự án: TopVNSport OMS (`/home/lupca/projects/topvnsport`)
- Task gốc: `projects/topvnsport-oms/tasks/OMS-001-zalo-otp-replace-sms.md`
- Result-ref: topvnsport@main
- Executor: @gpt-5.6-sol
- Ngày phát phiếu: 2026-07-23

## Acceptance Criteria cần verify

- [ ] **AC1**: `sms_service.py` bị xóa hoàn toàn, thay bằng `zalo_service.py` với hàm `send_zalo_otp(phone, otp, access_token, template_id)` gọi Zalo API `POST https://business.openapi.zalo.me/message/template`
- [ ] **AC2**: Endpoint `/api/sms/send-otp` gọi `zalo_service.send_zalo_otp` thay vì `sms_service.send_speed_sms`; fetch `zalo_access_token` và `zalo_template_id` từ `SystemConfig`
- [ ] **AC3**: Khi Zalo trả lỗi (`-118` SĐT không có Zalo, `-115` hết quota, `-108` format sai), API trả HTTP 400 với message tiếng Việt rõ ràng, không fallback SMS
- [ ] **AC4**: Model `OtpVerification` có thêm field `zalo_message_id: Optional[str]` để map webhook
- [ ] **AC5**: Endpoint webhook `/api/sms/zalo-webhook` lắng nghe event `user_received_message`, verify signature HMAC-SHA256 với `OA_SECRET_KEY`, update `provider_status = "DELIVERED"` vào record tương ứng
- [ ] **AC6**: Token refresh tự động: `BackgroundScheduler` (apscheduler) chạy mỗi 20 giờ, gọi `POST https://oauth.zaloapp.com/v4/oa/access_token` với refresh_token, update cả `access_token` và `refresh_token` mới vào `SystemConfig`
- [ ] **AC7**: `requirements.txt` có thêm `apscheduler==3.10.4`
- [ ] **AC8**: Tất cả unit tests trong `test_main.py` liên quan OTP được update mock từ `sms_service` sang `zalo_service`, pass 100%
- [ ] **AC9**: E2E test `test_storefront_otp_checkout_flow` vẫn pass (dùng test-endpoint bypass)

## Definition of Done (AGENTS.md mục 3)

- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%:
  - `OMS/backend/test_main.py::test_send_otp_rate_limit_and_lockout`
  - `OMS/backend/test_main.py::test_order_creation_otp_security`
  - `OMS/backend/test_main.py::test_otp_hashing`
  - `OMS/backend/test_main.py::test_sms_provider_failure`
  - `OMS/backend/test_main.py::test_otp_verification_flow`
  - `e2e_tests/tests/test_storefront_otp_flow.py::test_storefront_otp_checkout_flow`
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (bạn đang review, hãy xác nhận bạn ≠ @gpt-5.6-sol)

## Test gợi ý chạy trong repo code

```bash
# Unit tests OTP
cd /home/lupca/projects/topvnsport/OMS/backend
pytest test_main.py -k "otp" -v

# E2E test
cd /home/lupca/projects/topvnsport/e2e_tests
pytest tests/test_storefront_otp_flow.py -v

# Quick verification checks
test ! -f /home/lupca/projects/topvnsport/OMS/backend/services/sms_service.py && echo "PASS: sms_service.py deleted"
test -f /home/lupca/projects/topvnsport/OMS/backend/services/zalo_service.py && echo "PASS: zalo_service.py created"
grep -q "apscheduler" /home/lupca/projects/topvnsport/OMS/backend/requirements.txt && echo "PASS: apscheduler added"
grep -q "zalo_message_id" /home/lupca/projects/topvnsport/OMS/backend/models.py && echo "PASS: zalo_message_id field added"
```

## Câu hỏi rủi ro (từ code-review-graph, tĩnh)

| Priority | Category | Question |
|----------|----------|----------|
| high | bridge_node | `test_full_flow` là critical connector — verify không bị break |
| high | hub_risk | `OrdersPageContent` (OMS frontend) có 195 connections, không có test trực tiếp |
| medium | untested_hotspot | Các migration files có nhiều connections nhưng không có test |

**Lưu ý đặc biệt cho task này:**
- `test_storefront_otp_checkout_flow` là **bridge node** — thay đổi có thể ảnh hưởng nhiều flow khác
- Task có `risk: high` do touch vào luồng checkout critical

## Gợi ý công cụ

Repo code đích có sẵn skill `/code-review` — khuyến khích dùng để đọc diff + chạy test một cách có cấu trúc.

## Trả kết quả

Sau khi review xong, báo lại cho control-tower bằng lệnh:
```
/verdict OMS-001 <pass|changes> --reviewer @<tên bạn> [--commit <hash>] [--notes "..."]
```
