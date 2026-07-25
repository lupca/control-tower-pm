---
id: OMS-010
title: "Đưa Alembic vào OMS backend (như PMI) + migration fix config_value schema drift"
status: done
priority: urgent
risk: high
deadline: null
executor: "@gpt-5.6-luna-high"
reviewer: "@claude-opus"
result_ref: "a953632"
depends_on: []
files:
  - OMS/backend/main.py
  - OMS/backend/models.py
  - OMS/backend/database.py
  - OMS/backend/requirements.txt
  - OMS/backend/tests/conftest.py
  - OMS/docker-compose.yml
  - OMS/docker-compose.prod.yml
  - deploy_prod.sh
  # các file dưới đây CHƯA tồn tại, executor phải tạo mới (không có trong graph):
  - OMS/backend/alembic.ini
  - OMS/backend/alembic/env.py
  - OMS/backend/alembic/script.py.mako
  - OMS/backend/alembic/versions/
  - .github/workflows/ci.yml  # Spec Gate lần 2 (2026-07-25) — AC17, job oms-backend chưa chạy pytest
flows: [send_otp, verify_otp, update_sms_config, create_order, confirm_order]
tests:
  - OMS/backend/tests/test_config.py::test_sms_config_endpoints
  - OMS/backend/tests/test_config.py::test_sms_config_endpoints_support_long_tokens
  - OMS/backend/tests/test_config.py::test_sms_config_mutation_requires_admin
  - OMS/backend/test_main.py::test_zalo_token_refresh_updates_system_config
  - OMS/backend/test_main.py::test_get_zalo_config_returns_all_masked_fields
  - OMS/backend/tests/test_otp.py
  - OMS/backend/tests/test_webhooks.py::test_zalo_webhook_endpoint
  - e2e_tests/tests/test_oms_admin_sms.py::test_oms_admin_zalo_settings
  - e2e_tests/tests/test_storefront_otp_flow.py::test_storefront_otp_checkout_flow
dispatched: 2026-07-25
in_review: 2026-07-25
predicted_success: medium
prediction_factors:
  score: 0.5
  deductions:
    - "blast_radius > 8: -0.3 (get_impact_radius: 128 file bị ảnh hưởng trong 2 hop)"
    - "blast_radius > 15: -0.2 (cộng dồn -0.5)"
  notes:
    - "blast radius bị phóng đại: main.py là FastAPI entrypoint import toàn bộ routers, nên 2-hop traversal chạm gần hết OMS backend. Diện sửa thực tế nhỏ (bỏ create_all + ensure_zalo_otp_schema, thêm alembic scaffold)."
    - "không trừ hub/bridge: không file nào trong files: nằm trong get_hub_nodes(top_n=50)/get_bridge_nodes(top_n=50). Nhưng 2 bridge test NẰM TRÊN flow bị ảnh hưởng (test_storefront_otp_checkout_flow betweenness 0.0109, test_oms_admin_zalo_settings 0.0041) → đã đưa vào tests:."
    - "không trừ no-tests: đã có test hiện hữu cho SystemConfig/OTP."
    - "không trừ past-failure: OMS-001..006 đều pass."
confidence_interval: [0.35, 0.65]
created: 2026-07-25
updated: 2026-07-25
rejections: 2
---

# OMS-010: Đưa Alembic vào OMS backend (như PMI) + migration fix config_value schema drift

> Dự án: [[projects/topvnsport-oms/topvnsport-oms]]

## Bối cảnh (tại sao cần task này)

Sau khi [[OMS-006-fix-security-critical]] pass (commit `3116bf3`), root cause của lỗi 500 trên `PUT /api/configs/sms` — cột `system_configs.config_value` là `VARCHAR(500)` trên DB thật trong khi model khai báo unbounded — **vẫn còn nguyên trên prod**, vì OMS không có công cụ migration nào:

| Bằng chứng | Vị trí |
|---|---|
| OMS **không có** alembic (PMI/WMS/identity-service đều có) | `find` → chỉ `PMI/backend/alembic`, `WMS/backend/alembic`, `identity-service/backend/alembic` |
| CI/CD chỉ migrate PMI + WMS, **không có OMS** | `deploy_prod.sh:98-100`: `docker exec pim-api alembic upgrade head`, `docker exec wms-api alembic upgrade head` |
| OMS dựa vào `create_all()`, **không bao giờ ALTER cột đã tồn tại** | `OMS/backend/main.py:46` |
| Migration tay duy nhất chỉ xử lý 1 cột khác | `OMS/backend/main.py:49-79` `ensure_zalo_otp_schema()` → chỉ `otp_verifications.zalo_message_id` |
| Commit 3116bf3 không chứa ALTER/migration nào | AC8 của OMS-006, reviewer đã verify |

