---
id: OMS-002
task_path: projects/topvnsport-oms/tasks/OMS-002-frontend-zalo-otp.md
project: topvnsport-oms
result_ref: topvnsport@main
executor: "@gpt-5.6-sol"
reviewer: null
status: pending
issued: 2026-07-23
verdict: null
verdict_date: null
---

# Phiếu Review: OMS-002 — Frontend Zalo OTP - Chặn luồng khi SĐT không có Zalo

- Dự án: TopVNSport OMS (`/home/lupca/projects/topvnsport`)
- Task gốc: `projects/topvnsport-oms/tasks/OMS-002-frontend-zalo-otp.md`
- Result-ref: topvnsport@main
- Executor: @gpt-5.6-sol
- Ngày phát phiếu: 2026-07-23

## Acceptance Criteria cần verify

- [ ] **AC1**: `CartModal.tsx` gọi `sportApi.sendOtp(phone)` TRƯỚC khi mở OtpModal
- [ ] **AC2**: Nếu API sendOtp trả lỗi (400) → hiện `popupService.alert(err.message)` trực tiếp, KHÔNG mở OtpModal
- [ ] **AC3**: `OtpModal.tsx` xóa auto-send `triggerSendOtp()` trong `useEffect` khi `isOpen` thay đổi
- [ ] **AC4**: `OtpModal.tsx` xóa hoàn toàn bypass button `<button onClick={() => onSuccess('BYPASS_OTP_TOKEN')}>`
- [ ] **AC5**: Khi modal mở, chỉ reset state (`setOtpCode('')`, `setCooldown(60)`)
- [ ] **AC6**: E2E test `test_storefront_checkout_zalo_unregistered_block_ui` pass — modal KHÔNG hiện khi Zalo fail
- [ ] **AC7**: E2E test `test_storefront_otp_resend_cooldown_ui` pass — cooldown hoạt động đúng
- [ ] **AC8**: E2E test `test_storefront_otp_invalid_input` pass — nút xác nhận disabled khi OTP < 6 ký tự

## Definition of Done (AGENTS.md mục 3)

- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%:
  - `e2e_tests/tests/test_storefront_otp_flow.py::test_storefront_otp_checkout_flow`
  - `e2e_tests/tests/test_storefront_otp_flow.py::test_storefront_checkout_zalo_unregistered_block_ui`
  - `e2e_tests/tests/test_storefront_otp_flow.py::test_storefront_otp_resend_cooldown_ui`
  - `e2e_tests/tests/test_storefront_otp_flow.py::test_storefront_otp_invalid_input`
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (bạn đang review, hãy xác nhận bạn ≠ @gpt-5.6-sol)

## Test gợi ý chạy trong repo code

```bash
# E2E tests
cd /home/lupca/projects/topvnsport/e2e_tests
pytest tests/test_storefront_otp_flow.py -v

# Quick verification checks
grep -r "BYPASS_OTP_TOKEN" /home/lupca/projects/topvnsport/web/src/components/OtpModal.tsx && echo "FAIL: bypass still exists" || echo "PASS: bypass removed"

grep -A5 "useEffect.*isOpen" /home/lupca/projects/topvnsport/web/src/components/OtpModal.tsx | grep -q "triggerSendOtp" && echo "FAIL: auto-send still exists" || echo "PASS: auto-send removed"

# Frontend build check
cd /home/lupca/projects/topvnsport/web && npm run build
```

## Câu hỏi rủi ro (từ code-review-graph, tĩnh)

| Priority | Category | Question |
|----------|----------|----------|
| high | bridge_node | `test_full_flow` là critical connector — verify flow checkout không bị break |
| medium | dependency | Task phụ thuộc OMS-001 — verify backend Zalo API đã hoạt động trước khi test FE |

**Lưu ý đặc biệt cho task này:**
- Bypass button đã bị xóa — user PHẢI nhập OTP thật để checkout
- Auto-send đã chuyển sang CartModal — verify không có double-send

## Gợi ý công cụ

Repo code đích có sẵn skill `/code-review` — khuyến khích dùng để đọc diff + chạy test một cách có cấu trúc.

## Trả kết quả

Sau khi review xong, báo lại cho control-tower bằng lệnh:
```
/verdict OMS-002 <pass|changes> --reviewer @<tên bạn> [--commit <hash>] [--notes "..."]
```
