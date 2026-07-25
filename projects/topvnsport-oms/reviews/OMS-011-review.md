---
id: OMS-011
task_path: projects/topvnsport-oms/tasks/OMS-011-fix-fernet-key-continuity-prod.md
project: topvnsport-oms
result_ref: b9d4259
executor: @gpt-5.6-luna-high
reviewer: "@gpt-5.6-sol"
status: passed
issued: 2026-07-25
verdict: pass
verdict_date: 2026-07-25
---

# Phiếu Review: OMS-011 — Luồng Zalo OTP sống được sau khi CI/CD deploy: FERNET_KEY continuity + preflight env + smoke check

- Dự án: topvnsport-oms (`/home/lupca/projects/topvnsport`)
- Task gốc: `projects/topvnsport-oms/tasks/OMS-011-fix-fernet-key-continuity-prod.md`
- Result-ref: b9d4259
- Executor: @gpt-5.6-luna-high
- Reviewer: @gpt-5.6-sol
- Ngày phát phiếu: 2026-07-25

## Acceptance Criteria cần verify
## Tiêu chí nghiệm thu (AC)

> **Quyết định của User (2026-07-25)** — nguồn `FERNET_KEY` cho prod đã chốt: **GitHub repo secret → `deploy_prod.sh` ghi vào `$DEPLOY_PATH/OMS/.env` trên host**. User đã thêm `FERNET_KEY` vào GitHub secrets rồi. Yêu cầu bắt buộc do User nêu: **"đừng để nó ghi đè env khác"** → xem AC9.

- [ ] **AC1**: `OMS/docker-compose.prod.yml` **không chứa giá trị `FERNET_KEY`**, dùng đúng dạng đã chốt:
  ```yaml
  - FERNET_KEY=${FERNET_KEY:?FERNET_KEY is required}
  ```
  Fail ngay lúc `docker compose up` nếu thiếu, và Compose đọc được giá trị từ `$DEPLOY_PATH/OMS/.env` (file này đã được `deploy_prod.sh:31-33` loại khỏi rsync qua `--exclude '.env'` + `--exclude '*.env'`, nên tồn tại độc lập trên EC2).

  ✅ *Đã xử lý một phần*: thay đổi working-tree hardcode `2Jf7o...` **đã được revert** (kiểm tra tại commit `024c3f4`: `OMS/docker-compose.prod.yml:25` giờ là `- FERNET_KEY` pass-through, file không còn dirty). Việc còn lại của AC1 chỉ là đổi sang dạng `:?`.

  ⛔ **TUYỆT ĐỐI KHÔNG dùng dạng có default** `${FERNET_KEY:-<giá trị>}`. User đã cân nhắc và loại ngày 2026-07-25 vì: (a) vẫn là secret nằm trong file git-tracked, và vì prod chưa từng set `FERNET_KEY` nên nhánh default sẽ được dùng THẬT ⇒ tái phạm đúng AC1 của [[OMS-006-fix-security-critical]]; (b) nó khôi phục lại đúng chế độ **lỗi im lặng** mà fail-fast vừa loại bỏ — deploy báo thành công, app start bình thường, rồi 500 khi đọc row cũ (mã hoá bằng key fallback cũ).

  **`JWT_SECRET_KEY`**: xử lý ở **AC12** (rotate xuyên service), không xử lý trong AC1. Bối cảnh để hiểu AC12: literal `identity_jwt_secret_key_2026_change_me_in_prod` là secret **dùng chung**, đã verify bằng grep — `identity-service/docker-compose.prod.yml:12` (hardcode, là nơi SIGN token, xem `identity-service/backend/utils/jwt.py:8,25`), `PMI/docker-compose.prod.yml:11` (cùng literal, `PMI/backend/utils/auth.py:8` đọc `os.environ`), `OMS/docker-compose.prod.yml:27` (dạng `:-`), `OMS/backend/utils/auth.py:6-10` (fallback). Đổi riêng một service ⇒ service đó verify bằng key khác key sign ⇒ **401 vĩnh viễn**, không phải chỉ logout một lần. Vì vậy AC12 bắt buộc cả 3 cùng đọc **một** secret.

  Lưu ý: key `2Jf7oG7N4zFv2j3GmY5V0rLq9xW8pC1aB6dE3hK7nQw=` đã **cháy** — nó nằm trong `OMS/docker-compose.yml:32`, `OMS/backend/tests/conftest.py:4`, `OMS/backend/test_main.py:9` (git-tracked) ⇒ chỉ được dùng cho dev/test, không bao giờ làm key prod.

  Verify: `grep -nE "FERNET_KEY=[^$]|FERNET_KEY:-" OMS/docker-compose.prod.yml` → rỗng.