⇒ Deploy bao nhiêu lần thì prod schema vẫn drift. Đây cũng là điều kiện tiên quyết cho [[OMS-008-add-business-invariants]] và [[OMS-009-add-input-validation]] (cả hai đều cần thay đổi schema/constraint, không thể làm qua `create_all`).

**Pattern match:** không có pattern nào trong `knowledge/patterns/` khớp signature "model đổi định nghĩa cột nhưng DB thật không migrate theo, do repo thiếu migration tool" (gần nhất là `mandatory-tool-preflight` — cùng họ "thiếu tool → im lặng fallback sang đường degraded", nhưng không phải cùng vấn đề). Đã đề xuất tạo pattern mới `schema-drift-no-migration-tool` với User, chờ xác nhận.

## Tiêu chí nghiệm thu (AC)

- [x] **AC1**: `OMS/backend/` có bộ alembic hoàn chỉnh theo đúng khuôn của PMI: `alembic.ini` (`script_location = alembic`, `prepend_sys_path = .`, `sqlalchemy.url` để trống), `alembic/env.py` (đọc `DATABASE_URL` từ env, `target_metadata = Base.metadata`, `compare_type=True`), `alembic/script.py.mako`, `alembic/versions/`. Tham chiếu: `PMI/backend/alembic.ini` + `PMI/backend/alembic/env.py`.
- [x] **AC2**: `alembic` được thêm vào `OMS/backend/requirements.txt` (PMI đã có ở dòng 12).
- [x] **AC3**: Có **baseline revision** phản ánh schema hiện tại (toàn bộ bảng trong `models.py`), để: DB rỗng → `alembic upgrade head` dựng đủ schema; DB đang chạy (prod/local) → `alembic stamp <baseline>` rồi upgrade các revision sau mà không dựng lại bảng. Ghi rõ trong docstring của revision cách stamp cho DB có sẵn.
- [x] **AC4**: Có revision **sau baseline** đổi `system_configs.config_value` sang `TEXT` — idempotent, chạy được trên DB mà cột đang là `VARCHAR(500)` **và** trên DB mà cột đã là `TEXT`. Có `downgrade()` (hoặc ghi rõ lý do không downgrade được vì có thể mất dữ liệu).
- [x] **AC5**: Logic của `ensure_zalo_otp_schema()` (`main.py:49-79`: thêm cột `otp_verifications.zalo_message_id` + index `ix_otp_verifications_zalo_message_id`) được chuyển thành alembic revision, và hàm này **bị xoá khỏi `main.py`** — không còn ALTER TABLE bằng string concat ở startup (OCR flag đây là "unsafe query construction for schema modifications").
- [x] **AC6**: `Base.metadata.create_all(bind=engine)` bị xoá khỏi `main.py:46`. Test suite vẫn tự dựng schema được (fixture trong `OMS/backend/tests/conftest.py` / `test_main.py` dùng SQLite in-memory — nếu fixture đang dựa vào `create_all` ở import-time của `main`, phải sửa fixture để tự gọi `create_all`, KHÔNG được để test phụ thuộc side-effect của module `main`).
- [x] **AC7**: `deploy_prod.sh` chạy migration cho OMS: thêm `alembic upgrade head` cho container OMS backend (container name là `oms_backend` theo `OMS/docker-compose.prod.yml`, **không phải** `oms-api` — kiểm tra lại `docker ps` naming trước khi viết), đặt cùng chỗ với 2 dòng của PMI/WMS (`deploy_prod.sh:96-100`).
- [x] **AC8**: Migration **không được** bị `|| true` che lỗi. Nếu `alembic upgrade head` fail → deploy fail rõ ràng (hiện tại cả 2 dòng PMI/WMS đều có `|| true`, migration hỏng vẫn báo deploy thành công). Áp dụng cho dòng OMS mới; với 2 dòng PMI/WMS sẵn có, bỏ `|| true` luôn nếu không phá health-check hiện tại — nếu thấy rủi ro thì giữ nguyên và ghi lý do vào PR description (đừng tự ý mở rộng scope).
- [x] **AC9**: Toàn bộ test hiện hữu trong `tests:` vẫn xanh 100% (baseline OMS-006: 42 passed).
- [x] **AC10**: Thêm **1 test mới** khẳng định `alembic upgrade head` cho ra schema khớp `Base.metadata` (ví dụ: upgrade lên head trên DB trống rồi so sánh bằng `alembic.autogenerate.compare_metadata()` → phải rỗng). Lý do: `get_knowledge_gaps_tool` cho thấy toàn bộ hàm `upgrade()` của PMI/identity-service là **untested hotspot** (degree 204/103/90/73) — migration ở monorepo này chưa từng có test nào, đừng lặp lại.

