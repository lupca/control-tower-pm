---
id: OMS-006
title: "Fix Fernet secret fallback + wildcard CORS + gate test-OTP endpoint"
status: done
priority: urgent
risk: high
deadline: null
executor: "@gpt-5.6-luna-high"
reviewer: "@claude-opus"
result_ref: "3116bf3"
depends_on: []
files:
  - OMS/backend/main.py
  - OMS/backend/models.py
  - OMS/backend/routers/otp.py
  - OMS/backend/routers/config.py
  - OMS/backend/tests/test_config.py
  - OMS/docker-compose.prod.yml
flows: [login, checkout]
tests:
  - OMS/backend/test_main.py
  - OMS/backend/test_main.py::test_get_zalo_config_returns_all_masked_fields
  - OMS/backend/test_main.py::test_update_zalo_config_only_persists_unmasked_fields
  - OMS/backend/test_main.py::test_zalo_token_refresh_updates_system_config
  - OMS/backend/test_main.py::test_zalo_webhook_uses_admin_secret_key
  - OMS/backend/tests/test_webhooks.py::test_zalo_webhook_endpoint
  - OMS/backend/tests/test_config.py::test_sms_config_endpoints
dispatched: 2026-07-25
in_review: 2026-07-25
predicted_success: medium
prediction_factors:
  score: 0.5
  deductions:
    - "risk_high: -0.2 (security)"
    - "multiple_files: -0.05"
    - "unresolved root cause: -0.15 (2 competing hypotheses for the live 500 — Fernet key mismatch vs system_configs.config_value schema drift — needs live diagnosis on both envs before fix)"
    - "possible prod DB schema change: -0.1 (Project Gate: needs explicit User confirm before executor runs any ALTER/migrate, independent of bypass mode)"
confidence_interval: [0.35, 0.65]
created: 2026-07-25
updated: 2026-07-25
---

# OMS-006: Fix Fernet secret fallback + wildcard CORS + gate test-OTP endpoint

> Dự án: [[projects/topvnsport-oms/topvnsport-oms]]

## Bug Report (production 500 — inbox #7, 2026-07-25)

User báo lỗi: `PUT http://oms.topvnsport.com/oms-api/api/configs/sms` → 500 Internal Server Error, xảy ra trên **cả prod và local**, khi nhập Zalo App Secret Key / OA Access Token / OA Refresh Token (mỗi giá trị dài ~300–500 ký tự) + Template ID.

⚠️ **Secrets đã lộ**: giá trị token/secret thật đã bị dán cleartext vào `index.md` (git-tracked) khi báo lỗi. **User cần rotate lại toàn bộ Zalo App Secret Key / OA Access Token / OA Refresh Token này sau khi task này pass** — không phải AC code, nhưng bắt buộc phải làm.

### Root cause (giả thuyết, cần executor xác minh trước khi fix)

Cả GET và PUT `/api/configs/sms` đều đi qua `get_masked_zalo_config()` → decrypt từng `SystemConfig.config_value` (Fernet, class `EncryptedString` ở `models.py:91-116`). 2 giả thuyết, không loại trừ lẫn nhau:

1. **FERNET_KEY không nhất quán** (đây chính là AC1 gốc của task này) — khi thiếu `FERNET_KEY` env, code fallback về key hardcoded `models.py:100-103`. Nếu prod/local set (hoặc không set) `FERNET_KEY` khác nhau giữa các lần restart/container, data cũ mã hoá bằng key khác sẽ decrypt lỗi (`ValueError: Decryption failed`, không bị catch) → 500.
2. **Schema drift trên cột `config_value`** — repo không có alembic/migration, `Base.metadata.create_all()` không tự ALTER cột đã tồn tại. Nếu bảng `system_configs` được tạo trước khi `EncryptedString` đổi sang unbounded, cột có thể vẫn còn giới hạn độ dài cũ → ciphertext của access/refresh token dài (~500 ký tự, ~4/3 sau Fernet encode) bị truncate khi INSERT/UPDATE → decrypt lỗi ở lần đọc tiếp theo.

Cả 2 đường đều crash ở `EncryptedString.process_result_value()` (`models.py:110-116`) khi đọc lại config sau khi PUT — hiện tại lỗi bị wrap thành `ValueError` trần, không log rõ nguyên nhân gốc, nên phải điều tra trực tiếp trên cả 2 env trước khi fix (đừng đoán khi chưa xác nhận).

## Tiêu chí nghiệm thu (AC)

