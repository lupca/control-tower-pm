---
id: OMS-011
title: "Luồng Zalo OTP sống được sau khi CI/CD deploy: FERNET_KEY continuity + preflight env + smoke check"
status: done
priority: urgent
risk: high
deadline: null
executor: "@gpt-5.6-luna-high"
reviewer: "@gpt-5.6-sol"
result_ref: "b9d4259"
depends_on: [OMS-010]
files:
  - deploy_prod.sh
  - OMS/docker-compose.prod.yml
  - OMS/docker-compose.yml
  - .github/workflows/deploy.yml  # thêm ở Spec Gate lần 2 (2026-07-25) do User chốt hướng GitHub secret → AC9
  - OMS/backend/core/config.py    # thêm ở Spec Gate lần 3 (2026-07-25) — file do OMS-012 tạo, chứa default DATABASE_URL kèm credentials RDS
  - OMS/backend/.env.prod         # thêm ở Spec Gate lần 3 (2026-07-25) — kiểm tra có bị git-track không
  - identity-service/docker-compose.prod.yml  # Spec Gate lần 4 (2026-07-25) — AC12, User cho phép rotate JWT dùng chung
  - PMI/docker-compose.prod.yml               # Spec Gate lần 4 (2026-07-25) — AC12
  - OMS/backend/utils/auth.py                 # Spec Gate lần 4 (2026-07-25) — AC12, bỏ fallback literal
  - identity-service/backend/utils/jwt.py     # Spec Gate lần 4 (2026-07-25) — AC12, bỏ fallback literal
  - .github/workflows/ci.yml                  # Spec Gate lần 5 (2026-07-25) — AC13, job validate-compose sẽ fail vì dạng :?
  # file mới, executor phải tạo (không có trong graph):
  - OMS/backend/scripts/reencrypt_system_configs.py
flows: [send_otp, verify_otp, update_sms_config]
tests:
  - OMS/backend/tests/test_config.py::test_sms_config_endpoints
  - OMS/backend/tests/test_config.py::test_sms_config_endpoints_support_long_tokens
  - OMS/backend/test_main.py::test_get_zalo_config_returns_all_masked_fields
  - OMS/backend/test_main.py::test_update_zalo_config_only_persists_unmasked_fields
  - OMS/backend/test_main.py::test_zalo_token_refresh_updates_system_config
  - e2e_tests/tests/test_oms_admin_sms.py::test_oms_admin_zalo_settings
dispatched: 2026-07-25
in_review: 2026-07-25
predicted_success: medium
prediction_factors:
  score: 0.5
  deductions:
    - "blast_radius > 8: -0.3 (get_impact_radius trên deploy_prod.sh + OMS/docker-compose.prod.yml: 49 file bị ảnh hưởng)"
    - "blast_radius > 15: -0.2 (cộng dồn -0.5)"
  notes:
    - "không trừ hub/bridge: không file nào trong files: nằm trong get_hub_nodes/get_bridge_nodes(top_n=50)."
    - "không trừ no-tests: đã có test cho GET/PUT /api/configs/sms."
    - "rủi ro thật của task này KHÔNG nằm ở code mà ở dữ liệu prod (ciphertext không giải mã được nếu đổi key) — xem Project Gate."
confidence_interval: [0.35, 0.65]
created: 2026-07-25
updated: 2026-07-25
rejections: 1
---

# OMS-011: Luồng Zalo OTP sống được sau khi CI/CD deploy: FERNET_KEY continuity + preflight env + smoke check

> Dự án: [[projects/topvnsport-oms/topvnsport-oms]]

## Bối cảnh — deploy commit `3116bf3` lên prod NGUYÊN TRẠNG sẽ làm lỗi 500 quay lại

[[OMS-006-fix-security-critical]] đã bỏ Fernet fallback key (đúng về mặt security) nhưng tạo ra một vấn đề **liên tục hoá khoá** chưa ai xử lý:

1. **Trước `3116bf3`, prod chưa từng set `FERNET_KEY`.** Xác nhận: `git show 3116bf3~1:OMS/docker-compose.prod.yml` → block `environment:` của `oms_backend` **không có** `FERNET_KEY`.
2. ⇒ Toàn bộ row trong `system_configs` trên prod đang được mã hoá bằng **key fallback hardcoded cũ** (giá trị lấy từ `git show 3116bf3~1:OMS/backend/models.py` — không paste lại vào đây vì file này git-tracked).
3. Key cũ đó giờ **đã bị xoá sạch khỏi codebase** (`grep -rn "lz_K8Z8d" .` → không còn), chỉ còn trong git history.
4. ⇒ Sau khi deploy, nếu `FERNET_KEY` trên prod = **bất kỳ giá trị nào khác** key cũ → `EncryptedString.process_result_value()` (`OMS/backend/models.py:118-125`) raise `ValueError` khi đọc lại config → **`GET`/`PUT /api/configs/sms` lại 500**, và luồng `send_otp` mất `zalo_access_token`/`zalo_template_id` → OTP chết hoàn toàn.
5. **Đang có regression chưa commit**: working tree hiện sửa `OMS/docker-compose.prod.yml` thành hardcode một key MỚI (`FERNET_KEY=2Jf7o...`), trong khi commit `3116bf3` để đúng dạng pass-through `- FERNET_KEY`. Nếu thay đổi này bị commit thì (a) tái phạm chính AC1 của OMS-006 (secret hardcoded trong file git-tracked), (b) **chắc chắn** kích hoạt kịch bản (4). Xác nhận bằng `git status --short -- OMS/docker-compose.prod.yml` → ` M`.

Ngoài ra `deploy_prod.sh` hiện không kiểm tra biến env nào trước khi deploy (OCR cũng flag: "unvalidated env vars"), nên thiếu `FERNET_KEY` sẽ biểu hiện thành container crash-loop chứ không phải một thông báo lỗi rõ ràng.

## Tiêu chí nghiệm thu (AC)

> **Quyết định của User (2026-07-25)** — nguồn `FERNET_KEY` cho prod đã chốt: **GitHub repo secret → `deploy_prod.sh` ghi vào `$DEPLOY_PATH/OMS/.env` trên host**. User đã thêm `FERNET_KEY` vào GitHub secrets rồi. Yêu cầu bắt buộc do User nêu: **"đừng để nó ghi đè env khác"** → xem AC9.