- [ ] **AC2**: `deploy_prod.sh` **preflight fail-fast**: kiểm tra `FERNET_KEY` và `JWT_SECRET_KEY` đã set và non-empty **trước** bước `[3/5]` build/start, thoát với message rõ ràng nếu thiếu (dùng `: "${FERNET_KEY:?...}"` như pattern đã có cho `EC2_HOST` ở `deploy_prod.sh:7`). Không được để lộ giá trị key ra log/stdout. **Phải validate cả FORMAT**, không chỉ sự tồn tại — OCR flag `high` ở `OMS/backend/utils/crypto.py:8-15`: "only checks for existence but doesn't validate the key format … a malformed key could lead to encryption/decryption failure". Fernet key = 32 byte urlsafe-base64 (44 ký tự, kết thúc `=`); key sai format sẽ pass check hiện tại rồi crash ở import-time (`models.py:94-111`).
- [ ] **AC3**: Có **thủ tục 1 lần** để dữ liệu cũ trên prod đọc được sau deploy. Chọn 1 trong 2 và ghi rõ vào PR description + docs:
  - (a) set `FERNET_KEY` trên prod host = **đúng key fallback cũ** (khôi phục từ git history), rồi rotate sau bằng (b); **hoặc**
  - (b) script `OMS/backend/scripts/reencrypt_system_configs.py` đọc `FERNET_KEY_OLD` + `FERNET_KEY`, decrypt bằng key cũ → encrypt lại bằng key mới, chạy trong transaction, idempotent (row nào đã decrypt được bằng key mới thì bỏ qua), có `--dry-run` in ra số row sẽ đổi mà không ghi.
  - Khuyến nghị (b) vì key cũ đã lộ trong git history nên không được dùng làm key vĩnh viễn.
