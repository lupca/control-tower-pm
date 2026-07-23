---
id: OMS-002
title: "Frontend Zalo OTP - Chặn luồng khi SĐT không có Zalo"
status: dispatched
priority: high
risk: normal
deadline: null
executor: "@gpt-5.6-sol"
reviewer: "@claude-opus"
result_ref: null
depends_on: [OMS-001]
files:
  - web/src/components/CartModal.tsx
  - web/src/components/OtpModal.tsx
  - e2e_tests/tests/test_storefront_otp_flow.py
flows:
  - storefront-checkout
tests:
  - e2e_tests/tests/test_storefront_otp_flow.py::test_storefront_otp_checkout_flow
dispatched: 2026-07-23
in_review: null
predicted_success: high
prediction_factors:
  score: 0.9
  deductions:
    - "depends_on OMS-001: -0.1"
created: 2026-07-23
updated: 2026-07-23
---

# OMS-002: Frontend Zalo OTP - Chặn luồng khi SĐT không có Zalo

> Dự án: [[projects/topvnsport-oms/topvnsport-oms]]

## Tiêu chí nghiệm thu (AC)

- [ ] **AC1**: `CartModal.tsx` gọi `sportApi.sendOtp(phone)` TRƯỚC khi mở OtpModal
- [ ] **AC2**: Nếu API sendOtp trả lỗi (400) → hiện `popupService.alert(err.message)` trực tiếp, KHÔNG mở OtpModal
- [ ] **AC3**: `OtpModal.tsx` xóa auto-send `triggerSendOtp()` trong `useEffect` khi `isOpen` thay đổi
- [ ] **AC4**: `OtpModal.tsx` xóa hoàn toàn bypass button `<button onClick={() => onSuccess('BYPASS_OTP_TOKEN')}>`
- [ ] **AC5**: Khi modal mở, chỉ reset state (`setOtpCode('')`, `setCooldown(60)`)
- [ ] **AC6**: E2E test `test_storefront_checkout_zalo_unregistered_block_ui` pass — modal KHÔNG hiện khi Zalo fail
- [ ] **AC7**: E2E test `test_storefront_otp_resend_cooldown_ui` pass — cooldown hoạt động đúng
- [ ] **AC8**: E2E test `test_storefront_otp_invalid_input` pass — nút xác nhận disabled khi OTP < 6 ký tự

## Verification

```bash
# E2E tests
cd /home/lupca/projects/topvnsport/e2e_tests
pytest tests/test_storefront_otp_flow.py -v

# Verify bypass button removed
grep -r "BYPASS_OTP_TOKEN" /home/lupca/projects/topvnsport/web/src/components/OtpModal.tsx && echo "FAIL: bypass still exists" || echo "PASS: bypass removed"

# Verify auto-send removed (no triggerSendOtp in useEffect with isOpen)
grep -A5 "useEffect.*isOpen" /home/lupca/projects/topvnsport/web/src/components/OtpModal.tsx | grep -q "triggerSendOtp" && echo "FAIL: auto-send still exists" || echo "PASS: auto-send removed"
```

## Plan

### 1. Update `web/src/components/CartModal.tsx`
- Tìm hàm `handleCheckoutSubmit`
- Thêm `setIsSubmitting(true)` + gọi `sportApi.sendOtp(phone)`
- Nếu success → `setIsOtpModalOpen(true)`
- Nếu fail → `popupService.alert(err.message)`, giữ nguyên màn hình

### 2. Update `web/src/components/OtpModal.tsx`
- Xóa `triggerSendOtp()` trong `useEffect` khi `isOpen` thay đổi
- Xóa đoạn bypass button: `<button onClick={() => onSuccess('BYPASS_OTP_TOKEN')}> Bỏ qua xác nhận </button>`
- Giữ nguyên logic reset state khi modal mở

### 3. Add E2E tests
- `test_storefront_checkout_zalo_unregistered_block_ui`: Mock 400 → verify modal không hiện
- `test_storefront_otp_resend_cooldown_ui`: Verify cooldown logic
- `test_storefront_otp_invalid_input`: Verify disabled button khi OTP < 6

### Order of execution
```
[1] CartModal.tsx → [2] OtpModal.tsx → [3] E2E tests
```

## Sub-tasks

- [ ] Update `CartModal.tsx`: gọi sendOtp TRƯỚC khi mở modal, show error nếu fail
- [ ] Update `OtpModal.tsx`: xóa auto-send, xóa bypass button
- [ ] Add E2E test `test_storefront_checkout_zalo_unregistered_block_ui`
- [ ] Add E2E test `test_storefront_otp_resend_cooldown_ui`
- [ ] Add E2E test `test_storefront_otp_invalid_input`
- [ ] Verify tất cả E2E tests pass
