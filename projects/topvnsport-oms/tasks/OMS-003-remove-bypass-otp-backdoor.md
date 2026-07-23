---
id: OMS-003
title: "Xóa BYPASS_OTP_TOKEN backdoor khỏi production"
status: done
priority: high
risk: high
deadline: null
executor: "@gpt-5.6-sol"
reviewer: "@claude-opus"
result_ref: "topvnsport@main (commit abc27d7)"
depends_on: [OMS-001, OMS-002]
files:
  - OMS/backend/main.py
  - e2e_tests/tests/test_full_flow.py
  - e2e_tests/tests/test_storefront_otp_flow.py
flows:
  - create_order
  - storefront-checkout
tests:
  - e2e_tests/tests/test_full_flow.py::test_full_flow
  - e2e_tests/tests/test_storefront_otp_flow.py::test_storefront_otp_checkout_flow
dispatched: 2026-07-23
in_review: null
predicted_success: high
prediction_factors:
  score: 0.85
  deductions:
    - "risk_high: -0.15"
created: 2026-07-23
updated: 2026-07-23
---

# OMS-003: Xóa BYPASS_OTP_TOKEN backdoor khỏi production

> Dự án: [[projects/topvnsport-oms/topvnsport-oms]]

## Tiêu chí nghiệm thu (AC)

- [x] **AC1**: Xóa điều kiện `if payload.verification_token != "BYPASS_OTP_TOKEN"` tại `main.py:739` — mọi order PHẢI có OTP token hợp lệ từ DB
- [x] **AC2**: Update `test_full_flow.py` — thay `"verification_token": "BYPASS_OTP_TOKEN"` bằng flow lấy OTP thật từ `/api/sms/test-last-otp`
- [x] **AC3**: Update `test_storefront_otp_flow.py` — tương tự, dùng OTP thật từ test endpoint
- [x] **AC4**: Không còn string `"BYPASS_OTP_TOKEN"` trong codebase (grep = 0 matches)
- [x] **AC5**: Tất cả E2E tests vẫn pass với OTP thật

## Verification

```bash
# Verify no BYPASS_OTP_TOKEN remaining
cd /home/lupca/projects/topvnsport
grep -rn "BYPASS_OTP_TOKEN" --include="*.py" --include="*.tsx" --include="*.ts" && echo "FAIL" || echo "PASS: no backdoor"

# E2E tests
cd /home/lupca/projects/topvnsport/e2e_tests
pytest tests/test_full_flow.py tests/test_storefront_otp_flow.py -v
```

## Plan

### 1. Update `OMS/backend/main.py` (line ~739)
```python
# BEFORE:
if payload.verification_token != "BYPASS_OTP_TOKEN":
    otp_ver = db.query(models.OtpVerification).filter(...)
    ...
# AFTER:
otp_ver = db.query(models.OtpVerification).filter(
    models.OtpVerification.verification_token == payload.verification_token
).first()
if not otp_ver:
    raise HTTPException(status_code=400, detail="Token xác thực không hợp lệ")
# ... rest of validation
```

### 2. Update `e2e_tests/tests/test_full_flow.py` (line ~32)
```python
# BEFORE:
"verification_token": "BYPASS_OTP_TOKEN",

# AFTER:
# 1. Call /api/sms/send-otp
# 2. Get OTP from /api/sms/test-last-otp
# 3. Call /api/sms/verify-otp → get real verification_token
# 4. Use that token in order creation
```

### 3. Update `e2e_tests/tests/test_storefront_otp_flow.py` (line ~127)
- Tương tự như trên

## Sub-tasks

- [ ] Xóa backdoor condition trong `main.py`
- [ ] Update `test_full_flow.py` với OTP thật
- [ ] Update `test_storefront_otp_flow.py` với OTP thật
- [ ] Verify grep BYPASS_OTP_TOKEN = 0
- [ ] Run all E2E tests
