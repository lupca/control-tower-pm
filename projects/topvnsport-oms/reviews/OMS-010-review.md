---
id: OMS-010
task_path: projects/topvnsport-oms/tasks/OMS-010-introduce-alembic-migrations.md
project: topvnsport-oms
result_ref: a953632
executor: @gpt-5.6-luna-high
reviewer: "@claude-opus"
status: passed
issued: 2026-07-25
verdict: pass
verdict_date: 2026-07-25
---

# Phiếu Review: OMS-010 — Đưa Alembic vào OMS backend (như PMI) + migration fix config_value schema drift

- Dự án: topvnsport-oms (`/home/lupca/projects/topvnsport`)
- Task gốc: `projects/topvnsport-oms/tasks/OMS-010-introduce-alembic-migrations.md`
- Result-ref: a953632
- Executor: @gpt-5.6-luna-high
- Reviewer: @claude-opus
- Ngày phát phiếu: 2026-07-25

## Acceptance Criteria cần verify
## Tiêu chí nghiệm thu (AC)

- [ ] **AC1**: `OMS/backend/` có bộ alembic hoàn chỉnh theo đúng khuôn của PMI: `alembic.ini` (`script_location = alembic`, `prepend_sys_path = .`, `sqlalchemy.url` để trống), `alembic/env.py` (đọc `DATABASE_URL` từ env, `target_metadata = Base.metadata`, `compare_type=True`), `alembic/script.py.mako`, `alembic/versions/`. Tham chiếu: `PMI/backend/alembic.ini` + `PMI/backend/alembic/env.py`.
- [ ] **AC2**: `alembic` được thêm vào `OMS/backend/requirements.txt` (PMI đã có ở dòng 12).
- [ ] **AC3**: Có **baseline revision** phản ánh schema hiện tại (toàn bộ bảng trong `models.py`), để: DB rỗng → `alembic upgrade head` dựng đủ schema; DB đang chạy (prod/local) → `alembic stamp <baseline>` rồi upgrade các revision sau mà không dựng lại bảng. Ghi rõ trong docstring của revision cách stamp cho DB có sẵn.
- [ ] **AC4**: Có revision **sau baseline** đổi `system_configs.config_value` sang `TEXT` — idempotent, chạy được trên DB mà cột đang là `VARCHAR(500)` **và** trên DB mà cột đã là `TEXT`. Có `downgrade()` (hoặc ghi rõ lý do không downgrade được vì có thể mất dữ liệu).
- [ ] **AC5**: Logic của `ensure_zalo_otp_schema()` (`main.py:49-79`: thêm cột `otp_verifications.zalo_message_id` + index `ix_otp_verifications_zalo_message_id`) được chuyển thành alembic revision, và hàm này **bị xoá khỏi `main.py`** — không còn ALTER TABLE bằng string concat ở startup (OCR flag đây là "unsafe query construction for schema modifications").
- [ ] **AC6**: `Base.metadata.create_all(bind=engine)` bị xoá khỏi `main.py:46`. Test suite vẫn tự dựng schema được (fixture trong `OMS/backend/tests/conftest.py` / `test_main.py` dùng SQLite in-memory — nếu fixture đang dựa vào `create_all` ở import-time của `main`, phải sửa fixture để tự gọi `create_all`, KHÔNG được để test phụ thuộc side-effect của module `main`).
- [ ] **AC7**: `deploy_prod.sh` chạy migration cho OMS: thêm `alembic upgrade head` cho container OMS backend (container name là `oms_backend` theo `OMS/docker-compose.prod.yml`, **không phải** `oms-api` — kiểm tra lại `docker ps` naming trước khi viết), đặt cùng chỗ với 2 dòng của PMI/WMS (`deploy_prod.sh:96-100`).
- [ ] **AC8**: Migration **không được** bị `|| true` che lỗi. Nếu `alembic upgrade head` fail → deploy fail rõ ràng (hiện tại cả 2 dòng PMI/WMS đều có `|| true`, migration hỏng vẫn báo deploy thành công). Áp dụng cho dòng OMS mới; với 2 dòng PMI/WMS sẵn có, bỏ `|| true` luôn nếu không phá health-check hiện tại — nếu thấy rủi ro thì giữ nguyên và ghi lý do vào PR description (đừng tự ý mở rộng scope).
- [ ] **AC9**: Toàn bộ test hiện hữu trong `tests:` vẫn xanh 100% (baseline OMS-006: 42 passed).
- [ ] **AC10**: Thêm **1 test mới** khẳng định `alembic upgrade head` cho ra schema khớp `Base.metadata` (ví dụ: upgrade lên head trên DB trống rồi so sánh bằng `alembic.autogenerate.compare_metadata()` → phải rỗng). Lý do: `get_knowledge_gaps_tool` cho thấy toàn bộ hàm `upgrade()` của PMI/identity-service là **untested hotspot** (degree 204/103/90/73) — migration ở monorepo này chưa từng có test nào, đừng lặp lại.

## Definition of Done (AGENTS.md mục 3)
- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: OMS/backend/tests/test_config.py::test_sms_config_endpoints, OMS/backend/tests/test_config.py::test_sms_config_endpoints_support_long_tokens, OMS/backend/tests/test_config.py::test_sms_config_mutation_requires_admin, OMS/backend/test_main.py::test_zalo_token_refresh_updates_system_config, OMS/backend/test_main.py::test_get_zalo_config_returns_all_masked_fields, OMS/backend/tests/test_otp.py, OMS/backend/tests/test_webhooks.py::test_zalo_webhook_endpoint, e2e_tests/tests/test_oms_admin_sms.py::test_oms_admin_zalo_settings, e2e_tests/tests/test_storefront_otp_flow.py::test_storefront_otp_checkout_flow
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (xác nhận reviewer @claude-opus ≠ executor @gpt-5.6-luna-high)