- [x] **AC1**: `OMS/docker-compose.prod.yml` **không chứa giá trị `FERNET_KEY`**, dùng đúng dạng đã chốt:
  ```yaml
  - FERNET_KEY=${FERNET_KEY:?FERNET_KEY is required}
  ```
  Fail ngay lúc `docker compose up` nếu thiếu, và Compose đọc được giá trị từ `$DEPLOY_PATH/OMS/.env` (file này đã được `deploy_prod.sh:31-33` loại khỏi rsync qua `--exclude '.env'` + `--exclude '*.env'`, nên tồn tại độc lập trên EC2).

  ✅ *Đã xử lý một phần*: thay đổi working-tree hardcode `2Jf7o...` **đã được revert** (kiểm tra tại commit `024c3f4`: `OMS/docker-compose.prod.yml:25` giờ là `- FERNET_KEY` pass-through, file không còn dirty). Việc còn lại của AC1 chỉ là đổi sang dạng `:?`.

  ⛔ **TUYỆT ĐỐI KHÔNG dùng dạng có default** `${FERNET_KEY:-<giá trị>}`. User đã cân nhắc và loại ngày 2026-07-25 vì: (a) vẫn là secret nằm trong file git-tracked, và vì prod chưa từng set `FERNET_KEY` nên nhánh default sẽ được dùng THẬT ⇒ tái phạm đúng AC1 của [[OMS-006-fix-security-critical]]; (b) nó khôi phục lại đúng chế độ **lỗi im lặng** mà fail-fast vừa loại bỏ — deploy báo thành công, app start bình thường, rồi 500 khi đọc row cũ (mã hoá bằng key fallback cũ).

  **`JWT_SECRET_KEY`**: xử lý ở **AC12** (rotate xuyên service), không xử lý trong AC1. Bối cảnh để hiểu AC12: literal `identity_jwt_secret_key_2026_change_me_in_prod` là secret **dùng chung**, đã verify bằng grep — `identity-service/docker-compose.prod.yml:12` (hardcode, là nơi SIGN token, xem `identity-service/backend/utils/jwt.py:8,25`), `PMI/docker-compose.prod.yml:11` (cùng literal, `PMI/backend/utils/auth.py:8` đọc `os.environ`), `OMS/docker-compose.prod.yml:27` (dạng `:-`), `OMS/backend/utils/auth.py:6-10` (fallback). Đổi riêng một service ⇒ service đó verify bằng key khác key sign ⇒ **401 vĩnh viễn**, không phải chỉ logout một lần. Vì vậy AC12 bắt buộc cả 3 cùng đọc **một** secret.

  Lưu ý: key `2Jf7oG7N4zFv2j3GmY5V0rLq9xW8pC1aB6dE3hK7nQw=` đã **cháy** — nó nằm trong `OMS/docker-compose.yml:32`, `OMS/backend/tests/conftest.py:4`, `OMS/backend/test_main.py:9` (git-tracked) ⇒ chỉ được dùng cho dev/test, không bao giờ làm key prod.

  Verify: `grep -nE "FERNET_KEY=[^$]|FERNET_KEY:-" OMS/docker-compose.prod.yml` → rỗng.
- [x] **AC2**: `deploy_prod.sh` **preflight fail-fast**: kiểm tra `FERNET_KEY` và `JWT_SECRET_KEY` đã set và non-empty **trước** bước `[3/5]` build/start, thoát với message rõ ràng nếu thiếu (dùng `: "${FERNET_KEY:?...}"` như pattern đã có cho `EC2_HOST` ở `deploy_prod.sh:7`). Không được để lộ giá trị key ra log/stdout. **Phải validate cả FORMAT**, không chỉ sự tồn tại — OCR flag `high` ở `OMS/backend/utils/crypto.py:8-15`: "only checks for existence but doesn't validate the key format … a malformed key could lead to encryption/decryption failure". Fernet key = 32 byte urlsafe-base64 (44 ký tự, kết thúc `=`); key sai format sẽ pass check hiện tại rồi crash ở import-time (`models.py:94-111`).
- [x] **AC3**: Có **thủ tục 1 lần** để dữ liệu cũ trên prod đọc được sau deploy. Chọn 1 trong 2 và ghi rõ vào PR description + docs:
  - (a) set `FERNET_KEY` trên prod host = **đúng key fallback cũ** (khôi phục từ git history), rồi rotate sau bằng (b); **hoặc**
  - (b) script `OMS/backend/scripts/reencrypt_system_configs.py` đọc `FERNET_KEY_OLD` + `FERNET_KEY`, decrypt bằng key cũ → encrypt lại bằng key mới, chạy trong transaction, idempotent (row nào đã decrypt được bằng key mới thì bỏ qua), có `--dry-run` in ra số row sẽ đổi mà không ghi.
  - Khuyến nghị (b) vì key cũ đã lộ trong git history nên không được dùng làm key vĩnh viễn.
- [x] **AC4**: Script AC3(b) **không in cleartext** giá trị token/secret ra stdout/log (chỉ in `config_key` + số lượng). Có test unit cho script: encrypt bằng key A → chạy re-encrypt sang key B → decrypt được bằng B, và chạy lại lần 2 không đổi gì (idempotent).
- [x] **AC5**: Bước `[4.1/5] Post-deploy smoke checks` trong `deploy_prod.sh` có thêm 1 check **thật sự chạm vào đường decrypt** của OMS — không chỉ `GET /docs`. Ví dụ: `docker exec oms_backend python -c` đọc 1 row `system_configs` qua model `SystemConfig` và assert decrypt thành công (không in giá trị). Deploy phải FAIL nếu decrypt lỗi, thay vì để lỗi lộ ra khi user bấm vào trang cấu hình.
- [x] **AC6**: `OMS/docker-compose.yml` (local) — key dev hardcoded ở dòng 32 là chấp nhận được cho local, nhưng phải có comment nói rõ đây là key **chỉ dùng cho dev**, và giá trị này **không được** trùng key prod.
- [x] **AC7**: Ghi tài liệu danh sách env var **bắt buộc** cho OMS prod (`FERNET_KEY`, `CORS_ALLOWED_ORIGINS`, `JWT_SECRET_KEY`, `DATABASE_URL`) + cách sinh `FERNET_KEY` mới, vào `OMS/README.md` hoặc `docs/` của repo.
- [x] **AC8**: Toàn bộ test trong `tests:` vẫn xanh 100%; không regression suite OMS backend.
- [x] **AC9** *(hướng User đã chốt)*: `FERNET_KEY` đi từ GitHub secret vào `$DEPLOY_PATH/OMS/.env` trên host, **không ghi đè biến khác**:
  - `.github/workflows/deploy.yml`: thêm `FERNET_KEY: ${{ secrets.FERNET_KEY }}` **và** `JWT_SECRET_KEY: ${{ secrets.JWT_SECRET_KEY }}` vào block `env:` của step "Run production deploy" (cạnh `EC2_HOST`/`DEPLOY_PATH`/`PUBLIC_HOST` hiện có). Cả 2 secret User đã thêm trên GitHub. Không thêm gì vào `on:`/`concurrency:`.
  - `deploy_prod.sh`: thêm 1 bước **trước** `[3/5] Build and start production stacks` (phải trước, vì `docker compose up` cần `.env` đã có key — User đã xác nhận thứ tự này) ghi **cả `FERNET_KEY` và `JWT_SECRET_KEY`** vào `$DEPLOY_PATH/OMS/.env`.
  - ⛔ **KHÔNG được `> .env`** (truncate) — trên host có thể đã có biến khác, ghi đè là mất sạch. **Đây là yêu cầu User nêu trực tiếp.** Phải **upsert đúng 1 key**: nếu `grep -q '^FERNET_KEY=' .env` → `sed -i "s|^FERNET_KEY=.*|FERNET_KEY=$key|"`; nếu chưa có → `>> .env`. Dùng `|` làm delimiter cho `sed` (an toàn: Fernet key là urlsafe-base64 `A-Za-z0-9-_=`, không chứa `|`). Mọi dòng khác trong `.env` phải còn **nguyên vẹn và đúng thứ tự**.
  - Truyền giá trị **qua stdin heredoc** (`ssh "${SSH_OPTS[@]}" ... "bash -se" <<REMOTE`, đúng pattern đã có ở `deploy_prod.sh:120`), **KHÔNG** nhét vào argv của `ssh`/`sed`/`echo` — argv hiện trong `ps` trên host. Heredoc **không quote** (`<<REMOTE`) để nội suy `$FERNET_KEY` phía runner, escape `\$` cho biến phía remote.
  - `umask 077`, `touch .env && chmod 600 .env` trước khi ghi; tuyệt đối không `echo`/`set -x` làm lộ giá trị vào log GitHub Actions.
  - Viết thành hàm dùng lại được (ví dụ `upsert_env_var <file> <key> <value>`) để sau này thêm `JWT_SECRET_KEY`/`CORS_ALLOWED_ORIGINS` không phải copy-paste.
  - **`DATABASE_URL` sau khi [[OMS-012-rds-migration]] chuyển prod sang RDS**: `OMS/backend/core/config.py` và `OMS/docker-compose.prod.yml:12` đang default `postgresql://postgres:postgres@topvnsport-db.cluster-copm008y8icu.us-east-1.rds.amazonaws.com:5432/oms` — endpoint RDS thật + credentials trong file git-tracked, và nếu host không set biến thì app nối thẳng RDS bằng `postgres:postgres`. **Xử lý ở AC10** (đổi default sang container DB, không phải bỏ default). Đồng thời rà `OMS/backend/.env.prod` — đang được `.gitignore:19` (`.env.*`) chặn, xác nhận lại bằng `git ls-files --error-unmatch`.
  - **Không** ghi `DATABASE_URL` từ GitHub secret — secret đó không tồn tại. `DATABASE_URL` chỉ được set thủ công trong `.env` trên host khi thật sự cutover sang RDS.
  - **Test bắt buộc cho phần này** (chạy local, không cần EC2): tạo `.env` giả có 3 biến khác + `FERNET_KEY` cũ → chạy hàm upsert → assert `FERNET_KEY` đã đổi **và** 3 biến kia còn nguyên; chạy trên `.env` chưa có `FERNET_KEY` → assert được append, các biến cũ còn nguyên; chạy 2 lần liên tiếp → không sinh dòng trùng.