- [ ] **AC4**: Script AC3(b) **không in cleartext** giá trị token/secret ra stdout/log (chỉ in `config_key` + số lượng). Có test unit cho script: encrypt bằng key A → chạy re-encrypt sang key B → decrypt được bằng B, và chạy lại lần 2 không đổi gì (idempotent).
- [ ] **AC5**: Bước `[4.1/5] Post-deploy smoke checks` trong `deploy_prod.sh` có thêm 1 check **thật sự chạm vào đường decrypt** của OMS — không chỉ `GET /docs`. Ví dụ: `docker exec oms_backend python -c` đọc 1 row `system_configs` qua model `SystemConfig` và assert decrypt thành công (không in giá trị). Deploy phải FAIL nếu decrypt lỗi, thay vì để lỗi lộ ra khi user bấm vào trang cấu hình.
- [ ] **AC6**: `OMS/docker-compose.yml` (local) — key dev hardcoded ở dòng 32 là chấp nhận được cho local, nhưng phải có comment nói rõ đây là key **chỉ dùng cho dev**, và giá trị này **không được** trùng key prod.
- [ ] **AC7**: Ghi tài liệu danh sách env var **bắt buộc** cho OMS prod (`FERNET_KEY`, `CORS_ALLOWED_ORIGINS`, `JWT_SECRET_KEY`, `DATABASE_URL`) + cách sinh `FERNET_KEY` mới, vào `OMS/README.md` hoặc `docs/` của repo.
- [ ] **AC8**: Toàn bộ test trong `tests:` vẫn xanh 100%; không regression suite OMS backend.
- [ ] **AC9** *(hướng User đã chốt)*: `FERNET_KEY` đi từ GitHub secret vào `$DEPLOY_PATH/OMS/.env` trên host, **không ghi đè biến khác**:
  - `.github/workflows/deploy.yml`: thêm `FERNET_KEY: ${{ secrets.FERNET_KEY }}` **và** `JWT_SECRET_KEY: ${{ secrets.JWT_SECRET_KEY }}` vào block `env:` của step "Run production deploy" (cạnh `EC2_HOST`/`DEPLOY_PATH`/`PUBLIC_HOST` hiện có). Cả 2 secret User đã thêm trên GitHub. Không thêm gì vào `on:`/`concurrency:`.
  - `deploy_prod.sh`: thêm 1 bước **trước** `[3/5] Build and start production stacks` (phải trước, vì `docker compose up` cần `.env` đã có key — User đã xác nhận thứ tự này) ghi **cả `FERNET_KEY` và `JWT_SECRET_KEY`** vào `$DEPLOY_PATH/OMS/.env`.
  - ⛔ **KHÔNG được `> .env`** (truncate) — trên host có thể đã có biến khác, ghi đè là mất sạch. **Đây là yêu cầu User nêu trực tiếp.** Phải **upsert đúng 1 key**: nếu `grep -q '^FERNET_KEY=' .env` → `sed -i "s|^FERNET_KEY=.*|FERNET_KEY=$key|"`; nếu chưa có → `>> .env`. Dùng `|` làm delimiter cho `sed` (an toàn: Fernet key là urlsafe-base64 `A-Za-z0-9-_=`, không chứa `|`). Mọi dòng khác trong `.env` phải còn **nguyên vẹn và đúng thứ tự**.
  - Truyền giá trị **qua stdin heredoc** (`ssh "${SSH_OPTS[@]}" ... "bash -se" <<REMOTE`, đúng pattern đã có ở `deploy_prod.sh:120`), **KHÔNG** nhét vào argv của `ssh`/`sed`/`echo` — argv hiện trong `ps` trên host. Heredoc **không quote** (`<<REMOTE`) để nội suy `$FERNET_KEY` phía runner, escape `\$` cho biến phía remote.
  - `umask 077`, `touch .env && chmod 600 .env` trước khi ghi; tuyệt đối không `echo`/`set -x` làm lộ giá trị vào log GitHub Actions.
  - Viết thành hàm dùng lại được (ví dụ `upsert_env_var <file> <key> <value>`) để sau này thêm `JWT_SECRET_KEY`/`CORS_ALLOWED_ORIGINS` không phải copy-paste.
  - **`DATABASE_URL` sau khi [[OMS-012-rds-migration]] chuyển prod sang RDS**: `OMS/backend/core/config.py` và `OMS/docker-compose.prod.yml:12` đang default `postgresql://postgres:postgres@topvnsport-db.cluster-copm008y8icu.us-east-1.rds.amazonaws.com:5432/oms` — endpoint RDS thật + credentials trong file git-tracked, và nếu host không set biến thì app nối thẳng RDS bằng `postgres:postgres`. **Xử lý ở AC10** (đổi default sang container DB, không phải bỏ default). Đồng thời rà `OMS/backend/.env.prod` — đang được `.gitignore:19` (`.env.*`) chặn, xác nhận lại bằng `git ls-files --error-unmatch`.
  - **Không** ghi `DATABASE_URL` từ GitHub secret — secret đó không tồn tại. `DATABASE_URL` chỉ được set thủ công trong `.env` trên host khi thật sự cutover sang RDS.
  - **Test bắt buộc cho phần này** (chạy local, không cần EC2): tạo `.env` giả có 3 biến khác + `FERNET_KEY` cũ → chạy hàm upsert → assert `FERNET_KEY` đã đổi **và** 3 biến kia còn nguyên; chạy trên `.env` chưa có `FERNET_KEY` → assert được append, các biến cũ còn nguyên; chạy 2 lần liên tiếp → không sinh dòng trùng.

