---
id: OMS-013
task_path: projects/topvnsport-oms/tasks/OMS-013-provision-service-env-files.md
project: topvnsport-oms
result_ref: 48a410e
executor: "@coordinator"
reviewer: "@antigravity"
status: passed
issued: 2026-07-25
verdict: pass
verdict_date: 2026-07-25
---

# Phiếu Review: OMS-013 — Deploy tự tạo `.env.prod` cho PMI/identity trên host + sửa endpoint cũ trong `.env.prod.example`

- Dự án: topvnsport-oms (`/home/lupca/projects/topvnsport`)
- Task gốc: `projects/topvnsport-oms/tasks/OMS-013-provision-service-env-files.md`
- Result-ref: 48a410e
- Executor: @coordinator
- Reviewer: @antigravity
- Ngày phát phiếu: 2026-07-25

## Acceptance Criteria cần verify

- [x] **AC1**: `deploy_prod.sh` bước `[2.1]` provision **cả** `$DEPLOY_PATH/PMI/backend/.env.prod` và `$DEPLOY_PATH/identity-service/.env.prod` trước bước `[3/5]`, dùng lại đúng `upsert_env_var`/`write_secret` đã có — **không viết hàm mới**, không `> file` (giữ nguyên yêu cầu của User: không ghi đè biến khác).
  - Verified: `deploy_prod.sh` lines 176-196 uses `write_secret` (which invokes `upsert_env_var_from_stdin` -> `upsert_env_var`) to provision both files before step `[3/5]`. Atomic line-by-line upsert preserves existing environment variables.
- [x] **AC2**: `DATABASE_URL` của từng service được ghép từ secret `RDS_HOST`/`RDS_USER`/`RDS_PASSWORD`/`RDS_SSLMODE` với **đúng tên database**: PMI → `pmi`, identity → `identity`, OMS → `oms` (OMS đã xong ở OMS-011), WMS → `wms` (đã xong ở `b9d4259`). Kèm `?sslmode=...`.
  - Verified: `deploy_prod.sh` constructs DSN for PMI (`.../pmi?sslmode=${RDS_SSLMODE}`) and identity (`.../identity?sslmode=${RDS_SSLMODE}`).
- [x] **AC3**: Giá trị non-secret của PMI (`AWS_DEFAULT_REGION`, `AWS_REGION`, `S3_BUCKET`, `AWS_S3_BUCKET`, `S3_PRESIGNED_URL_EXPIRY`) cũng được provision. Chúng **không phải secret** nên có thể hardcode trong script hoặc trong compose `environment:` — chọn cách nào cũng được, ghi rõ lý do. **Không** thêm `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` (dùng EC2 instance role, `.example` cũng để comment).
  - Verified: `deploy_prod.sh` lines 179-193 provisions these non-secret variables to `PMI/backend/.env.prod`. AWS access key / secret key are excluded so the EC2 IAM instance role is enforced.
- [x] **AC4**: `PMI/backend/.env.prod.example` và `identity-service/.env.prod.example` đổi endpoint cũ `database-topvnsport...` → `topvnsport-db.cluster-copm008y8icu.us-east-1.rds.amazonaws.com`. Giữ placeholder `<rds-password>`, **không** ghi password thật vào `.example` (file này git-tracked).
  - Verified: Both `.env.prod.example` files updated to `topvnsport-db...` with `<rds-password>`. Repository search for `database-topvnsport` returned zero occurrences.
- [x] **AC5**: Không làm CI đỏ: bước seed trong job `validate-compose` (`a953632`) vẫn phải hoạt động. Chạy đúng lệnh của CI trong shell không có biến nào và xác nhận exit 0 cho cả 4 compose prod.
  - Verified: Execution of `docker compose config` validation matching CI steps succeeded with output `All compose files valid`.
- [x] **AC6**: `tests/test_deploy_env_upsert.sh` vẫn xanh; nếu thêm hàm/nhánh mới thì bổ sung case tương ứng (đặc biệt: file **chưa tồn tại** → tạo mới với `chmod 600`; file có sẵn biến khác → giữ nguyên byte-for-byte).
  - Verified: `tests/test_deploy_env_upsert.sh` passed. Tests cover fresh file creation (`chmod 600`) and idempotency without duplicate key insertion.
- [x] **AC7**: Không log giá trị secret ra output GitHub Actions (không `echo`, không `set -x`); giá trị đi qua stdin, không qua argv.
  - Verified: Secrets are streamed over SSH via unquoted stdin heredoc (`write_secret` / `upsert_env_var_from_stdin`) without `echo` or `set -x`.
- [x] **AC8**: Toàn bộ test hiện hữu của OMS/PMI/WMS/identity vẫn xanh (baseline: OMS 44 passed/1 skipped, identity 58, WMS 31). **Báo cáo full suite, không phải tập con.**
  - Verified full test suites:
    - OMS backend: 44 passed, 1 skipped (total 45)
    - Identity service: 58 passed
    - WMS backend: 31 passed
    - PMI backend: 229 passed
- [x] **AC9**: `WMS/backend/requirements.txt` có `alembic` (chỉ có `sqlalchemy` trước) — để `docker exec wms-api alembic upgrade head` chạy được.
  - Verified: `alembic` added to `WMS/backend/requirements.txt`.
- [x] **AC10**: Bước migration không dừng ở service fail đầu tiên — thử cả 3 service, gom lỗi, exit 1 cuối nếu có fail.
  - Verified: `deploy_prod.sh` lines 237-249 iterates `pim-api wms-api oms_backend`, accumulates errors in `migration_failures`, and exits 1 at the end if any migration step failed.

## Definition of Done (AGENTS.md mục 3)

- [x] Toàn bộ AC pass
- [x] Test liên quan xanh 100%: `tests/test_deploy_env_upsert.sh`
- [x] Không regression (test khác trong module vẫn xanh)
- [x] Reviewer khác executor (Reviewer `@antigravity` != Executor `@coordinator`)

## Test gợi ý chạy trong repo code

```bash
cd /home/lupca/projects/topvnsport
bash -n deploy_prod.sh
bash tests/test_deploy_env_upsert.sh
env -u FERNET_KEY -u JWT_SECRET_KEY -u RDS_HOST -u RDS_USER -u RDS_PASSWORD -u RDS_SSLMODE \
  bash -c 'for f in PMI OMS WMS; do docker compose -f $f/docker-compose.prod.yml config >/dev/null || echo "FAIL $f"; done'
grep -rn "database-topvnsport" --include="*.example" --include="*.yml" --include="*.py" . | grep -v node_modules   # phải rỗng
```

## Review Toolchain

- `ocr`: open-code-review tool run on commit range `b9d4259..48a410e`. Comments analyzed and verified.
- `bash -n`: deploy_prod.sh syntax check clean.
- `pytest`: Full suites for OMS (44p/1s), identity-service (58p), WMS (31p), PMI (229p) passed without errors.

## Kết quả nghiệm thu

Verdict: **PASS**
All acceptance criteria (AC1 - AC10) and Definition of Done items are fully satisfied and verified with empirical test execution.