## Verification (executor tự chạy trước khi báo xong)

```bash
cd /home/lupca/projects/topvnsport
# 1. unit/integration test OMS backend
docker compose -f OMS/docker-compose.yml exec oms_backend pytest -q
# hoặc theo TEST_INFRA.md nếu khác

# 2. migration chạy sạch trên DB trống
docker compose -f OMS/docker-compose.yml exec oms_backend alembic upgrade head
docker compose -f OMS/docker-compose.yml exec oms_backend alembic current

# 3. drift check: sau upgrade, autogenerate không được sinh thêm gì
docker compose -f OMS/docker-compose.yml exec oms_backend alembic check   # hoặc revision --autogenerate rồi verify diff rỗng

# 4. cột đã là TEXT
docker compose -f OMS/docker-compose.yml exec oms_db psql -U postgres -d oms_db \
  -c "\d+ system_configs"
```

## Plan

Thứ tự bắt buộc — mỗi bước chạy được test trước khi sang bước sau.

### Bước 1 — Scaffold alembic (AC1, AC2)

Khuôn lấy từ PMI, **giữ y hệt convention** (`WORKDIR /app` giống nhau ở cả 2 Dockerfile nên path tương thích):

- `OMS/backend/requirements.txt`: thêm `alembic` (PMI để không pin version, dòng 12 — làm giống).
- `OMS/backend/alembic.ini`: copy từ `PMI/backend/alembic.ini` — `script_location = alembic`, `prepend_sys_path = .`, `sqlalchemy.url =` (để trống, env.py set runtime).
- `OMS/backend/alembic/env.py`: copy `PMI/backend/alembic/env.py`, chỉ đổi default DSN cho khớp `OMS/backend/database.py:5` → `postgresql://postgres:postgres@oms_db:5432/oms_db` (**lưu ý**: default trong `database.py` là `localhost:15434` cho dev ngoài docker, còn trong container là host `oms_db`; ưu tiên đọc `DATABASE_URL` từ env, default chỉ là fallback). Giữ `target_metadata = Base.metadata`, `compare_type=True`, `import models  # noqa: F401`.
- `OMS/backend/alembic/script.py.mako`: copy nguyên từ PMI.
- Tạo `OMS/backend/alembic/versions/` (rỗng).

⚠️ `env.py` `import models` ⇒ `alembic` sẽ **đòi `FERNET_KEY`** (Fernet key load ở import-time, `models.py:94-111`). Kiểm tra ngay ở bước này: `docker compose -f OMS/docker-compose.yml exec oms_backend alembic current` phải chạy được. Nếu fail vì thiếu key ⇒ đó là hành vi đúng nhưng phải ghi vào docs (AC7 của OMS-011 lo phần prod).

### Bước 2 — Baseline revision (AC3)

- `alembic revision --autogenerate -m "baseline oms schema"` trên một DB **rỗng** (không phải DB local đang có data — dùng DB tạm để autogenerate không bị lệch).
- Rà lại file sinh ra bằng tay: `EncryptedString` là `TypeDecorator` với `impl = SqlString` unbounded ⇒ autogenerate phải ra `sa.String()`/`TEXT` cho `system_configs.config_value`, **không được** ra `VARCHAR(500)`. Nếu ra sai, sửa tay.
- Docstring của revision ghi rõ: DB đã có schema thì chạy `alembic stamp <baseline_rev>` (KHÔNG upgrade), DB rỗng thì `alembic upgrade head`.

### Bước 3 — Revision cho zalo_message_id (AC5)

Chuyển nguyên logic `ensure_zalo_otp_schema()` (`main.py:49-79`) thành revision sau baseline:
- `op.add_column('otp_verifications', sa.Column('zalo_message_id', sa.String(100), nullable=True))`
- `op.create_index('ix_otp_verifications_zalo_message_id', 'otp_verifications', ['zalo_message_id'])`
- Idempotent như bản cũ: baseline (Bước 2) autogenerate từ `models.py` nên **đã bao gồm** cột này ⇒ revision này sẽ conflict trên DB rỗng. Xử lý: dùng `op.get_bind()` + `sa.inspect()` để skip nếu cột/index đã tồn tại (đúng tinh thần `IF NOT EXISTS` của bản cũ ở `main.py:57-70`). Đây là hệ quả không tránh được của việc baseline hoá một DB đang drift — ghi rõ lý do trong comment.

### Bước 4 — Revision đổi `config_value` sang TEXT (AC4)