- [x] `FERNET_KEY` không có fallback value trong models.py/docker-compose
- [x] CORS không còn `allow_origins=["*"]` với credentials
- [x] `/test-last-otp` endpoint yêu cầu explicit flag `ALLOW_TEST_OTP_ENDPOINT=true`
- [x] SMS/Zalo config mutation yêu cầu admin role
- [x] **AC5 (bug repro)**: Xác định root cause thật của 500 (kiểm tra `FERNET_KEY` trên cả 2 env bằng `\d system_configs` + so sánh env var) trước khi fix.
- [x] **AC6 (bug repro)**: PUT `/api/configs/sms` với access_token/refresh_token dài thực tế (~500 ký tự, giống input lỗi gốc) trả về 200 trên cả local và prod, không còn 500.
- [x] **AC7 (regression test)**: Thêm test PUT/GET với token dài thực tế (~500 ký tự) vào `tests/test_config.py` — `test_sms_config_endpoints` hiện chỉ test giá trị ngắn.
- [x] **AC8 (Project Gate — cần User xác nhận riêng)**: Nếu root cause là schema drift, executor phải chạy ALTER TABLE (hoặc tương đương) trên `system_configs.config_value` ở **cả local và prod DB**. Đây là thay đổi cấu trúc DB → theo Project Gate của `topvnsport-oms` (`topvnsport-oms.md`), bắt buộc User xác nhận riêng trước khi thực thi trên prod, **kể cả khi coordination mode đang là `bypass`**.

## Verification

- `grep -r "lz_K8Z8d" OMS/` → empty (no hardcoded Fernet key)
- `grep 'allow_origins=\["\*"\]' OMS/backend/main.py` → empty
- Start service without ALLOW_TEST_OTP_ENDPOINT → `/test-last-otp` returns 404
- Non-admin user → PUT /api/configs/sms → 403
- `docker compose -f OMS/docker-compose.yml exec oms_db psql -U postgres -d oms_db -c "\d system_configs"` → confirm actual column type/length on local
- `docker compose -f OMS/docker-compose.yml exec oms_backend pytest tests/test_config.py test_main.py -k "config or zalo" -v` → 100% pass, including new long-token regression test
- Manual repro: PUT `/settings/sms` form với token dài thực tế → 200, không 500 (local + verify lại trên prod sau deploy)

## Plan

### 0. Diagnose trước (bắt buộc, chặn AC5) — không code trước khi biết root cause thật
1. Local: `docker compose -f OMS/docker-compose.yml exec oms_db psql -U postgres -d oms_db -c "\d system_configs"` → so `config_value` column type/length với kỳ vọng unbounded (`models.py:91-96`, `impl = SqlString` không length → Postgres VARCHAR không giới hạn). Local compose (`docker-compose.yml:32`) đã set `FERNET_KEY` cố định trùng đúng giá trị fallback hardcoded → **giả thuyết FERNET_KEY mismatch khó xảy ra ở local** (key luôn giống nhau dù có/không set env), nên nếu local cũng lỗi, ưu tiên nghi ngờ giả thuyết #2 (schema drift cột).
2. Prod: chạy `\d system_configs` tương tự trên prod DB + kiểm tra biến `FERNET_KEY` thật trên host prod (không có trong `docker-compose.prod.yml` đã đọc — không set `environment: FERNET_KEY` lẫn `env_file`, nên giá trị thật nằm ngoài repo, phải xác nhận trực tiếp trên server).
3. Nếu có thể, thử reproduce cục bộ: PUT payload với `zalo_access_token`/`zalo_refresh_token` dài ~500 ký tự (dùng input tương tự bug report, KHÔNG dùng lại token thật đã lộ) → xem traceback thật (log backend) để xác nhận lỗi đến từ đâu (INSERT truncate vs decrypt Fernet).

### 1. Fix theo root cause đã xác nhận ở bước 0
- Nếu **schema drift**: viết 1 script/lệnh ALTER (`ALTER TABLE system_configs ALTER COLUMN config_value TYPE TEXT;` hoặc tương đương) — **dừng lại xin User xác nhận riêng trước khi chạy trên prod** (AC8, Project Gate `topvnsport-oms`), chạy trên local trước để test.
- Nếu **FERNET_KEY mismatch**: xác định giá trị đúng cần dùng, đảm bảo prod set nhất quán qua secret nằm ngoài repo (không hardcode vào `docker-compose.prod.yml`) trước khi tiếp tục bước 2.
- Cả 2 trường hợp: sửa `EncryptedString.process_result_value` (`models.py:110-116`) để log/preserve exception gốc thay vì `raise ValueError(f"Decryption failed: {e}")` trần — giúp lần sau debug nhanh hơn, không phải chờ báo cáo user.