## Verification (executor tự chạy trước khi báo xong)

```bash
cd /home/lupca/projects/topvnsport
# AC1
grep -n "FERNET_KEY" OMS/docker-compose.prod.yml   # phải là pass-through, không có dấu "="

# AC2 — preflight phải chặn khi thiếu key (chạy trong shell rời, KHÔNG deploy thật)
env -u FERNET_KEY EC2_HOST=dummy bash -n deploy_prod.sh   # syntax
# + test tay logic preflight bằng cách trích đoạn ra file tạm, đừng chạy deploy thật

# AC3/AC4 — re-encrypt script
docker compose -f OMS/docker-compose.yml exec oms_backend \
  python scripts/reencrypt_system_configs.py --dry-run

# AC8
docker compose -f OMS/docker-compose.yml exec oms_backend pytest -q
```

## Plan

Thứ tự này chọn theo mức chặn: AC10 trước tiên vì nó là thứ duy nhất khiến `git push` có thể **mất dữ liệu prod**.

### Bước 1 — Gỡ credentials RDS khỏi repo (AC10)

**KHÔNG khôi phục `oms_db`** — prod đã chạy trên RDS (User xác nhận data migration xong). Việc cần làm:
1. Verify 3 điều trong AC10 trước tiên (database `oms` có dữ liệu thật; auth password vs IAM; có `alembic_version` chưa) — đặc biệt là khả năng runbook đã dump/restore sai tên (`oms-db`/`oms` vs `oms_db`/`oms_db`).
2. `OMS/docker-compose.prod.yml:12` → `${DATABASE_URL:?DATABASE_URL is required}` (default hiện tại chứa mật khẩu master RDS trong file git-tracked).
3. `OMS/backend/core/config.py` → bỏ default, raise nếu thiếu. Giữ indirection OMS-012 đã tạo.
4. Verify `docker compose -f OMS/docker-compose.prod.yml config` — nhớ AC13, job `validate-compose` chạy lệnh này **không có env**.

### Bước 2 — `FERNET_KEY` sang dạng `:?` (AC1)

`- FERNET_KEY=${FERNET_KEY:?FERNET_KEY is required}`. **Không đụng `JWT_SECRET_KEY`** (xem quyết định trong AC1). `OMS/docker-compose.yml` local: giữ key dev, chỉ thêm comment "dev only" (AC6).

### Bước 3 — Đường đi của secret: GitHub → `.env` trên host (AC9)

1. `.github/workflows/deploy.yml`: thêm vào block `env:` của step "Run production deploy": `FERNET_KEY: ${{ secrets.FERNET_KEY }}` và `JWT_SECRET_KEY: ${{ secrets.JWT_SECRET_KEY }}` (AC12). **Không thêm `DATABASE_URL`** — secret đó không tồn tại.
   - Hàm upsert phải **bỏ qua key có value rỗng** thay vì ghi dòng `KEY=` rỗng vào `.env` — ghi rỗng sẽ làm `:?` pass rồi app chết lúc dùng.
2. `deploy_prod.sh`: thêm hàm `upsert_env_var <file> <key> <value>` và một bước ghi `.env` **trước** `[3/5]`:
   - upsert đúng 1 key: `grep -q '^KEY='` → `sed -i "s|^KEY=.*|KEY=$value|"`, ngược lại `>> file`. **Không bao giờ `> file`.**
   - value truyền qua **stdin heredoc** (`ssh ... "bash -se" <<REMOTE`, pattern có sẵn ở `deploy_prod.sh:120`), không qua argv.
   - `umask 077`, `touch .env && chmod 600 .env`, không `echo` giá trị, không `set -x`.
   - bỏ qua key có value rỗng.
3. Test hàm upsert (local, không cần EC2): `.env` giả có 3 biến khác + key cũ → assert key đổi, 3 biến kia còn nguyên và đúng thứ tự; `.env` chưa có key → assert append; chạy 2 lần → không sinh dòng trùng; value chứa ký tự `=`, `/`, `+` (base64) → không hỏng.

### Bước 4 — Preflight fail-fast (AC2)

Thêm vào đầu `deploy_prod.sh`, cạnh `: "${EC2_HOST:?...}"` (dòng 7): kiểm `FERNET_KEY` set + non-empty + **đúng format Fernet** (44 ký tự urlsafe-base64, decode ra 32 byte) và `JWT_SECRET_KEY` set + non-empty. Không in giá trị. **Không** kiểm `DATABASE_URL` (không có secret cho nó, prod dùng default container DB theo AC10). Chạy trước bước `[3/5]`.

### Bước 5 — Liên tục hoá khoá cho dữ liệu prod (AC3, AC4)

Viết `OMS/backend/scripts/reencrypt_system_configs.py`: đọc `FERNET_KEY_OLD` + `FERNET_KEY`, với mỗi row `system_configs` thử decrypt bằng key mới (đã ok → bỏ qua, idempotent), không được thì decrypt bằng key cũ → encrypt lại bằng key mới; toàn bộ trong 1 transaction; `--dry-run` in số row sẽ đổi; chỉ log `config_key` + số lượng, **không log giá trị**. Test unit: encrypt bằng key A → re-encrypt sang B → decrypt được bằng B; chạy lần 2 không đổi gì.

Ghi vào docs quy trình 1 lần trên prod, **đúng thứ tự này** (sai thứ tự là mất dữ liệu): backup `system_configs` → set `FERNET_KEY` mới trong `.env` → chạy migration của [[OMS-010-introduce-alembic-migrations]] để `config_value` thành `TEXT` → `reencrypt --dry-run` với `FERNET_KEY_OLD` = key fallback cũ (`git show 3116bf3~1:OMS/backend/models.py`, **chỉ truyền qua env, không commit**) → chạy thật.