- `op.alter_column('system_configs', 'config_value', type_=sa.Text(), existing_type=sa.String(500), existing_nullable=True)`.
- Idempotent: check type hiện tại qua `sa.inspect(op.get_bind())` trước khi ALTER; DB đã là TEXT thì no-op (bắt buộc, vì DB local/CI có thể đã đúng).
- `downgrade()`: `Text` → `String(500)` **có thể mất dữ liệu** (ciphertext dài hơn 500). Viết downgrade nhưng raise/abort nếu tồn tại row dài > 500, kèm comment giải thích.

### Bước 5 — Xoá schema-management khỏi `main.py` (AC5, AC6)

- Xoá `Base.metadata.create_all(bind=engine)` (`main.py:46`).
- Xoá hàm `ensure_zalo_otp_schema()` (`main.py:49-79`) + call site (`main.py:81`).
- Dọn import không còn dùng: `from sqlalchemy import inspect as sa_inspect, text` (`main.py:13`) — **kiểm tra `text` còn dùng ở chỗ khác trong file không** trước khi xoá.
- **Test KHÔNG bị ảnh hưởng**: `OMS/backend/tests/conftest.py:28` và `OMS/backend/test_main.py:33` đều tự gọi `Base.metadata.create_all(bind=engine)` trên engine SQLite riêng của chúng. Ngược lại, việc xoá này **cắt** phụ thuộc hiện tại: `from main import app` đang chạy `create_all` + `ensure_zalo_otp_schema()` + seed channels lên **Postgres thật** ngay lúc import ⇒ test hiện phải chạy trong môi trường có `oms_db` reachable. Sau khi xoá, phụ thuộc đó giảm đi (khối seed channels ở `main.py:84-105` vẫn còn — xem note dưới).

> **Note (không phải AC, cần executor tự phán đoán + giải trình trong PR):** khối seed channels `main.py:84-105` vẫn chạy ở import-time và vẫn cần DB thật; OCR cũng flag đây là race condition (medium, concurrency). Chuyển nó vào FastAPI lifespan (file đã import `asynccontextmanager`) sẽ hợp lý hơn, nhưng **không nằm trong AC của task này**. Nếu executor thấy buộc phải sửa để test/migration chạy được thì làm và ghi rõ; nếu không thì để nguyên, đừng tự mở rộng scope.

### Bước 6 — Wire vào CI/CD (AC7, AC8)

Trong `deploy_prod.sh`, cạnh 2 dòng hiện có (`:96-100`):
```bash
sudo docker exec pim-api alembic upgrade head || true
sudo docker exec wms-api alembic upgrade head || true
```
- Thêm dòng cho OMS dùng **đúng container name `oms_backend`** (`OMS/docker-compose.prod.yml: container_name: oms_backend`) — KHÔNG phải `oms-api`. Verify bằng `docker ps` output ở bước `[5/5]` của chính script.
- Dòng mới **không** có `|| true`.
- Về 2 dòng PMI/WMS: OCR flag `high` tại `deploy_prod.sh:91-92` đúng chỗ này. Bỏ `|| true` cho cả 2 nếu không phá health check; nếu thấy rủi ro (ví dụ WMS chưa có revision nào) thì giữ nguyên + ghi lý do vào PR description.
- Lưu ý thứ tự: block này hiện nằm **sau** khi các stack đã `up -d`, tức app đã khởi động (và có thể đã crash vì schema cũ) trước khi migrate. Giữ nguyên vị trí để không đổi hành vi của PMI/WMS, nhưng ghi nhận hạn chế này trong PR.

### Bước 7 — Test cho migration (AC10)

Test mới (đặt ở `OMS/backend/tests/test_migrations.py`):
- Dựng DB tạm rỗng (Postgres test container nếu có, hoặc SQLite nếu alembic revision tương thích — **kiểm tra trước**: `op.alter_column` với `type_` trên SQLite bị hạn chế, có thể phải skip trên SQLite và chỉ chạy trên Postgres → nếu vậy dùng `pytest.mark.skipif`).
- `alembic upgrade head` bằng `alembic.command.upgrade` + `Config`.
- Assert `alembic.autogenerate.compare_metadata(context, Base.metadata) == []`.
- Assert `system_configs.config_value` là TEXT/không có length limit.
- Chạy `upgrade head` 2 lần → lần 2 no-op (idempotency).

### Bước 8 — Docs

Ghi vào `OMS/README.md` (tạo nếu chưa có): cách tạo revision, cách stamp DB có sẵn, cảnh báo "KHÔNG dùng `create_all` nữa".

## Sub-tasks

