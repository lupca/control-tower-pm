---
id: OMS-004
title: "Cập nhật trang cấu hình Admin: SMS → Zalo OTP"
status: done
priority: high
risk: normal
deadline: null
executor: "@gpt-5.6-sol"
reviewer: "@claude-opus"
result_ref: "topvnsport@main (commit abc27d7)"
depends_on: [OMS-001]
files:
  - OMS/frontend/src/app/settings/sms/page.tsx
  - OMS/backend/main.py
  - OMS/backend/schemas/auth.py
flows:
  - admin-settings
tests: []
dispatched: 2026-07-23
in_review: null
predicted_success: high
prediction_factors:
  score: 0.9
  deductions: []
created: 2026-07-23
updated: 2026-07-23
---

# OMS-004: Cập nhật trang cấu hình Admin: SMS → Zalo OTP

> Dự án: [[projects/topvnsport-oms/topvnsport-oms]]

## Tiêu chí nghiệm thu (AC)

- [x] **AC1**: Đổi title trang từ "Cấu hình SMS OTP (SpeedSMS)" → "Cấu hình Zalo OTP"
- [x] **AC2**: Form có 5 fields thay vì 1:
  - `zalo_app_id` (text, required)
  - `zalo_secret_key` (password, required) — dùng cho webhook HMAC verify
  - `zalo_access_token` (password, required)
  - `zalo_refresh_token` (password, required)
  - `zalo_template_id` (text, required)
- [x] **AC3**: Backend endpoint `GET /api/configs/sms` trả về tất cả 5 config keys (masked)
- [x] **AC4**: Backend endpoint `PUT /api/configs/sms` nhận object với 5 fields, chỉ update field nào thay đổi (không chứa `*`)
- [x] **AC5**: Xóa mọi reference đến `speed_sms_token` trong codebase (frontend + backend config endpoints)
- [x] **AC6**: UI hiển thị status "Token hợp lệ" nếu access_token đã được cấu hình

## Verification

```bash
# Verify no speed_sms references
cd /home/lupca/projects/topvnsport
grep -rn "speed_sms\|SpeedSMS" --include="*.tsx" --include="*.ts" --include="*.py" | grep -v test | grep -v __pycache__ && echo "FAIL" || echo "PASS"

# Frontend build
cd /home/lupca/projects/topvnsport/OMS/frontend && npm run build

# Manual: Open http://localhost:3001/settings/sms → verify 5 fields appear
```

## Plan

### 1. Update `OMS/backend/schemas/auth.py`
```python
class ZaloConfigOut(BaseModel):
    zalo_app_id: str
    zalo_secret_key: str  # masked
    zalo_access_token: str  # masked
    zalo_refresh_token: str  # masked
    zalo_template_id: str

class ZaloConfigUpdate(BaseModel):
    zalo_app_id: Optional[str] = None
    zalo_secret_key: Optional[str] = None
    zalo_access_token: Optional[str] = None
    zalo_refresh_token: Optional[str] = None
    zalo_template_id: Optional[str] = None
```

### 2. Update `OMS/backend/main.py` endpoints (~line 1472-1500)
- `GET /api/configs/sms` → fetch all 5 zalo_* keys, mask each
- `PUT /api/configs/sms` → update only fields that don't contain `*`

### 3. Update `OMS/frontend/src/app/settings/sms/page.tsx`
- Change schema to 5 fields
- Change form to 5 input groups
- Update title/description
- Each field: password type + show/hide toggle
- Only submit fields that changed (không có `*`)

## Sub-tasks

- [ ] Update backend schemas (ZaloConfigOut, ZaloConfigUpdate)
- [ ] Update backend GET endpoint — fetch 5 keys
- [ ] Update backend PUT endpoint — update changed fields only
- [ ] Update frontend form — 5 fields với validation
- [ ] Update frontend title/description
- [ ] Remove all speed_sms references
- [ ] Test UI manually