> **Lối tắt hợp lệ, ghi rõ cho User chọn:** Zalo App Secret Key / OA Access Token / OA Refresh Token **dù sao cũng phải rotate** vì đã lộ cleartext trong `index.md`. Nếu `system_configs` chỉ chứa mấy row Zalo config đó, thì thay vì re-encrypt có thể chỉ cần: deploy với `FERNET_KEY` mới → vào UI nhập lại token Zalo mới. Rẻ hơn và giải quyết luôn việc rotate. Executor **vẫn phải viết script** (AC3/AC4) vì nó cần cho lần rotate key sau này, nhưng ghi cả 2 đường vào docs.

### Bước 6 — Smoke check thật sự chạm đường decrypt (AC5)

Thêm vào `[4.1/5] Post-deploy smoke checks`:
1. `docker exec oms_backend python -c ...` đọc 1 row `system_configs` qua model `SystemConfig` và assert decrypt được (chỉ in `config_key`, không in giá trị). Deploy FAIL nếu decrypt lỗi.
2. **Kiểm auth xuyên service**: lấy 1 token từ identity-service rồi gọi 1 endpoint OMS cần auth, assert **không phải 401**. Lý do: OMS và identity dùng chung `JWT_SECRET_KEY`, và bước này là cái duy nhất bắt được sự cố "2 bên lệch key" — kể cả khi vòng sau ai đó rotate key (xem `inbox.md` mục 8).

### Bước 6b — Rotate JWT dùng chung (AC12)

Làm **sau** Bước 6 để smoke check của AC5 bắt được lỗi lệch key ngay: đổi `JWT_SECRET_KEY` ở `identity-service/docker-compose.prod.yml:12` + `PMI/docker-compose.prod.yml:11` + `OMS/docker-compose.prod.yml:27` sang `${JWT_SECRET_KEY:?...}`, ghi secret vào **cả 3** file `.env` bằng `upsert_env_var`, bỏ fallback literal trong `OMS/backend/utils/auth.py:6-10` và `identity-service/backend/utils/jwt.py:8`, xác định WMS xác thực bằng cách nào. Chỉ sửa đúng dòng `JWT_SECRET_KEY` trong compose của PMI/identity — 2 file đó đang có thay đổi RDS chưa commit của session khác.

### Bước 7 — Docs + kiểm tra cuối (AC7, AC8, AC11)

Ghi `OMS/README.md`: danh sách env bắt buộc (`FERNET_KEY`, `DATABASE_URL`, `JWT_SECRET_KEY`, `CORS_ALLOWED_ORIGINS`), cách sinh Fernet key, quy trình re-encrypt, và **cách cutover sang RDS = đổi `DATABASE_URL` trong `OMS/.env` trên host** (không đổi code). Kiểm `OMS/backend/.env.prod` có bị git-track không (`git ls-files --error-unmatch`) — hiện đang được `.gitignore:19` chặn, xác nhận lại. Chạy full suite. Cuối cùng viết đoạn kết luận "push-readiness" theo AC11.

## Sub-tasks

- [ ] Khôi phục key fallback cũ từ `git show 3116bf3~1:OMS/backend/models.py` để làm `FERNET_KEY_OLD` — **chỉ truyền qua env lúc chạy script, không commit vào bất kỳ file nào**.
- [ ] Kiểm tra `system_configs` trên prod hiện có bao nhiêu row / những `config_key` nào, trước khi chọn (a) hay (b) — nếu chỉ có vài row Zalo config thì có thể đơn giản là nhập lại qua UI sau khi đổi key (phương án (c), rẻ nhất — nếu chọn thì phải ghi rõ là User sẽ phải nhập lại token, và task vẫn cần AC1/AC2/AC5/AC7).
- [ ] Xác nhận `CORS_ALLOWED_ORIGINS` mặc định `https://oms.topvnsport.com` (`OMS/docker-compose.prod.yml:26`) đúng với domain thật đang dùng — health check ở `deploy_prod.sh:107-116` đang gọi `http://` (không phải https), kiểm tra xem có lệch scheme gây CORS block không.
- [ ] Kiểm tra `refresh_zalo_tokens_job` (`OMS/backend/main.py:107+`, APScheduler) — nếu key sai thì job này cũng fail âm thầm mỗi lần chạy; đảm bảo lỗi decrypt được log rõ.

## ⚠️ Project Gate — KHÔNG tự chạy lên prod DB / prod host

- Executor **KHÔNG** ssh vào prod, **KHÔNG** chạy `alembic upgrade head`, `ALTER TABLE`, hay re-encrypt script trên prod DB. Chỉ viết script + wire vào deploy, test trên local.
- Việc apply lên prod (set env, chạy migration của [[OMS-010-introduce-alembic-migrations]], chạy re-encrypt) là quyết định của User, cần xác nhận riêng, **độc lập với coordination mode**.
- Thứ tự an toàn khi apply lên prod: backup `system_configs` → set `FERNET_KEY` → (OMS-010) `alembic upgrade head` để `config_value` thành `TEXT` → chạy re-encrypt `--dry-run` → chạy thật. Đổi thứ tự (re-encrypt trước khi cột thành TEXT) có thể bị truncate ciphertext dài → mất dữ liệu.

## Pre-scan findings (OCR)

`ocr scan --path OMS/backend/main.py,OMS/backend/models.py,OMS/backend/database.py,OMS/backend/utils/crypto.py,deploy_prod.sh` → **28 finding** (5 high). Chỉ finding liên quan task này:

- 🔴 **high · security · `deploy_prod.sh:7`** — "uses environment variables for configuration but lacks validation that they are properly set before use" → **AC2**. Làm luôn cho `PUBLIC_HOST`/`DOMAIN_NAME` vì cùng chỗ.
- 🔴 **high · security · `OMS/backend/utils/crypto.py:8-15`** — `FERNET_KEY` chỉ check tồn tại, **không check format** → đã ghi thẳng vào AC2.
- 🔴 **high · security · `OMS/backend/models.py:94-111`** — Fernet key load ở **module import time** ⇒ thiếu/sai key thì app không start được (crash-loop), và `alembic/env.py` của [[OMS-010-introduce-alembic-migrations]] `import models` nên **migration cũng sẽ fail**. Đây chính là lý do preflight (AC2) phải chặn TRƯỚC khi build/start, chứ không để phát hiện qua crash-loop.
- 🔴 **high · security · `OMS/backend/utils/crypto.py:22-29`** — decrypt catch-all rồi re-raise `ValueError`, **mất exception type + traceback**. Cộng với `models.py:118-125` (medium: "generic ValueError … difficult to distinguish between invalid ciphertext and actual decryption failure") ⇒ khi key mismatch xảy ra trên prod, log **không phân biệt được** "sai key" vs "ciphertext hỏng/bị truncate". AC5 (smoke check) và việc chẩn đoán key continuity đều phụ thuộc vào chỗ này — executor nên cải thiện message/log tại 2 điểm đó ở mức đủ để phân biệt 2 nguyên nhân (không cần refactor lại toàn bộ crypto.py).
- **medium · performance · `crypto.py:8-15`** — `get_fernet()` tạo `Fernet` instance mới mỗi lần gọi. Nếu script re-encrypt (AC3b) chạy trên nhiều row thì đáng cache instance trong script; *không bắt buộc sửa `crypto.py`*.