## Test gợi ý chạy trong repo code
- `OMS/backend/tests/test_config.py::test_sms_config_endpoints`
- `OMS/backend/tests/test_config.py::test_sms_config_endpoints_support_long_tokens`
- `OMS/backend/tests/test_config.py::test_sms_config_mutation_requires_admin`
- `OMS/backend/test_main.py::test_zalo_token_refresh_updates_system_config`
- `OMS/backend/test_main.py::test_get_zalo_config_returns_all_masked_fields`
- `OMS/backend/tests/test_otp.py`
- `OMS/backend/tests/test_webhooks.py::test_zalo_webhook_endpoint`
- `e2e_tests/tests/test_oms_admin_sms.py::test_oms_admin_zalo_settings`
- `e2e_tests/tests/test_storefront_otp_flow.py::test_storefront_otp_checkout_flow`

## Câu hỏi rủi ro (vòng 3 — reviewer MỚI sau 2 lần `changes`)

Bạn là reviewer **thứ hai** của task này. `rejections: 2` đã bật `reviewer_rotation_alert`, nên reviewer được đổi từ @gpt-5.6-sol sang bạn để có góc nhìn thứ ba. **Phạm vi vòng này rất hẹp** — hãy tận dụng để soi kỹ thay vì rà lại từ đầu.

### Trạng thái tích luỹ (đừng review lại phần đã được verify)

| Vòng | Ref | Verdict | Kết quả |
|---|---|---|---|
| 1 | `024c3f4` | changes | 4 finding |
| 2 | `5cceee9` | changes | @gpt-5.6-sol verify **3/4 đã fix**: existing-schema adoption (kể cả schema thiếu một phần + 2 tiến trình upgrade đồng thời), clean startup + seed ordering/error handling, bỏ `|| true` PMI/WMS. Còn 1 finding: test PostgreSQL bị skip mặc định + CI không chạy pytest |
| 3 | `a953632` | ← bạn | Chỉ còn **AC17** |

Ref `a953632` gồm 2 commit mới so với `5cceee9`:
- `badfc51` — **AC17**: thêm `services: postgres` + `Run pytest` vào job `oms-backend` trong `.github/workflows/ci.yml`.
- `a953632` — **không thuộc AC nào của task này**: sửa job `validate-compose` để seed `.env.prod` từ `.env.prod.example`, vì CI trên `main` đang đỏ do commit `eec9556` của epic RDS (PMI/identity compose có `env_file` trỏ file bị gitignore). Coordinator tự làm để gỡ chặn deploy. Xem `inbox.md` mục 10. **Review nó như một phần của ref**, nhưng đừng fail AC17 vì nó.

### Câu hỏi

1. **AC17 — bằng chứng "không skip"**: executor khai test PostgreSQL "runs and passes, not skipped" và suite `44 passed`. Verify cơ chế: `OMS/backend/tests/test_migrations.py` bật nhánh PostgreSQL bằng biến/điều kiện gì, và job `oms-backend` có thật sự set đúng biến đó? Nếu điều kiện dựa vào việc kết nối được Postgres thì kiểm health check của service có chặn race lúc container chưa ready.
2. **AC17 — pytest có chạy đúng thư mục không**: job dùng `defaults.run.working-directory: OMS/backend`. `pytest -v --tb=short` từ đó có thu được **cả** `test_main.py` (ở `OMS/backend/`) và `tests/*` không? Vòng 2 baseline là 44 passed (có PG) / 43 passed + 1 skipped (không PG) — con số trong CI phải khớp, nếu ít hơn thì có test bị bỏ sót.
3. **AC17 — env cho test**: `OMS/backend/tests/conftest.py:1-6` và `test_main.py:7-11` cần `FERNET_KEY`, `INTEGRITY_MODE`/`ENV=development`, `ALLOW_TEST_OTP_ENDPOINT`. Verify job set đủ, và `FERNET_KEY` dùng trong CI **không phải** key prod.
4. **`a953632` — cách seed có đúng chỗ không**: bước seed chạy **trước** bước validate trong cùng job chứ? Và nó chỉ tạo file khi thiếu (`[ ! -f ]`), không ghi đè? Coordinator đã verify bằng sandbox dựng từ `git archive HEAD` (nên `.env.prod` local bị loại): trước seed PMI fail đúng lỗi CI, sau seed PMI + identity đều `config` OK. Bạn tự verify lại độc lập.
5. 🔴 **An toàn push — câu quan trọng nhất, trả lời trong notes**: `eec9556` (RDS) **đã nằm trên origin/main**, và `OMS/docker-compose.prod.yml:12` hiện là `DATABASE_URL=${DATABASE_URL:-<endpoint RDS thật>}`. CI đang đỏ là thứ duy nhất chặn deploy. Nếu ref này được push → CI xanh → `deploy.yml` chạy → OMS trỏ vào **RDS rỗng** (doc hạ tầng ghi RDS "Created, not connected yet", dữ liệu prod vẫn ở container DB). Theo bạn, ref này có an toàn để push chưa, hay phải chờ [[OMS-011-fix-fernet-key-continuity-prod]] AC10 đổi default về container DB trước? (Coordinator đánh giá là **chưa an toàn** và sẽ không push.)
6. **Regression**: 2 commit này chỉ đụng `.github/workflows/ci.yml` — xác nhận không có file nào khác trong `badfc51..a953632`, và job `validate-compose` không bị đổi ngoài bước seed.

## Review Toolchain
Chạy theo toolchain của repo đích; preflight các tool đã đăng ký trước khi review.

## Trả kết quả
`/verdict OMS-010 <pass|changes> --reviewer @claude-opus [--commit <hash>] [--notes "..."]`