### 2. Fernet key fallback (AC1)
- `OMS/backend/models.py:98-103`: bỏ nhánh fallback hardcoded key, raise lỗi rõ ràng lúc khởi động (fail-fast) nếu thiếu `FERNET_KEY` khi `ENV != "development"`.
- `OMS/docker-compose.yml:32`: giữ nguyên (dev convenience, đã set rõ ràng) nhưng đổi giá trị sang key khác không trùng chuỗi hardcoded cũ, để không còn “default key” nào bị lộ qua git history.
- `OMS/docker-compose.prod.yml`: xác nhận `FERNET_KEY` được cấp qua secret/host env (không nằm trong compose file plaintext).

### 3. CORS (AC2)
- `OMS/backend/main.py:208-209`: thay `allow_origins=["*"]` bằng danh sách domain thật (`oms.topvnsport.com`, localhost dev) đọc từ env var, giữ `allow_credentials=True` chỉ khi origin explicit (không dùng `*` kèm credentials — vi phạm CORS spec).

### 4. Gate `/test-last-otp` (AC3)
- `OMS/backend/routers/otp.py:42-49`: thêm check `os.getenv("ALLOW_TEST_OTP_ENDPOINT") == "true"` bên cạnh điều kiện `INTEGRITY_MODE`/`ENV` hiện có, trả 404 khi flag tắt.

### 5. Admin role cho config mutation (AC4)
- `OMS/backend/routers/config.py::update_sms_config`: thêm role check dùng `get_current_user` (đã có sẵn field `role` trong `utils/auth.py`) — chỉ cho phép role admin PUT `/api/configs/sms`, trả 403 cho role khác. Áp dụng pattern tương tự chỗ khác trong codebase đã check role (nếu có) để nhất quán.

### 6. Regression test (AC7)
- `OMS/backend/tests/test_config.py`: thêm test PUT/GET với `zalo_access_token`/`zalo_refresh_token` dài thực tế (giả lập ~500 ký tự, dùng chuỗi test bất kỳ) để cover đúng lỗi đã xảy ra ở prod, tránh regression về sau.

### Thứ tự thực hiện
Diagnose (0) → fix root cause thật (1) → AC1/AC5/AC6 pass trước (bug đang chặn user, ưu tiên cao nhất) → AC2/AC3/AC4 (hardening có sẵn trong scope task) → AC7 (test) → verify lại AC6 trên prod sau deploy.

## Sub-tasks

- [ ] Remove Fernet key fallback, require env var
- [ ] Replace wildcard CORS với allowed origins list
- [ ] Add explicit flag check cho test-OTP endpoint
- [ ] Add admin role check cho config mutation endpoints
- [ ] Kiểm tra `FERNET_KEY` có nhất quán giữa local/prod không (trước khi fix fallback)
- [ ] Kiểm tra schema thật của cột `config_value` trên local + prod DB (`psql \d system_configs`)
- [ ] Nếu schema drift: ALTER cột `config_value` (cần User xác nhận riêng — xem AC8)
- [ ] Thêm test PUT/GET `/api/configs/sms` với token dài thực tế vào `tests/test_config.py`
- [ ] Preserve exception gốc trong `EncryptedString.process_result_value` thay vì raise `ValueError` trần (giúp debug lần sau)
- [ ] Note cho User sau khi pass: rotate Zalo App Secret Key / OA Access Token / OA Refresh Token đã lộ cleartext trong `index.md`

## Reference

- Debt file: `docs/TopVNSport - TODO & Technical Debt/oms/01_security_critical.md`
- Bug report gốc: `inbox.md` #7 (2026-07-25)

## Causal Analysis
- **Root cause**: Cột system_configs.config_value trong Postgres thật vẫn là VARCHAR(500) dù model SQLAlchemy (EncryptedString/SqlString) đã đổi sang unbounded — repo không có alembic/migration, Base.metadata.create_all() không tự ALTER cột đã tồn tại khi model đổi.
- **Mechanism**: Fernet-encrypt ciphertext của Zalo OA Access/Refresh Token dài (~300-500 ký tự thô) vượt quá 500 ký tự sau encode, bị truncate khi INSERT/UPDATE vào cột VARCHAR(500); lần đọc tiếp theo (GET và PUT đều gọi get_masked_zalo_config decrypt toàn bộ SystemConfig) decrypt dữ liệu bị truncate → Fernet raise lỗi không bắt được → 500.
- **Counterfactual**: Nếu cột được khai báo unbounded ngay từ đầu, hoặc có alembic migration đi kèm khi OMS-004 đổi model, truncation sẽ không xảy ra và endpoint config đã xử lý đúng token dài từ đầu.
- **Pattern**: [[schema-drift-no-migration-tool]]