**Ngoài scope task này:** `deploy_prod.sh:52` hardcode Docker Compose v2.29.7 + tải binary không verify checksum, `:21-27` SSH opts lặp lại, `:30-39` rsync full mỗi lần deploy, `:59-93` inline bash + heredoc khó bảo trì, health check duplicate → **chưa có task nào cho deploy-script hardening**, chưa làm. `crypto.py:17-20` inconsistency giữa `encrypt_value`/`decrypt_value` với chuỗi rỗng → [[OMS-009-add-input-validation]].

## Verifier (LLM-Modulo, `.claude/verifier-rules.yaml`)

- ✅ `no-circular-deps` — `depends_on: [OMS-010]`, OMS-010 có `depends_on: []`.
- ⚠️ `files-exist` — 3/4 path xác nhận qua graph; `OMS/backend/scripts/reencrypt_system_configs.py` là file **mới**, đã comment trong `files:`.
- ⚠️ `reasonable-scope` — blast radius 49 file > 8, **đã split**: phần migration tooling nằm ở OMS-010, task này chỉ env/secret/deploy.
- ✅ `tests-for-changes` — 6 test hiện hữu + AC4 thêm test cho script mới.
- ❌ `no-conflicting-tasks` — **VI PHẠM, phát hiện 2026-07-25**: [[OMS-012-rds-migration]] đang ở `status: dispatched` và có `OMS/docker-compose.prod.yml` trong `files:` — trùng trực tiếp với AC1/AC9 của task này. Nghiêm trọng hơn cả việc trùng file: OMS-012 **bỏ service `db` khỏi `docker-compose.prod.yml` và chuyển sang RDS Aurora**, tức `DATABASE_URL` sẽ đổi ⇒ ảnh hưởng cả `deploy_prod.sh` (dòng `docker exec oms_backend alembic upgrade head` của OMS-010 giả định DB là container `oms_db`) và cách `.env` được nạp. Thuộc epic RDS/S3 migration cùng với `DEVOPS-001`/`DEVOPS-002`, `WMS-006-rds-migration`, `PMI-023-rds-s3-migration`.
  ⇒ **Phải chốt thứ tự với User trước khi dispatch OMS-011**: OMS-011 trước OMS-012 (rồi OMS-012 giữ nguyên cơ chế `.env` upsert), hay OMS-012 trước (rồi OMS-011 viết lại AC1/AC9 theo cấu hình RDS)? Không dispatch khi chưa chốt.
- ⚠️ Trùng `files:` với OMS-010 ở `deploy_prod.sh` + `OMS/docker-compose*.yml`. OMS-010 hiện `changes-requested` ⇒ `depends_on: [OMS-010]` vẫn giữ: OMS-010 phải pass + merge trước.

## AC bổ sung — tách cutover RDS ra khỏi `git push` (thêm 2026-07-25)

- [ ] **AC10** *(VIẾT LẠI 2026-07-25 sau khi User xác nhận "dữ liệu được migration hết sang RDS và S3 rồi")*: **KHÔNG khôi phục service `oms_db`. Prod trỏ RDS là ĐÚNG.** Việc còn lại là gỡ credentials ra khỏi file git-tracked.

  ⚠️ Phiên bản trước của AC10 yêu cầu khôi phục `oms_db` + đổi default về container DB — **đã bị bãi bỏ**, đừng làm theo. Lý do bãi bỏ: AC đó dựa trên `topvnsport-devops/docs/prod-infrastructure.md` ghi RDS *"Created, not connected yet"* và OMS *"Needs migrate to RDS"*, tức RDS còn rỗng. User xác nhận doc đó **đã lỗi thời**: data migration sang RDS + S3 đã xong.

  **Chưa kiểm chứng được từ phía coordinator** (ghi lại để executor xác minh trước khi tin): không có `psql` trên máy này và việc kết nối vào DB prod bằng credential bị chặn. TCP tới `topvnsport-db.cluster-copm008y8icu.us-east-1.rds.amazonaws.com:5432` **mở** từ máy dev. Executor **phải verify 3 điều này trước khi coi AC10 là xong** và ghi kết quả vào PR description:
  1. Database `oms` trên RDS tồn tại và có bảng `system_configs` **kèm dữ liệu** (`select count(*) from system_configs`), khớp với container DB cũ (`docker exec oms_db psql -U postgres -d oms_db -c "select count(*) from system_configs"`). Runbook `topvnsport-devops/docs/migration-runbook.md:189` dump từ container tên `oms-db` và database tên `oms`, nhưng compose thật đặt `container_name: oms_db` và `POSTGRES_DB: oms_db` ⇒ **lệnh trong runbook có thể đã chạy sai tên** — đây là chỗ dễ sai nhất, kiểm trước tiên.
  2. Auth: `postgres:postgres` có kết nối được RDS không, hay cluster chỉ nhận **IAM Database Authentication** (`prod-infrastructure.md:26` ghi IAM auth). Nếu là IAM auth thì `DATABASE_URL` dạng password sẽ **không kết nối được** và phải xử lý riêng (token 15 phút không nhét được vào `.env` tĩnh).
  3. Bảng `alembic_version` trên database `oms` — nếu chưa có thì lần deploy tới `alembic upgrade head` sẽ đi vào đúng nhánh "adopt existing schema" mà [[OMS-010-introduce-alembic-migrations]] vừa làm (đã được review verify là chạy sạch), nhưng vẫn nên xác nhận.

  **Việc phải làm:**
  1. `OMS/docker-compose.prod.yml:12` hiện `DATABASE_URL=${DATABASE_URL:-postgresql://postgres:postgres@database-topvnsport.cluster-...rds.amazonaws.com:5432/oms}` — **default này chứa mật khẩu master của RDS trong file git-tracked**. Giờ RDS là DB thật của prod nên đây là secret thật, đúng loại vấn đề mà AC1 xử lý cho `FERNET_KEY`. Đổi thành `${DATABASE_URL:?DATABASE_URL is required}`.
  2. `OMS/backend/core/config.py`: bỏ default chứa endpoint + credentials, raise `RuntimeError` nếu thiếu `DATABASE_URL`.
  3. ⚠️ **Mục 3 và 4 dưới đây đã được AC14 thay thế** (User xác nhận 3 project dùng chung 1 RDS host, chỉ khác database) — làm theo AC14, không làm theo mục 3. Giữ lại để hiểu bối cảnh: **`DATABASE_URL` chưa có trong GitHub secrets** (User xác nhận danh sách: `DEPLOY_PATH`, `DEPLOY_SSH_KEY`, `EC2_HOST`, `EC2_USER`, `FERNET_KEY`, `JWT_SECRET_KEY`, `PUBLIC_HOST`, `SSH_KNOWN_HOSTS`) ⇒ chọn 1 và ghi rõ:
     - (a) **báo User thêm secret `DATABASE_URL`** rồi ghi vào `.env` qua `upsert_env_var` như `FERNET_KEY` — nhất quán, khuyến nghị; hoặc
     - (b) tạo `$DEPLOY_PATH/OMS/.env` một lần trên EC2 chứa `DATABASE_URL` (file đã được `deploy_prod.sh:31-33` loại khỏi rsync nên không bị ghi đè), deploy không cần biết secret.
     - Với (b), bước preflight AC2 **không** được đòi `DATABASE_URL` ở phía runner (nó chỉ tồn tại trên host).
  4. `OMS/backend/.env.prod` đang chứa `DATABASE_URL` — xác nhận nó vẫn bị `.gitignore` (`.env.*`) chặn: `git ls-files --error-unmatch OMS/backend/.env.prod` phải fail.

  📌 **Ảnh hưởng tới push**: với dữ liệu đã ở RDS, push **không còn là rủi ro mất dữ liệu**. Nhưng vẫn chưa push được cho tới khi AC9 xong: `OMS/docker-compose.prod.yml:13` là `- FERNET_KEY` pass-through, nếu host không có giá trị thì `models.py:94-111` raise `RuntimeError` lúc import ⇒ `oms_backend` crash-loop ⇒ **OMS sập** (không chỉ deploy fail). Xem AC11.