- [ ] Đọc `PMI/backend/alembic.ini` + `PMI/backend/alembic/env.py` + 1 revision mẫu (`PMI/backend/alembic/versions/c9a2d4b80123_remove_stock_column.py`) làm khuôn — giữ cùng convention với monorepo, đừng tự phát minh layout mới.
- [ ] Xác nhận tên container OMS backend thật (`oms_backend` trong compose) trước khi sửa `deploy_prod.sh` — sai tên thì `docker exec` fail và (nếu còn `|| true`) fail âm thầm.
- [ ] Kiểm tra `OMS/backend/tests/conftest.py` + `OMS/backend/test_main.py` xem test có phụ thuộc `create_all` ở import-time của `main` không, sửa fixture trước khi xoá dòng đó.
- [ ] Viết test cho migration (AC10) — hiện monorepo chưa có test nào cho migration (knowledge gap).
- [ ] Ghi vào `OMS/README.md` (hoặc `CLAUDE.md` của repo) cách tạo revision mới + cách stamp DB có sẵn, để lần sau không ai lại `create_all`.

## ⚠️ Project Gate — KHÔNG tự chạy migration lên prod DB

Task này chỉ **tạo** migration + wire vào CI/CD. Executor **KHÔNG** được ssh/exec vào prod DB để chạy `alembic upgrade head` hay `ALTER TABLE`. Việc apply lên prod cần User xác nhận riêng (xem `projects/topvnsport-oms/topvnsport-oms.md` §Quy tắc phê duyệt riêng), và phải làm **sau** [[OMS-011-fix-fernet-key-continuity-prod]] vì có rủi ro dữ liệu không giải mã được.

## Pre-scan findings (OCR)

`ocr scan --path OMS/backend/main.py,OMS/backend/models.py,OMS/backend/database.py,OMS/backend/utils/crypto.py,deploy_prod.sh` → **28 finding** (5 high). JSON đầy đủ: `/tmp/claude-1000/-home-lupca-projects-control-tower/f3a5119f-268c-435c-ba20-83d4c3c081f6/scratchpad/ocr-oms-010.json` (file tạm, executor nên chạy lại `ocr scan` trong repo nếu cần).

**Liên quan trực tiếp task này:**

- 🔴 **high · security · `deploy_prod.sh:91-92`** — "executes database migrations with silent failure handling (`|| true`) … could mask critical migration errors, system might be left in an inconsistent state". → chính là **AC8**. Đây là finding độc lập xác nhận `|| true` phải bỏ.
- **medium · maintainability · `deploy_prod.sh:59-93`** — inline bash + heredoc lẫn lộn, khó đọc. Khi thêm dòng migration cho OMS, giữ nguyên style hiện tại; đừng refactor cả script trong task này.
- **`main.py` — unsafe query construction cho schema modification** (string concat trong `ensure_zalo_otp_schema`, thấy ở project_summary của OCR) → **AC5** xử lý bằng cách xoá hẳn, chuyển sang alembic revision.
- 🔴 **high · security · `models.py:94-111`** — Fernet key load ở **module import time** ⇒ app không start nếu `FERNET_KEY` thiếu/sai. Quan trọng với task này: `alembic/env.py` `import models` (như PMI làm) ⇒ **chạy `alembic upgrade head` cũng sẽ đòi `FERNET_KEY`**. Executor phải tính đến điều này khi wire migration vào `deploy_prod.sh`, nếu không migration sẽ fail ở bước import chứ không phải ở SQL.

**Ngoài scope task này** (ghi lại để không ai tưởng đã xử lý):

- `main.py:86-105` (medium, concurrency) race khi seed channels; `main.py:112-116` `threading.Lock` không đủ cho multi-process; `main.py:175-177` + `198-201` broad except / shutdown không handle exception → [[OMS-007-fix-race-conditions]].
- `models.py:7-8` `utcnow()` bỏ tzinfo; `models.py:42-43` Numeric(10,2) tiền tệ; `models.py:44` `shipping_address` cho phép chuỗi rỗng; `models.py:142` `phone_number` không validate format; `models.py:60` thiếu index `order_id` → [[OMS-009-add-input-validation]] / [[OMS-008-add-business-invariants]]. **Lưu ý**: mọi fix loại này về sau đều cần migration ⇒ thêm lý do task này phải xong trước.
- `database.py:5` (medium ×2, security) `DATABASE_URL` không validate + default trỏ DB dev; `database.py:7-10` engine/session global → *chưa có task*. `alembic/env.py` sẽ đọc cùng biến này, executor **đừng nhân bản logic parse**, chỉ `os.getenv("DATABASE_URL", ...)` như PMI.
- `crypto.py:8-15`/`17-20`/`22-29` (2 high + medium): key format không validate, `get_fernet()` tạo instance mới mỗi lần gọi, catch-all mất exception type → [[OMS-011-fix-fernet-key-continuity-prod]] + [[OMS-009-add-input-validation]].
- `deploy_prod.sh:7` (high) env var không validate → [[OMS-011-fix-fernet-key-continuity-prod]] AC2. `deploy_prod.sh:52` hardcode Docker Compose v2.29.7 + tải binary không verify checksum, `:21-27` SSH opts lặp, `:30-39` rsync full mỗi lần, health check duplicate → **chưa có task nào**, chưa làm.

