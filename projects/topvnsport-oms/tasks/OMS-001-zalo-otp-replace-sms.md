---
id: OMS-001
title: "Thay thế SMS OTP bằng Zalo OTP (ZBS Template Message)"
status: in-review
priority: high
risk: high
deadline: null
executor: "@gpt-5.6-sol"
reviewer: "@claude-opus"
result_ref: "topvnsport@main"
depends_on: []
files:
  - OMS/backend/services/sms_service.py
  - OMS/backend/services/zalo_service.py
  - OMS/backend/main.py
  - OMS/backend/models.py
  - OMS/backend/requirements.txt
  - OMS/backend/test_main.py
  - e2e_tests/tests/test_storefront_otp_flow.py
flows:
  - send_otp
  - verify_otp
  - update_sms_config
  - get_sms_config
  - create_order
tests:
  - OMS/backend/test_main.py::test_send_otp_rate_limit_and_lockout
  - OMS/backend/test_main.py::test_order_creation_otp_security
  - OMS/backend/test_main.py::test_otp_hashing
  - OMS/backend/test_main.py::test_sms_provider_failure
  - OMS/backend/test_main.py::test_otp_verification_flow
  - e2e_tests/tests/test_storefront_otp_flow.py::test_storefront_otp_checkout_flow
dispatched: 2026-07-23
in_review: 2026-07-23
predicted_success: high
prediction_factors:
  score: 0.8
  deductions:
    - "hits_bridge_node (test_storefront_otp_checkout_flow): -0.2"
created: 2026-07-23
updated: 2026-07-23
plan_approved: null
---

# OMS-001: Thay thế SMS OTP bằng Zalo OTP (ZBS Template Message)

> Dự án: [[projects/topvnsport-oms/topvnsport-oms]]

## Tiêu chí nghiệm thu (AC)

- [ ] **AC1**: `sms_service.py` bị xóa hoàn toàn, thay bằng `zalo_service.py` với hàm `send_zalo_otp(phone, otp, access_token, template_id)` gọi Zalo API `POST https://business.openapi.zalo.me/message/template`
- [ ] **AC2**: Endpoint `/api/sms/send-otp` gọi `zalo_service.send_zalo_otp` thay vì `sms_service.send_speed_sms`; fetch `zalo_access_token` và `zalo_template_id` từ `SystemConfig`
- [ ] **AC3**: Khi Zalo trả lỗi (`-118` SĐT không có Zalo, `-115` hết quota, `-108` format sai), API trả HTTP 400 với message tiếng Việt rõ ràng, không fallback SMS
- [ ] **AC4**: Model `OtpVerification` có thêm field `zalo_message_id: Optional[str]` để map webhook
- [ ] **AC5**: Endpoint webhook `/api/sms/zalo-webhook` lắng nghe event `user_received_message`, verify signature HMAC-SHA256 với `OA_SECRET_KEY`, update `provider_status = "DELIVERED"` vào record tương ứng
- [ ] **AC6**: Token refresh tự động: `BackgroundScheduler` (apscheduler) chạy mỗi 20 giờ, gọi `POST https://oauth.zaloapp.com/v4/oa/access_token` với refresh_token, update cả `access_token` và `refresh_token` mới vào `SystemConfig`
- [ ] **AC7**: `requirements.txt` có thêm `apscheduler==3.10.4`
- [ ] **AC8**: Tất cả unit tests trong `test_main.py` liên quan OTP được update mock từ `sms_service` sang `zalo_service`, pass 100%
- [ ] **AC9**: E2E test `test_storefront_otp_checkout_flow` vẫn pass (dùng test-endpoint bypass)

## Verification

