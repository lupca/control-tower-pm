---
id: OMS-003
task_path: projects/topvnsport-oms/tasks/OMS-003-remove-bypass-otp-backdoor.md
project: topvnsport-oms
result_ref: "topvnsport@main (commit abc27d7)"
executor: "@gpt-5.6-sol"
reviewer: null
status: pending
issued: 2026-07-23
verdict: null
verdict_date: null
---

# Phiếu Review: OMS-003 — Xóa BYPASS_OTP_TOKEN backdoor

- Dự án: TopVNSport OMS (`/home/lupca/projects/topvnsport`)
- Task gốc: `projects/topvnsport-oms/tasks/OMS-003-remove-bypass-otp-backdoor.md`
- Result-ref: topvnsport@main (commit abc27d7)
- Executor: @gpt-5.6-sol
- Ngày phát phiếu: 2026-07-23

## Acceptance Criteria cần verify

- [ ] **AC1**: Xóa điều kiện `if payload.verification_token != "BYPASS_OTP_TOKEN"` tại `main.py` — mọi order PHẢI có OTP token hợp lệ từ DB
- [ ] **AC2**: Update `test_full_flow.py` — dùng OTP thật từ `/api/sms/test-last-otp`
- [ ] **AC3**: Update `test_storefront_otp_flow.py` — dùng OTP thật từ test endpoint
- [ ] **AC4**: Không còn string `"BYPASS_OTP_TOKEN"` trong codebase (grep = 0 matches)
- [ ] **AC5**: Tất cả E2E tests vẫn pass với OTP thật

## Definition of Done
- [ ] Toàn bộ AC pass
- [ ] Tests xanh 100%
- [ ] Reviewer khác executor (bạn ≠ @gpt-5.6-sol)

## Test gợi ý

```bash
grep -rn "BYPASS_OTP_TOKEN" /home/lupca/projects/topvnsport --include="*.py" --include="*.tsx" && echo "FAIL" || echo "PASS"

cd /home/lupca/projects/topvnsport/e2e_tests
pytest tests/test_full_flow.py tests/test_storefront_otp_flow.py -v
```

## Trả kết quả
```
/verdict OMS-003 <pass|changes> --reviewer @<tên bạn> --commit abc27d7
```