## Verifier (LLM-Modulo, `.claude/verifier-rules.yaml`)

- ✅ `no-circular-deps` — `depends_on: []`.
- ⚠️ `files-exist` — 8/12 path xác nhận qua graph; 4 path alembic là file **mới**, đã comment rõ trong `files:`.
- ⚠️ `reasonable-scope` — blast radius 128 file > 8, **đã split**: task này chỉ làm migration tooling; phần env/secret prod tách sang OMS-011.
- ✅ `tests-for-changes` — 9 test hiện hữu + AC10 thêm test cho knowledge gap (migration untested).
- ✅ `no-conflicting-tasks` — OMS-007/008/009 đang `todo` (không `dispatched`/`in-review`); OMS-006 đã `done`.

## Findings từ reviewer
- [ ] HIGH — deploy_prod.sh:93 chạy 'alembic upgrade head' trên prod schema đã tồn tại nhưng chưa stamp. Reviewer reproduce trên PostgreSQL: migration exit 1 với DuplicateTable ngay tại 0001_baseline_oms_schema.py:27 (create customers). Bước 'alembic stamp' chỉ nằm trong docstring, chưa được tích hợp vào rollout
- [ ] HIGH — môi trường local/CI sạch không còn dựng được schema OMS: create_all đã bỏ nhưng không có gì chạy alembic (Docker CMD start uvicorn trực tiếp, .github/workflows/e2e.yml:62 chỉ start services), nên E2E trên runner sạch không thể đạt DoD. Kèm theo, khối seed channels chạy trước khi bảng tồn tại và swallow lỗi
- [ ] MEDIUM — AC8 chưa hoàn thành: 2 dòng PMI/WMS ở deploy_prod.sh:91 vẫn còn '|| true' mà không ghi lý do như AC8 bắt buộc
- [ ] MEDIUM — test_migrations.py:16 chỉ cover SQLite sạch. Cần thêm PostgreSQL cho đúng đường prod: schema có sẵn, stamp baseline, thiếu cột/index zalo, VARCHAR(500) sang TEXT kèm assert dữ liệu không mất

## Vòng 2 — bối cảnh RDS đã thay đổi dưới chân task này (2026-07-25)

⚠️ **Đọc kỹ trước khi sửa.** Sau khi `024c3f4` được commit, [[OMS-012-rds-migration]] (executor `@antigravity-3.6-medium`, thuộc epic RDS/S3 cùng `DEVOPS-001`/`DEVOPS-002`) đã chạy và để lại **thay đổi chưa commit** ngay trên `main`, đụng đúng file của task này. User đã quyết định (2026-07-25) **giữ nguyên trên main, OMS-010 điều chỉnh theo RDS** — không tách branch. Vậy nên:

Trạng thái file hiện tại (đã kiểm bằng đọc file, không phải giả định):
- `OMS/backend/core/config.py` **(mới)** — tập trung `DATABASE_URL`, default là endpoint RDS thật kèm credentials `postgres:postgres`.
- `OMS/backend/database.py` — giờ `from core.config import DATABASE_URL`.
- `OMS/backend/alembic/env.py` — giờ `from core.config import DATABASE_URL` rồi `os.getenv("DATABASE_URL", DATABASE_URL)`.
- `OMS/docker-compose.prod.yml` — **service `oms_db` và volume `oms_db_data` đã bị xoá**, `DATABASE_URL` trỏ RDS. `- FERNET_KEY` pass-through vẫn còn.
- `OMS/docker-compose.yml` (local) — **vẫn có `oms_db`**, không đổi ⇒ mọi lệnh verify local trong mục "Verification" ở trên vẫn dùng được nguyên.
- `deploy_prod.sh` — đã commit ở `024c3f4`, OMS-012 KHÔNG sửa. Dòng `sudo docker exec oms_backend alembic upgrade head` vẫn chạy được với RDS (container `oms_backend` vẫn tồn tại, chỉ khác là nó nối tới RDS qua `DATABASE_URL`) ⇒ **AC7 vẫn đúng, không phải viết lại**.