- [ ] **AC11**: Sau khi AC1–AC10 xong, `git push` phải **an toàn**: verify bằng cách rà lại toàn bộ đường deploy (`deploy_prod.sh` → compose → entrypoint) và trả lời được: prod lấy `FERNET_KEY`/`JWT_SECRET_KEY`/`DATABASE_URL` từ đâu, `alembic upgrade head` chạy trên DB nào, và nếu thiếu bất kỳ biến nào thì fail ở đâu với message gì. Ghi kết luận vào PR description — đây là căn cứ để User bấm push.

- [ ] **AC12** *(thêm 2026-07-25 sau khi User cho phép logout hàng loạt)*: `JWT_SECRET_KEY` của **cả 3 service cùng đọc từ một GitHub secret duy nhất** — đây là điều kiện để rotate mà không sập auth:
  - `identity-service/docker-compose.prod.yml:12` — đang **hardcode literal** `identity_jwt_secret_key_2026_change_me_in_prod`, đổi thành `- JWT_SECRET_KEY=${JWT_SECRET_KEY:?JWT_SECRET_KEY is required}`. Đây là nơi **SIGN** token (`identity-service/backend/utils/jwt.py:25`).
  - `PMI/docker-compose.prod.yml:11` — cùng literal, đổi y hệt. (`PMI/backend/utils/auth.py:8` đọc `os.environ["JWT_SECRET_KEY"]`, đã fail-fast sẵn.)
  - `OMS/docker-compose.prod.yml:27` — đổi từ `${JWT_SECRET_KEY:-...}` sang `${JWT_SECRET_KEY:?...}`.
  - `deploy_prod.sh`: dùng cùng hàm `upsert_env_var` của AC9 để ghi `JWT_SECRET_KEY` vào **cả 3** file `.env`: `$DEPLOY_PATH/OMS/.env`, `$DEPLOY_PATH/PMI/.env`, `$DEPLOY_PATH/identity-service/.env`. Không ghi đè biến khác trong các file đó.
  - `.github/workflows/deploy.yml`: thêm `JWT_SECRET_KEY: ${{ secrets.JWT_SECRET_KEY }}` (User đã thêm secret này ngày 2026-07-25).
  - Bỏ fallback literal trong code: `OMS/backend/utils/auth.py:6-10` (hiện fallback về literal khi `ENV != production`) và `identity-service/backend/utils/jwt.py:8` (fallback `super_secret_key_change_me_in_production`). Fallback dev thì giữ được, nhưng **không được** là literal đang dùng trên prod — nếu cần default cho dev thì đặt giá trị khác hẳn và ghi rõ "dev only".
  - **WMS**: `grep -rn "JWT_SECRET_KEY" WMS/` không ra kết quả ⇒ phải xác định WMS xác thực request bằng cách nào (internal service token? không auth?) và ghi kết luận vào PR description. Nếu WMS cũng verify JWT bằng đường khác thì phải xử lý cùng, nếu không sẽ lệch key.
  - **Verify sau khi đổi**: `grep -rn "identity_jwt_secret_key_2026_change_me_in_prod" .` chỉ còn xuất hiện ở file dev/test (`PMI/docker-compose.yml`, `identity-service/docker-compose.dev.yml`), **không còn ở bất kỳ `*.prod.yml` nào**.
  - ✅ **KHÔNG có logout thật**: User xác nhận (2026-07-25) giá trị GitHub secret `JWT_SECRET_KEY` **đúng bằng literal đang dùng** `identity_jwt_secret_key_2026_change_me_in_prod` ⇒ AC12 là **refactor thuần** (bỏ hardcode, 3 service cùng đọc 1 secret), token đang lưu ở client vẫn hợp lệ. User cũng đã đồng ý trước đó là logout thì "ko sao cả" nếu có, nên đây là đường an toàn nhất: bỏ được hardcode mà không gián đoạn ai.
  - ⚠️ **Rotate thật vẫn chưa làm**: vì giá trị secret = literal đã nằm công khai trong repo, ai đọc được repo vẫn forge được JWT admin cho PMI/OMS/identity. Sau khi AC12 xong, việc rotate chỉ còn là **đổi giá trị secret trên GitHub + redeploy** (không phải sửa code nữa) — đã ghi `inbox.md` mục 8.
  - Smoke check của AC5 (lấy token từ identity → gọi endpoint OMS → assert không 401) là **bước bắt buộc** để chứng minh 3 service đã cùng key.

⚠️ **Lưu ý phối hợp**: `PMI/docker-compose.prod.yml` và `identity-service/docker-compose.prod.yml` **đang có thay đổi chưa commit** của đợt RDS/S3 (session khác, PMI-023). Chỉ sửa đúng dòng `JWT_SECRET_KEY`, không format lại file, không revert thay đổi RDS trong đó. Đã ghi vào `inbox.md` mục 8.

- [ ] **AC13** 🔴 *(thêm 2026-07-25 — nếu bỏ qua thì OMS-011 sẽ làm CI fail, và CI fail thì `deploy.yml` KHÔNG BAO GIỜ chạy)*: job `validate-compose` trong `.github/workflows/ci.yml` chạy
  ```bash
  docker compose -f PMI/docker-compose.prod.yml config > /dev/null
  docker compose -f OMS/docker-compose.prod.yml config > /dev/null
  docker compose -f WMS/docker-compose.prod.yml config > /dev/null
  docker compose -f web/docker-compose.prod.yml config > /dev/null
  ```
  **không set biến env nào**. `docker compose config` thực hiện interpolation, nên `${FERNET_KEY:?...}` (AC1) và `${JWT_SECRET_KEY:?...}` (AC12) sẽ làm lệnh này **exit non-zero** ⇒ `validate-compose` fail ⇒ `ci-success` fail (job này fail là fail cứng, thấy ở `ci.yml`: `if [[ "${{ needs.validate-compose.result }}" == "failure" ]]; then exit 1`) ⇒ `deploy.yml` (trigger `workflow_run` khi CI `success`) không chạy.

  Chọn 1 trong 2, ghi lý do vào PR description:
  - (a) thêm block `env:` với **giá trị dummy** cho job `validate-compose` (`FERNET_KEY`, `JWT_SECRET_KEY`) — vẫn kiểm được interpolation, dummy không phải secret thật; **hoặc**
  - (b) đổi sang `docker compose ... config --no-interpolate` — không cần env, nhưng mất phần kiểm interpolation.
  - Khuyến nghị (a).

  Nhớ cả `PMI/docker-compose.prod.yml` (AC12 cũng đổi file này sang `:?`). `identity-service/docker-compose.prod.yml` hiện **không** nằm trong danh sách `validate-compose` — cân nhắc thêm vào, nhưng không bắt buộc trong task này.

  **Verify**: chạy đúng lệnh của CI trong shell **không có** các biến đó (`env -u FERNET_KEY -u JWT_SECRET_KEY docker compose -f OMS/docker-compose.prod.yml config > /dev/null`) và phải exit 0.