## Definition of Done (AGENTS.md mục 3)
- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: OMS/backend/tests/test_config.py::test_sms_config_endpoints, OMS/backend/tests/test_config.py::test_sms_config_endpoints_support_long_tokens, OMS/backend/test_main.py::test_get_zalo_config_returns_all_masked_fields, OMS/backend/test_main.py::test_update_zalo_config_only_persists_unmasked_fields, OMS/backend/test_main.py::test_zalo_token_refresh_updates_system_config, e2e_tests/tests/test_oms_admin_sms.py::test_oms_admin_zalo_settings
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (xác nhận reviewer @gpt-5.6-sol ≠ executor @gpt-5.6-luna-high)

## Test gợi ý chạy trong repo code
- `OMS/backend/tests/test_config.py::test_sms_config_endpoints`
- `OMS/backend/tests/test_config.py::test_sms_config_endpoints_support_long_tokens`
- `OMS/backend/test_main.py::test_get_zalo_config_returns_all_masked_fields`
- `OMS/backend/test_main.py::test_update_zalo_config_only_persists_unmasked_fields`
- `OMS/backend/test_main.py::test_zalo_token_refresh_updates_system_config`
- `e2e_tests/tests/test_oms_admin_sms.py::test_oms_admin_zalo_settings`

## Câu hỏi rủi ro (vòng 2 — re-review sau `changes`)

Bạn đã review vòng 1 (`621744e`) và trả `changes` với 5 finding. Vòng này verify chúng đã hết, cộng 2 điểm mới bên dưới. **Sau khi task này pass, coordinator sẽ `git push` và deploy chạy thật lên prod** — `main` đang `ahead 4`.

### Đã đổi so với vòng 1

Hạ tầng đã sẵn sàng, khác hẳn lúc bạn review vòng 1:
- Cluster **đổi tên** `database-topvnsport` → **`topvnsport-db`**, endpoint `topvnsport-db.cluster-copm008y8icu.us-east-1.rds.amazonaws.com`, **password auth (không còn IAM-only)**, data đã migrate, database OMS tên **`oms`**, cần `sslmode=require`.
- **6 secret đã tồn tại** trên GitHub (coordinator tạo, `gh secret list` xác nhận): `FERNET_KEY`, `JWT_SECRET_KEY`, `RDS_HOST`, `RDS_USER`, `RDS_PASSWORD`, `RDS_SSLMODE`. Finding vòng 1 về "AC14/AC15 chưa implement" giờ phải verify theo AC15 (không phải AC14 — AC14 đã bị AC15 thay ở phần password).
- Task có thêm mục **"Verify hạ tầng"** ở cuối với 4 câu hỏi read-only trên RDS.

### Câu hỏi