**Điều quan trọng nhất:** finding HIGH số 1 **không hề nhẹ đi** khi lên RDS — trái lại. `DEVOPS-002` migrate dữ liệu prod vào RDS ⇒ RDS sẽ có sẵn đầy đủ bảng nhưng **không có** row `alembic_version` ⇒ đúng kịch bản "schema có sẵn, chưa stamp" mà reviewer đã reproduce ra `DuplicateTable`. Fix finding 1 là bắt buộc bất kể container hay RDS.

**Ngoài scope task này** (đừng sửa, đã giao chỗ khác): `DATABASE_URL` default chứa endpoint RDS + credentials `postgres:postgres` trong `core/config.py` và `OMS/docker-compose.prod.yml` — cùng loại anti-pattern `:-default` mà User đã cấm với `FERNET_KEY`; đã giao cho [[OMS-011-fix-fernet-key-continuity-prod]] AC9. Nếu bạn phải sửa `core/config.py` vì lý do khác, **đừng** đụng phần default đó.

## Vòng 2 — AC bổ sung (fix 4 finding)

- [ ] **AC11** *(finding 1)*: `alembic upgrade head` chạy thành công trên **cả 3 loại DB**, không cần thao tác tay: (a) DB trống, (b) DB **đã có schema nhưng chưa stamp** (đúng trạng thái prod và RDS sau DEVOPS-002), (c) DB đã stamp. Chọn cơ chế nào tuỳ bạn (baseline idempotent với `checkfirst`, hoặc bước tự phát hiện "có bảng nhưng không có `alembic_version`" → `stamp` baseline rồi upgrade tiếp), nhưng **hướng dẫn stamp bằng tay trong docstring là KHÔNG đủ** — reviewer đã reproduce `DuplicateTable` exit 1 tại `0001_baseline_oms_schema.py:27`. Nếu chọn auto-stamp thì phải an toàn khi 2 tiến trình chạy đồng thời.
- [ ] **AC12** *(finding 2)*: Môi trường **sạch** (local mới clone, CI runner) dựng được schema mà không cần ai gõ lệnh. Đề xuất: entrypoint của container backend chạy `alembic upgrade head` trước khi `uvicorn` khởi động (`OMS/backend/Dockerfile` hiện `CMD ["uvicorn", ...]`, không có entrypoint). Phải bao phủ cả `.github/workflows/e2e.yml:62` (workflow chỉ start services, không chạy alembic) — nếu entrypoint xử lý thì workflow không cần sửa, ghi rõ lý do vào PR.
- [ ] **AC13** *(finding 2, phần seed)*: Khối seed channels (`main.py`, chạy ở import-time) **không được** chạy trước khi bảng tồn tại và **không được** nuốt lỗi. Đây giờ là AC bắt buộc, không còn là "note để executor tự quyết" như vòng 1 — reviewer xác nhận nó vỡ ở môi trường sạch. Chuyển vào FastAPI lifespan (file đã import `asynccontextmanager`) hoặc chỗ chạy sau khi migration xong; lỗi phải được log ở mức `error` và không bị `except Exception: pass`.
- [ ] **AC14** *(finding 3)*: Bổ sung lý do giữ `|| true` ở 2 dòng PMI/WMS (`deploy_prod.sh:91-92`) — ghi vào commit message hoặc comment ngay tại dòng đó. Hoặc bỏ `|| true` nếu đã verify không phá health check. AC8 vòng 1 yêu cầu điều này nhưng chưa làm.
- [ ] **AC15** *(finding 4)*: `OMS/backend/tests/test_migrations.py` phải cover **PostgreSQL theo đúng đường prod**, không chỉ SQLite sạch: dựng DB có schema sẵn + `system_configs.config_value VARCHAR(500)` + vài row ciphertext dài + thiếu cột/index zalo → chạy upgrade → assert dữ liệu **không mất/không truncate**, cột thành `TEXT` unbounded, cột+index zalo được tạo, và chạy lần 2 là no-op. Giữ luôn test SQLite hiện có nếu còn chạy được.
- [ ] **AC16**: Toàn bộ test vẫn xanh sau khi OMS-012 đã đổi `database.py`/`env.py` sang `core.config` (baseline vòng 1: 43 passed).

## Findings từ reviewer
- [ ] Round 2 — 3/4 finding vòng 1 đã fix và reviewer verify được: existing-schema adoption (kể cả schema thiếu một phần + 2 tiến trình upgrade đồng thời) PASS, clean startup + seed ordering/error handling PASS, bỏ '|| true' cho PMI/WMS PASS. CÒN LẠI 1 finding: test PostgreSQL cho đường prod chỉ pass khi bật thủ công, mặc định bị SKIP, và job 'oms-backend' trong .github/workflows/ci.yml KHÔNG chạy pytest (chỉ 'python -m py_compile main.py') nên AC15 không được CI bảo vệ — phải wire pytest + service PostgreSQL vào CI cho OMS

