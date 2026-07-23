---
id: OMS-004
task_path: projects/topvnsport-oms/tasks/OMS-004-zalo-admin-config.md
project: topvnsport-oms
result_ref: "topvnsport@main (commit abc27d7)"
executor: "@gpt-5.6-sol"
reviewer: null
status: pending
issued: 2026-07-23
verdict: null
verdict_date: null
---

# Phiếu Review: OMS-004 — Cập nhật trang cấu hình Admin: SMS → Zalo OTP

- Dự án: TopVNSport OMS (`/home/lupca/projects/topvnsport`)
- Task gốc: `projects/topvnsport-oms/tasks/OMS-004-zalo-admin-config.md`
- Result-ref: topvnsport@main (commit abc27d7)
- Executor: @gpt-5.6-sol
- Ngày phát phiếu: 2026-07-23

## Acceptance Criteria cần verify

- [ ] **AC1**: Đổi title trang từ "Cấu hình SMS OTP (SpeedSMS)" → "Cấu hình Zalo OTP"
- [ ] **AC2**: Form có 5 fields: zalo_app_id, zalo_secret_key, zalo_access_token, zalo_refresh_token, zalo_template_id
- [ ] **AC3**: Backend GET trả về 5 config keys (masked)
- [ ] **AC4**: Backend PUT chỉ update field thay đổi (không chứa `*`)
- [ ] **AC5**: Xóa mọi reference đến `speed_sms_token`
- [ ] **AC6**: UI hiển thị "Token hợp lệ" nếu access_token đã cấu hình

## Definition of Done
- [ ] Toàn bộ AC pass
- [ ] Frontend build pass
- [ ] Reviewer khác executor (bạn ≠ @gpt-5.6-sol)

## Test gợi ý

```bash
grep -rn "speed_sms\|SpeedSMS" /home/lupca/projects/topvnsport --include="*.tsx" --include="*.py" | grep -v test && echo "FAIL" || echo "PASS"

cd /home/lupca/projects/topvnsport/OMS/frontend && npm run build
```

## Trả kết quả
```
/verdict OMS-004 <pass|changes> --reviewer @<tên bạn> --commit abc27d7
```