- [ ] **AC14** 🔴 *(thêm 2026-07-25 sau khi User xác nhận: EC2 **chưa có** `OMS/.env`, và **3 project dùng chung 1 RDS host, chỉ khác database**)*: `DATABASE_URL` phải được **ghép từ secret chung**, không phải một secret trọn gói.
  - **Bỏ** cách dùng một secret `DATABASE_URL` (đã ghi ở AC10) — sai thiết kế: một secret không mang được 3 database khác nhau, và nhồi host+password vào 4 secret riêng thì rotate mật khẩu RDS phải sửa 4 chỗ.
  - **Secret User sẽ tạo**: `RDS_HOST` = `topvnsport-db.cluster-copm008y8icu.us-east-1.rds.amazonaws.com` **(endpoint MỚI — cluster đã đổi tên)**, `RDS_USER` = `postgres`, `RDS_PASSWORD` = *(mật khẩu master RDS)*. **Không** tạo `DATABASE_URL`.
  - `OMS/docker-compose.prod.yml`:
    ```yaml
    - DATABASE_URL=postgresql://${RDS_USER:?RDS_USER is required}:${RDS_PASSWORD:?RDS_PASSWORD is required}@${RDS_HOST:?RDS_HOST is required}:5432/<tên db của OMS>
    ```
    Tên database **không phải secret**, hardcode trong compose.
  - `.github/workflows/deploy.yml`: thêm `RDS_HOST`, `RDS_USER`, `RDS_PASSWORD` vào block `env:` của step "Run production deploy".
  - `deploy_prod.sh`: ghi 3 biến đó vào `.env` của **từng service** bằng chính hàm `upsert_env_var` đã có (AC9) — OMS chắc chắn, PMI/WMS/identity nếu compose của họ cũng cần (kiểm trước, các file đó đang do session RDS sửa).
  - ⚠️ **Tên database chưa xác định** — phải làm rõ trước khi coi AC14 xong: `migration-runbook.md:189` ghi `docker exec oms-db pg_dump -U postgres oms` (database `oms`) nhưng `OMS/docker-compose.yml` thật đặt `container_name: oms_db` + `POSTGRES_DB: oms_db`. Xác định bằng `psql -h <RDS_HOST> -U postgres -l` trên EC2 rồi dùng đúng tên. **Đoán sai tên database = OMS nối vào database rỗng hoặc không tồn tại.** Đã yêu cầu User chạy lệnh này và trả kết quả.
  - ⚠️ **EC2 chưa có `$DEPLOY_PATH/OMS/.env`** (User xác nhận) ⇒ **không được** giả định file đã tồn tại. Hàm ghi `.env` phải tự `touch` + `chmod 600` khi file chưa có (AC9 đã yêu cầu, verify lại trong bối cảnh này), và toàn bộ giá trị prod phải đến từ GitHub secrets — không có đường nào khác.
  - ✅ **ĐÃ XÁC NHẬN (2026-07-25)**: cluster **chỉ có IAM Database Authentication, không có password tĩnh**; database OMS tên **`oms`**; cần `sslmode=require` ⇒ phần password của AC14 **được thay bằng AC15**. Làm theo AC15.

- [ ] **AC15** 🔴 *(thay thế AC14 phần password, 2026-07-25 — User xác nhận RDS dùng **IAM Database Authentication, KHÔNG có password tĩnh**; token TTL 15 phút; database OMS tên **`oms`**; `sslmode=require`)*

  **Vấn đề**: `.env` tĩnh không thể chứa token 15 phút. Nặng hơn: `OMS/backend/database.py:6` tạo `engine = create_engine(DATABASE_URL)` một lần ở import-time và SQLAlchemy giữ **connection pool** — kết nối đầu tiên có thể thành công, nhưng khi pool mở connection mới sau 15 phút thì token đã hết hạn ⇒ OMS chết dần chứ không chết ngay, kiểu lỗi khó chẩn đoán nhất. Cùng vấn đề với `alembic/env.py` (nó tự tạo engine riêng qua `engine_from_config`).

  ✅ **ĐÃ GIẢI QUYẾT Ở TẦNG HẠ TẦNG (2026-07-25)** — session DEVOPS đã cấp cluster mới dùng **password auth, KHÔNG IAM**, và dữ liệu đã migrate:

  | Item | Value |
  |---|---|
  | Cluster | `topvnsport-db` *(đổi tên từ `database-topvnsport`)* |
  | Endpoint | `topvnsport-db.cluster-copm008y8icu.us-east-1.rds.amazonaws.com` |
  | Port | `5432` |
  | User | `postgres` |
  | Password | *(không ghi vào file này — file git-tracked; lấy từ GitHub secret `RDS_PASSWORD`)* |
  | Auth | **Password**, không IAM |
  | Data | ✅ đã migrate |

  ⇒ Đường (B) bên dưới **không cần làm nữa** (giữ lại làm tham chiếu cho task devops ở `inbox.md` mục 12 nếu sau này quay lại IAM auth). Làm đường (A):

  **(A) — dùng password auth *(cluster đã ở trạng thái này, không cần bật gì thêm)*:**
  - Secrets trên GitHub: `RDS_HOST`, `RDS_USER`, `RDS_PASSWORD`, và **`RDS_SSLMODE=require`** *(bắt buộc — Aurora đang bật SSL, DSN thiếu `sslmode` sẽ fail)*.
  - `OMS/docker-compose.prod.yml`:
    ```yaml
    - DATABASE_URL=postgresql://${RDS_USER:?}:${RDS_PASSWORD:?}@${RDS_HOST:?}:5432/oms?sslmode=${RDS_SSLMODE:-require}
    ```
    Tên database là **`oms`** (User đã xác nhận — chấm dứt nghi vấn `oms` vs `oms_db` từ `migration-runbook.md:189`).
  - `deploy_prod.sh`: ghi `RDS_HOST`/`RDS_USER`/`RDS_PASSWORD`/`RDS_SSLMODE` vào `.env` từng service bằng `upsert_env_var` (AC9). **Không code Python nào phải đổi** — đây là lý do chọn (A).
  - Verify: `psql "host=$RDS_HOST port=5432 dbname=oms user=postgres sslmode=require password=$RDS_PASSWORD" -c "select count(*) from system_configs"` chạy được từ EC2.

  **(B) — dùng IAM token đúng cách *(KHÔNG làm trong task này, đã ghi `inbox.md` để mở task devops)*.** Cần đủ 4 thứ, thiếu 1 là OMS sập lúc runtime:
  1. `boto3` vào `OMS/backend/requirements.txt` (hiện **chưa có**, chỉ có `psycopg2-binary`).
  2. Hook `do_connect` của SQLAlchemy để sinh token **mỗi lần mở connection**, không phải 1 lần lúc import:
     ```python
     @event.listens_for(engine, "do_connect")
     def _iam_token(dialect, conn_rec, cargs, cparams):
         cparams["password"] = boto3.client("rds", region_name=REGION).generate_db_auth_token(
             DBHostname=HOST, Port=5432, DBUsername=USER)
         cparams["sslmode"] = "require"
     ```
     Phải áp cho **cả** `database.py` và `alembic/env.py` (2 engine khác nhau).
  3. EC2 instance profile có quyền `rds-db:connect` trên đúng resource `arn:aws:rds-db:us-east-1:402631154151:dbuser:<cluster-resource-id>/postgres` — **chưa xác minh là đã có**.
  4. Trong Postgres: `GRANT rds_iam TO postgres` (hoặc user riêng). `migration-runbook.md` không có bước này.
  ⇒ (B) đúng đắn hơn về bảo mật (không có credential sống lâu) nhưng là thay đổi runtime xuyên 4 service + phụ thuộc 2 thứ chưa xác minh ở tầng AWS. Không phù hợp để làm cùng lúc với việc gỡ chặn bug prod.

  **Nếu User từ chối bật password auth** thì AC này chuyển sang (B) và task phải được re-plan — đừng tự chọn đường vòng kiểu sinh token trong entrypoint rồi ghi vào `.env` (sống 15 phút, sập sau đó).