## Vòng 3 — AC bổ sung (fix finding còn lại của vòng 2)

Vòng 2 (`ref 5cceee9`): reviewer @gpt-5.6-sol verify được **3/4 finding vòng 1 đã fix** — existing-schema adoption (kể cả schema thiếu một phần và 2 tiến trình upgrade đồng thời), clean startup + seed ordering/error handling, bỏ `|| true` cho PMI/WMS. Còn đúng 1 finding.

- [ ] **AC17** *(finding còn lại)*: Test migration PostgreSQL phải **thật sự chạy trong CI**, không chỉ chạy được khi bật tay.
  - Hiện trạng đã verify: job `oms-backend` trong `.github/workflows/ci.yml` **không chạy pytest** — chỉ có bước `Python syntax check: python -m py_compile main.py`. Toàn bộ 43+ test của OMS chưa từng chạy trên CI. (Job `pmi-backend` thì có `Run pytest`, dùng nó làm khuôn.)
  - Và `OMS/backend/tests/test_migrations.py` mặc định **skip** test PostgreSQL ⇒ ngay cả khi thêm pytest vào CI mà không có Postgres thì AC15 vẫn không được bảo vệ.
  - **Việc phải làm**:
    1. Thêm bước `Run pytest` vào job `oms-backend` (theo khuôn `pmi-backend`), kèm các env test cần thiết (`FERNET_KEY` dev, `INTEGRITY_MODE`/`ENV=development`, `ALLOW_TEST_OTP_ENDPOINT`, `JWT_SECRET_KEY` dummy — xem `OMS/backend/tests/conftest.py:1-6` và `test_main.py:7-11` để biết test cần gì).
    2. Thêm `services: postgres:` (image `postgres:15-alpine`, health check) vào job đó và set biến mà `test_migrations.py` dùng để bật nhánh PostgreSQL, sao cho test PG **chạy thật, không skip**.
    3. **Bằng chứng nghiệm thu**: output pytest trong CI phải cho thấy test PostgreSQL ở trạng thái **passed**, không phải `skipped`. Nếu chạy local thì chứng minh bằng `pytest -v` cho thấy tên test PG + `PASSED` khi có Postgres, và giải thích cơ chế bật trong CI.
  - **Ngoài scope**: job `wms-backend` cũng chỉ `py_compile` (cùng lỗ hổng) — **không sửa** ở task này, đã ghi vào `inbox.md`.
  - ⚠️ Job `validate-compose` trong cùng file: **đừng đụng vào**. Nó sẽ được [[OMS-011-fix-fernet-key-continuity-prod]] AC13 sửa (khi compose chuyển sang dạng `:?` thì job này cần env dummy). Sửa cả 2 nơi trong 1 lượt sẽ đè lên nhau.

## Causal Analysis
- **Root cause**: OMS backend không có công cụ migration nào: schema được quản lý bằng Base.metadata.create_all() cộng một hàm ALTER TABLE viết tay ở startup (ensure_zalo_otp_schema), trong khi PMI/WMS/identity-service đều đã có alembic. Mọi thay đổi định nghĩa cột trong models.py vì thế không bao giờ được áp vào DB đang chạy.
- **Mechanism**: create_all() chỉ tạo bảng còn thiếu, không bao giờ ALTER bảng/cột đã tồn tại. Song song đó deploy_prod.sh chỉ chạy 'alembic upgrade head' cho pim-api và wms-api, không có dòng nào cho OMS, và 2 dòng đó còn bị '|| true' che lỗi. Kết quả: prod schema đứng yên qua mọi lần deploy trong khi model tiến lên, tạo drift âm thầm — system_configs.config_value vẫn là VARCHAR(500) dù model khai unbounded, nên ciphertext Fernet của Zalo access/refresh token (~500+ ký tự) bị từ chối và PUT /api/configs/sms trả 500.
- **Counterfactual**: Nếu OMS có alembic + 'alembic upgrade head' trong deploy ngay từ đầu như PMI/WMS, thì lần đổi config_value sang unbounded (OMS-004/OMS-006) sẽ tự động được áp lên prod ở lần deploy kế tiếp, và lỗi 500 khi lưu cấu hình Zalo OA sẽ không bao giờ xảy ra. Nếu 2 dòng migration của PMI/WMS không bị '|| true', drift ở các service khác cũng đã lộ ra từ sớm thay vì bị che.
- **Pattern**: [[schema-drift-no-migration-tool]]
