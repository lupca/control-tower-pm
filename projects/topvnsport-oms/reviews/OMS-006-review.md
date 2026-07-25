---
id: OMS-006
task_path: projects/topvnsport-oms/tasks/OMS-006-fix-security-critical.md
project: topvnsport-oms
result_ref: 3116bf3
executor: @gpt-5.6-luna-high
reviewer: "@claude-opus"
status: passed
issued: 2026-07-25
verdict: pass
verdict_date: 2026-07-25
---

# Phiếu Review: OMS-006 — Fix Fernet secret fallback + wildcard CORS + gate test-OTP endpoint

- Dự án: topvnsport-oms (`/home/lupca/projects/topvnsport`)
- Task gốc: `projects/topvnsport-oms/tasks/OMS-006-fix-security-critical.md`
- Result-ref: 3116bf3
- Executor: @gpt-5.6-luna-high
- Reviewer: @claude-opus
- Ngày phát phiếu: 2026-07-25

## Verdict: PASS

## Acceptance Criteria Verification

- [x] **AC1**: `FERNET_KEY` không có fallback value trong models.py/docker-compose
  - `models.py:104-106`: Raises `RuntimeError` if missing
  - `utils/crypto.py:10-11`: Raises `RuntimeError` if missing
  - `docker-compose.prod.yml:25`: Pass-through from host env (`- FERNET_KEY`)
  - `docker-compose.yml:32`: Uses new key `2Jf7oG7N4...` (different from old hardcoded)
  - Verified: `grep -r "lz_K8Z8d" OMS/` → empty

- [x] **AC2**: CORS không còn `allow_origins=["*"]` với credentials
  - `main.py:207-217`: Uses `cors_origins` list from `CORS_ALLOWED_ORIGINS` env var
  - Verified: `grep 'allow_origins=\["\*"\]' OMS/backend/main.py` → empty

- [x] **AC3**: `/test-last-otp` endpoint yêu cầu explicit flag `ALLOW_TEST_OTP_ENDPOINT=true`
  - `otp.py:45-46`: Checks `os.getenv("ALLOW_TEST_OTP_ENDPOINT", "").lower() != "true"` → 404
  - Test `test_test_last_otp_requires_explicit_flag` passes

- [x] **AC4**: SMS/Zalo config mutation yêu cầu admin role
  - `config.py:48-49`: `if current_user.get("role") != "admin"` → 403
  - Test `test_sms_config_mutation_requires_admin` passes

- [x] **AC5**: Xác định root cause thật của 500
  - Commit message: "fix config_value schema drift"
  - `models.py:98`: `impl = SqlString` (unbounded, no length constraint)
  - Code uses unbounded type so NEW DB tables won't have the constraint

- [x] **AC6**: PUT `/api/configs/sms` với token dài trả về 200
  - Test `test_sms_config_endpoints_support_long_tokens` passes with ~500 char tokens

- [x] **AC7**: Thêm test PUT/GET với token dài
  - `tests/test_config.py::test_sms_config_endpoints_support_long_tokens` added

- [x] **AC8**: Project Gate — executor did NOT modify prod DB
  - No migration or ALTER TABLE in commit
  - Executor correctly followed instruction to not touch prod without user confirmation

## Definition of Done

- [x] Toàn bộ AC pass
- [x] Test liên quan xanh 100%: All 14 selected tests pass
- [x] Không regression: Full suite 42 tests pass
- [x] Reviewer khác executor: @claude-opus ≠ @gpt-5.6-luna-high

## Test Results

```
tests/test_config.py::test_sms_config_endpoints PASSED
tests/test_config.py::test_sms_config_endpoints_support_long_tokens PASSED
tests/test_config.py::test_sms_config_mutation_requires_admin PASSED
test_main.py::test_get_zalo_config_returns_all_masked_fields PASSED
test_main.py::test_update_zalo_config_only_persists_unmasked_fields PASSED
test_main.py::test_zalo_webhook_uses_admin_secret_key PASSED
test_main.py::test_zalo_token_refresh_updates_system_config PASSED
tests/test_otp.py::test_test_last_otp_requires_explicit_flag PASSED
tests/test_webhooks.py::test_zalo_webhook_endpoint PASSED
======================== 42 passed, 2 warnings in 7.58s ========================
```

## Risk Items Verified

1. **Excluded file**: `sync_all_data_from_prod_to_local.sh` NOT in commit ✅
2. **No hardcoded keys**: `grep -r "lz_K8Z8d" OMS/` → empty ✅
3. **docker-compose.prod.yml**: Reads `FERNET_KEY`/`CORS_ALLOWED_ORIGINS` from env ✅
4. **Prod DB untouched**: No migration/ALTER in commit per AC8 ✅

## Post-Deploy Actions Required

1. **FERNET_KEY on prod**: Ensure `FERNET_KEY` is set via host env/secret before deploy (app will fail-fast if missing)
2. **Prod schema drift**: If prod DB `system_configs.config_value` is still VARCHAR(500), run:
   ```sql
   ALTER TABLE system_configs ALTER COLUMN config_value TYPE TEXT;
   ```
   This requires **user confirmation** per Project Gate.
3. **Zalo token rotation**: User must rotate Zalo App Secret Key / OA Access Token / OA Refresh Token that were leaked in `index.md`

## Files Changed (11)

- `OMS/backend/main.py` — CORS explicit origins
- `OMS/backend/models.py` — Fernet fail-fast + logging
- `OMS/backend/routers/config.py` — Admin role check
- `OMS/backend/routers/otp.py` — ALLOW_TEST_OTP_ENDPOINT gate
- `OMS/backend/test_main.py` — New Fernet key + OTP flag
- `OMS/backend/tests/conftest.py` — New Fernet key + OTP flag
- `OMS/backend/tests/test_config.py` — Long token + admin role tests
- `OMS/backend/tests/test_otp.py` — OTP flag test
- `OMS/backend/utils/crypto.py` — Fernet fail-fast + logging
- `OMS/docker-compose.prod.yml` — Env pass-through
- `OMS/docker-compose.yml` — New dev key