## Findings từ reviewer
- [ ] HIGH — AC14/AC15 chưa implement: OMS/docker-compose.prod.yml:12 đòi DATABASE_URL nhưng workflow và deploy_prod.sh:125 chỉ cấp FERNET_KEY/JWT_SECRET_KEY, mà EC2 không có OMS/.env sẵn. Deploy sẽ fail SAU KHI PMI đã redeploy xong, tức nửa hệ thống đã đổi. Làm theo AC15 (ghép DSN từ RDS_HOST/RDS_USER/RDS_PASSWORD/RDS_SSLMODE, database tên 'oms', kèm sslmode=require)
- [ ] HIGH — smoke-check heredoc chỉ truyền DEPLOY_PATH, biến DOMAIN_NAME ở deploy_prod.sh:241 không được set ở phía remote. Reviewer chạy thật và xác nhận 'set -u' thoát với 'DOMAIN_NAME: unbound variable' — tức smoke check LUÔN fail, kéo deploy fail
- [ ] HIGH — token smoke check dùng staff_id=0 (deploy_prod.sh:240) nhưng identity-service/backend/routers/auth.py:113 từ chối id falsey, nên kể cả sau khi sửa DOMAIN_NAME thì check vẫn trả 401. Phải dùng staff_id hợp lệ hoặc cách xác thực khác
- [ ] HIGH — AC10/AC11 chưa có phần verify trên prod (commit tự khai không đụng prod host/DB): chưa xác nhận nội dung database oms trên RDS, cơ chế auth, bảng alembic_version, và ciphertext Fernet có đọc được không. Phần hạ tầng đã chuyển sang session DEVOPS qua inbox mục 14, executor chờ kết quả rồi verify
- [ ] MEDIUM — upsert_env_var (deploy_prod.sh:45) làm HỎNG file .env đã tồn tại mà KHÔNG có newline cuối: key mới bị nối thẳng vào value của dòng trước. Reviewer reproduce được, và test hiện tại bỏ sót case này. Đây đúng là kiểu lỗi 'ghi đè mất biến khác' mà User yêu cầu tránh — phải thêm test cho file không có trailing newline

## Verify hạ tầng — 4 secret đã sẵn sàng (2026-07-25)

Coordinator đã tạo đủ 6 secret trên GitHub (`gh secret list` xác nhận): `FERNET_KEY`, `JWT_SECRET_KEY`, `RDS_HOST`, `RDS_USER`, `RDS_PASSWORD`, `RDS_SSLMODE`. Từ đây `deploy_prod.sh` có đủ nguyên liệu.

**Coordinator KHÔNG verify được nội dung RDS** — kết nối tới DB prod bằng credential bị permission classifier chặn (2 lần), và không lách. Executor/reviewer chạy với cờ bypass nên làm được. Đây là phần còn thiếu của AC10/AC11, **bắt buộc** trước khi coi task xong (chỉ đọc, KHÔNG ghi):

```python
# chạy trong repo topvnsport, password lấy từ env, KHÔNG hardcode
python3 -c "
import os, psycopg2
c=psycopg2.connect(host=os.environ['RDS_HOST'], user=os.environ['RDS_USER'],
                   password=os.environ['RDS_PASSWORD'], dbname='oms',
                   sslmode='require', connect_timeout=10)
cur=c.cursor()
cur.execute(\"select count(*) from system_configs\");            print('rows:', cur.fetchone()[0])
cur.execute(\"select config_key, length(config_value) from system_configs order by 1\"); print(cur.fetchall())
cur.execute(\"select to_regclass('alembic_version') is not null\"); print('alembic_version:', cur.fetchone()[0])
cur.execute(\"select data_type, character_maximum_length from information_schema.columns \"
            \"where table_name='system_configs' and column_name='config_value'\"); print('config_value:', cur.fetchone())
"
```

Cần trả lời được 4 câu, ghi vào PR description:
1. `system_configs` trên database `oms` có bao nhiêu row? **Nếu 0** thì token Zalo chưa sang RDS ⇒ sau deploy phải nhập lại qua UI (dù sao cũng phải nhập lại vì token đã lộ, xem `inbox.md` mục 2) — không phải lỗi, nhưng phải nói rõ cho User.
2. `config_value` là `text` hay còn `character varying(500)`? Nếu còn 500 thì migration `0003_config_value_text` **chưa được áp** lên RDS ⇒ đúng bug gốc của OMS-006 vẫn còn, và lần deploy tới entrypoint sẽ tự chạy `alembic upgrade head` để sửa — xác nhận điều đó xảy ra được.
3. Có bảng `alembic_version` chưa? Nếu chưa thì lần deploy tới sẽ đi vào nhánh "adopt existing schema" của OMS-010 (đã được review verify chạy sạch trên Postgres có schema chưa stamp).
4. Ciphertext trong `config_value` giải mã được bằng `FERNET_KEY` hiện tại không? Nếu không thì phải chạy `reencrypt_system_configs.py` với `FERNET_KEY_OLD` = key fallback cũ (`git show 3116bf3~1:OMS/backend/models.py`), hoặc chọn đường nhập lại token qua UI.

## Causal Analysis
- **Root cause**: OMS-006 biến việc thiếu FERNET_KEY thành lỗi fatal ở import-time (models.py:94-111 raise RuntimeError) nhưng KHÔNG có bất kỳ bước nào đưa secret đó tới host prod. Nguyên nhân sâu hơn: toàn bộ credential của hệ thống được quản lý bằng cách hardcode giá trị vào file git-tracked (docker-compose.prod.yml, core/config.py, utils/auth.py) thay vì đi qua một kênh secret — nên 'sửa security' ở tầng code lại tạo ra lỗi vận hành ở tầng deploy.
- **Mechanism**: compose để '- FERNET_KEY' pass-through và ':-default' cho JWT/DATABASE_URL; deploy_prod.sh không ghi biến env nào lên host; .github/workflows/deploy.yml không truyền secret nào ngoài SSH/EC2. Chuỗi hệ quả: biến không tồn tại lúc 'docker compose up' → oms_backend raise RuntimeError lúc import → crash-loop → health check fail → deploy fail (hoặc tệ hơn: OMS sập nếu container cũ đã bị thay). Đồng thời mật khẩu master RDS và literal JWT dùng chung nằm công khai trong repo, và không có smoke check nào chạm đường decrypt nên lỗi chỉ lộ ra khi user bấm vào trang cấu hình Zalo.
- **Counterfactual**: Nếu ngay từ đầu compose dùng dạng ${VAR:?} và deploy_prod.sh upsert secret từ GitHub vào .env trên host, thì OMS-006 deploy được ngay trong cùng một lần và OMS-011 không cần tồn tại. Và nếu bước post-deploy có smoke check đọc-giải-mã một row system_configs, thì lỗi 500 Zalo OA đã bị bắt ngay tại lần deploy gây ra nó, thay vì để user phát hiện trên prod rồi mới lần ngược về schema drift.
- **Pattern**: [[secret-not-plumbed-to-runtime]]