```bash
# Unit tests
cd /home/lupca/projects/topvnsport/OMS/backend
pytest test_main.py -k "otp" -v

# E2E test
cd /home/lupca/projects/topvnsport/e2e_tests
pytest tests/test_storefront_otp_flow.py -v

# Verify sms_service.py deleted
test ! -f /home/lupca/projects/topvnsport/OMS/backend/services/sms_service.py && echo "PASS: sms_service.py deleted"

# Verify zalo_service.py exists
test -f /home/lupca/projects/topvnsport/OMS/backend/services/zalo_service.py && echo "PASS: zalo_service.py created"

# Verify apscheduler in requirements
grep -q "apscheduler" /home/lupca/projects/topvnsport/OMS/backend/requirements.txt && echo "PASS: apscheduler added"

# Verify zalo_message_id field
grep -q "zalo_message_id" /home/lupca/projects/topvnsport/OMS/backend/models.py && echo "PASS: zalo_message_id field added"
```

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| User không có Zalo = không checkout được | High | PO đã xác nhận chấp nhận risk này |
| Zalo quota limit (-115) khi traffic cao | Medium | Monitor và alert khi gần limit |
| Token refresh race condition | Medium | Dùng lock mechanism hoặc atomic update |
| `test_storefront_otp_checkout_flow` là bridge node | High | Review kỹ E2E test, chạy nhiều lần |

## Plan

### 1. Tạo `OMS/backend/services/zalo_service.py`
```python
async def send_zalo_otp(phone: str, otp: str, access_token: str, template_id: str) -> dict:
    # POST https://business.openapi.zalo.me/message/template
    # Headers: access_token
    # Body: phone (format 84xxx), template_data {otp}
    # Return: {status, error_code, message_id} hoặc {status: failed, error_code, failed_reason}

async def refresh_zalo_token(app_id: str, secret_key: str, refresh_token: str) -> dict:
    # POST https://oauth.zaloapp.com/v4/oa/access_token
    # Return: {access_token, refresh_token} mới
```

### 2. Update `OMS/backend/models.py` (line ~143)
- Thêm `zalo_message_id = Column(String(100), nullable=True)` vào `OtpVerification`

### 3. Update `OMS/backend/main.py`
- **Lines 28**: `import services.zalo_service` thay `import services.sms_service`
- **Lines 1098-1104**: Fetch `zalo_access_token`, `zalo_template_id` thay vì `speed_sms_token`
- **Lines 1120-1126**: Call `zalo_service.send_zalo_otp()` thay `sms_service.send_speed_sms()`
- **Lines 1129**: Lưu `zalo_message_id` từ response vào `otp_ver`
- **Lines 1135-1136**: HTTP 400 với message Việt khi Zalo fail, không fallback
- **After line 1243**: Thêm endpoint `POST /api/sms/zalo-webhook` — verify HMAC-SHA256, update `provider_status`
- **startup event**: Khởi tạo `BackgroundScheduler`, job mỗi 20h gọi `refresh_zalo_token()`, update `SystemConfig`

### 4. Update `OMS/backend/requirements.txt`
- Thêm `apscheduler==3.10.4`

### 5. Update `OMS/backend/test_main.py`
- **Lines 367-377**: Fixture `configure_sms` → `configure_zalo_otp`, seed `zalo_access_token`, `zalo_template_id`
- **Lines 385, 412, 425, 443**: `monkeypatch.setattr("services.zalo_service.send_zalo_otp", ...)`
- Thêm test cases: `test_send_zalo_otp_invalid_phone`, `test_send_zalo_otp_unregistered_zalo`, `test_zalo_webhook_valid_signature`, `test_zalo_webhook_invalid_signature`

### 6. Verify E2E `e2e_tests/tests/test_storefront_otp_flow.py`
- Chạy `pytest tests/test_storefront_otp_flow.py` — test dùng bypass endpoint nên không cần thay đổi

### 7. Xóa `OMS/backend/services/sms_service.py`
- `rm OMS/backend/services/sms_service.py`

### Order of execution
```
[2] models.py → [1] zalo_service.py → [4] requirements.txt → [3] main.py → [5] test_main.py → [6] verify E2E → [7] delete sms_service.py
```

## Sub-tasks

- [ ] Tạo `OMS/backend/services/zalo_service.py` với `send_zalo_otp()` và `refresh_zalo_token()`
- [ ] Update `OMS/backend/models.py`: thêm `zalo_message_id` vào `OtpVerification`
- [ ] Update `OMS/backend/main.py`: thay call SMS bằng Zalo, thêm webhook endpoint, setup scheduler
- [ ] Update `OMS/backend/requirements.txt`: thêm apscheduler
- [ ] Update `OMS/backend/test_main.py`: mock `zalo_service` thay vì `sms_service`
- [ ] Verify E2E test `test_storefront_otp_flow.py` vẫn pass
- [ ] Xóa `OMS/backend/services/sms_service.py`