1. 🔴 **Số test tụt mạnh — kiểm trước tiên**: vòng 1 executor báo `OMS: 44 passed, 1 skipped` và `WMS: 31 passed`; vòng 2 báo **`OMS: 16 passed, 1 skipped`** và **`WMS: 13 passed`**. Con số giảm ~2/3. Hai khả năng: (a) executor chỉ chạy một tập con (chọn file/`-k`) và báo cáo đúng cái nó chạy; (b) có test bị **collection error** nên không được đếm. (b) là finding chặn. Tự chạy full suite và đối chiếu: `pytest -v` trong `OMS/backend` phải ra 44 passed + 1 skipped (hoặc 45 nếu có test mới), `WMS/backend` ra 31.
2. 🔴 **4 finding vòng 1 — verify từng cái**: (a) `DOMAIN_NAME` đã được truyền vào heredoc remote chưa (chạy lại cách bạn đã reproduce `set -u` abort); (b) smoke JWT giờ "chọn một staff account đang active" — verify cách chọn có deterministic và không fail khi DB chưa có staff nào, và nó **không** in token ra log; (c) `upsert_env_var` với file thiếu trailing newline — test mới có đúng không, và có assert các dòng khác nguyên vẹn byte-for-byte không; (d) AC15 wiring đầy đủ ở cả 3 chỗ (compose, `deploy.yml`, `.env` upsert trong `deploy_prod.sh`).
3. 🔴 **WMS — vượt scope nhưng lần này là cần thiết**: commit sửa `WMS/docker-compose.prod.yml`, `WMS/backend/alembic/env.py`, `WMS/backend/core/config.py` để bỏ endpoint cũ. Coordinator chủ động gộp vào đây vì 3 file này trùng với file OMS-011 đã sửa ở vòng 1 (chạy task riêng song song sẽ xung đột), và vì `deploy_prod.sh` giờ hard-fail nên endpoint chết ở WMS sẽ **kéo cả deploy fail**. Verify: WMS giờ lấy DSN từ đâu, database name của WMS là gì (đừng để trỏ `oms`), và `WMS/backend/alembic/env.py` có còn fallback credential nào không.
4. **AC13 — CI phải xanh**: compose dùng `${VAR:?}` cho FERNET/JWT/RDS. Chạy đúng lệnh của job `validate-compose` trong shell **không có** các biến đó và xác nhận exit 0 cho cả 4 compose prod (PMI/OMS/WMS/web). Kiểm cả bước seed `.env.prod` (thêm ở `a953632`) còn hoạt động.
5. ⚠️ **Phần KHÔNG verify được, và nó có thể là lý do trả `changes`**: endpoint mới chỉ resolve ra **private `172.31.x.x`** nên không kết nối được từ workstation (coordinator cũng bị permission classifier chặn 2 lần khi thử). Vì vậy 4 câu của mục "Verify hạ tầng" vẫn trống: row count `system_configs`, kiểu cột `config_value`, có `alembic_version` chưa, ciphertext có giải mã được bằng `FERNET_KEY` hiện tại không.
   - Nếu bạn có đường vào EC2/VPC thì chạy read-only và trả lời — sẽ chốt được AC10/AC11.
   - Nếu không: đánh giá xem **smoke check post-deploy có đủ làm lưới an toàn** hay không. Thiết kế hiện tại là: sai key ⇒ smoke check decrypt fail ⇒ deploy FAIL (không mất dữ liệu, chỉ là deploy đỏ), rồi mới chạy `reencrypt_system_configs.py` hoặc nhập lại token qua UI. Nếu bạn thấy lưới này đủ thì nói rõ trong notes và **đừng chặn task chỉ vì thiếu số liệu prod** — coordinator sẽ push và theo dõi deploy. Nếu bạn thấy chưa đủ, nói rõ thiếu cái gì.
6. **AC5 smoke check phải FAIL được**: verify 2 bước smoke (decrypt + JWT xuyên service) không bị `|| true`, và khi fail thì `deploy_prod.sh` thoát non-zero. Đây là lưới an toàn duy nhất cho lần push tới.
7. **Không lộ secret**: grep `deploy_prod.sh` + `deploy.yml` xem có chỗ nào `echo`/`set -x` làm lộ `RDS_PASSWORD`/`FERNET_KEY`/token vào log GitHub Actions. Xác nhận password RDS **không** nằm trong bất kỳ file tracked nào: `git grep -n 'JeWOsX' $(git rev-list --all) -- 2>/dev/null | head` phải rỗng (nếu có thì là finding chặn, phải rotate ngay).

### Nếu PASS

Ghi trong notes: theo bạn push `b9d4259` có an toàn chưa, và thứ tự thao tác nào — push rồi để `deploy.yml` tự chạy, hay còn việc gì phải làm tay trên EC2 trước (ví dụ tạo `OMS/.env` lần đầu).

## Review Toolchain
Chạy theo toolchain của repo đích; preflight các tool đã đăng ký trước khi review.

## Trả kết quả
`/verdict OMS-011 <pass|changes> --reviewer @gpt-5.6-sol [--commit <hash>] [--notes "..."]`
