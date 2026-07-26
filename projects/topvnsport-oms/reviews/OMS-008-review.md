---
id: OMS-008
task_path: projects/topvnsport-oms/tasks/OMS-008-add-business-invariants.md
project: topvnsport-oms
result_ref: 7f17d6bba3e9f99dbda0525b02870482de1bb02a
executor: "@antigravity"
reviewer: "@claude-opus-5"
status: passed
issued: 2026-07-26
verdict: pass
verdict_date: 2026-07-26
---

# Phiếu Review: OMS-008 — Add business invariants

- Dự án: topvnsport-oms (`/home/lupca/projects/topvnsport`)
- Task gốc: `projects/topvnsport-oms/tasks/OMS-008-add-business-invariants.md`
- Result-ref: 7f17d6bba3e9f99dbda0525b02870482de1bb02a
- Executor: @antigravity
- Ngày phát phiếu: 2026-07-26

## Acceptance Criteria cần verify
- [x] Delete customer với active orders → 409 Conflict
- [x] Delete channel với active orders → 409 Conflict
- [x] Partial WMS cancellation → CANCELLATION_PENDING status + error log
- [x] Soft delete thay vì hard delete cho customers

## Definition of Done (AGENTS.md mục 3)
- [x] Toàn bộ AC pass
- [x] Test liên quan xanh 100%: OMS/backend/test_main.py, OMS/backend/tests/
- [x] Không regression (test khác trong module vẫn xanh)
- [x] Reviewer khác executor (bạn đang review, hãy xác nhận bạn ≠ @antigravity-3.6-high)

## Test gợi ý chạy trong repo code
docker compose -f OMS/docker-compose.yml exec api pytest OMS/backend/tests/ OMS/backend/test_main.py

## Review Toolchain
Chạy review theo repo's toolchain:
  cat .claude/review-toolchain.md
Repo PHẢI khai báo toolchain. Với mỗi tool trong pipeline:
  - Preflight theo knowledge/tools/tool-registry.md (health_check → install nếu cần → re-check)
  - Tool required=hard mà preflight fail sau install → BLOCK + escalate, không review với partial tools
  - /code-review là baseline tool trong registry, chạy cùng (không thay thế) các tools khác
Chạy tất cả tools trong pipeline, aggregate kết quả,
rồi verify từng AC item.

## Trả kết quả
Sau khi review xong, báo lại cho control-tower bằng lệnh:
`/verdict OMS-008 <pass|changes> --reviewer @<tên bạn> [--commit <hash>] [--notes "..."]`

## Kết quả review vòng 4 (@claude-opus-5) — PASS

### Findings vòng 3 đã fix
- [x] BLOCKER auth regression — ĐÃ FIX. 4 endpoint `create/retrieve/update/delete` channels quay lại `get_current_user` (channels.py:21,97,108,133). Verify LIVE trên `:18101` không kèm credential: POST/GET/PUT/DELETE đều trả **401 `Authentication required`** (vòng 3 là 201/200/200/204). Đối chứng `GET /customers/1` cũng 401. Lưu ý: `list_channels` (channels.py:72) vẫn `get_optional_user` nhưng đã như vậy từ 6a0d978 (trước OMS-008) → tiền tồn tại, không thuộc regression này.
- [x] Minor ChannelOut — ĐÃ FIX. OpenAPI `ChannelOut` chỉ còn `{code, id, is_active, name}`, `CustomerOut` cũng sạch. `Channel` interface frontend (api.ts) đã bỏ 2 field.
- [~] Minor resurrect-on-create — CÓ TEST nhưng CHƯA SỬA LỆCH. `test_create_channel_resurrect_returns_200` giờ codify hành vi trả 200 trong khi route vẫn khai báo `status_code=201` → test đang khóa cái lệch OpenAPI thay vì sửa. Code vẫn lặp ở 2 chỗ (channels.py:23-37 và 49-64). Hành vi tái dùng id cũ (order lịch sử gắn ngầm sang kênh mới) giữ nguyên.

### Findings vòng 2 (verify lại, đều đã fix)
- [x] BLOCKER overload `is_active` — verify LIVE: PUT `is_active=false` → 200, GET sau đó → 200, kênh vẫn trong LIST, PUT reactivate → 200. Đường hồi sinh đã thông.
- [x] Minor frontend CANCELLATION_PENDING — có trong union `api.ts:61`, `getStatusBadgeClass` (orders/page.tsx:62) và banner chi tiết (:1105-1116).
- [x] Minor ALLOWED_TRANSITIONS — không nhánh nào target `CANCELLATION_PENDING` (orders.py:24-32) → không set tay được; có test `test_manual_transition_to_cancellation_pending_forbidden`.

### AC verify (live + test)
- AC1 — `DELETE /customers/1` khi order 1 ở `PENDING` → **409** `Cannot delete customer with 1 active orders`.
- AC2 — `DELETE /channels/1` cùng điều kiện → **409**.
- AC3 — `has_partial_failure` → `CANCELLATION_PENDING` + `logger.error` (orders.py:414-430); ngữ nghĩa "active" đã loại cả `CANCELLED` và `COMPLETED`.
- AC4 — soft delete xác nhận trong DB: row còn nguyên, `is_deleted=t`, `deleted_at` set.

### Test
`58 passed, 1 skipped`. **Cảnh báo môi trường:** container `oms_backend` đang phục vụ code CŨ (compose dùng `develop: watch`, không bind-mount). Lần chạy đầu ra `54 passed` với `test_channels.py` chỉ 3 test — số liệu vô hiệu. Phải `docker compose up -d --build oms_backend` mới đo đúng commit. Đây là cạm bẫy lặp lại qua nhiều vòng review.

### Test gap còn lại (không block)
- **Không có test nào assert 401 cho channel endpoints.** `conftest.py:68` override `get_current_user` toàn cục → đúng kiểu regression vòng 3 vẫn sẽ lọt CI lần nữa. Nên thêm 1 test dùng client không override.
- `test_migrations.py` vẫn chỉ `DROP COLUMN` cho `customers` (dòng 71,74), **chưa cover `channels`** → lặp lại pattern "pass giả" đã bị flag ở vòng 1. Test cũng skip mặc định vì thiếu `OMS_TEST_POSTGRES_URL` trong container/CI.
- Reviewer tự đóng gap này: chạy trên Postgres 15 thật (DB scratch) — `downgrade 0004` → insert row legacy → `upgrade head`: `is_deleted boolean NOT NULL DEFAULT false` + `deleted_at`, row cũ backfill về `false`, idempotent, downgrade sạch, không mất dữ liệu. Migration 0005 dùng `sa.false()` đúng, `alembic_version` ở head 0005, backend không crash-loop.

### Toolchain
- `ocr` v1.7.15 — preflight PASS. Lệnh literal `--from main --to 7f17d6b` trả `skipped: No supported files changed` vì `main == result_ref` (range rỗng) → chạy trên range thật. Bị **429 Too Many Requests** nặng từ backend LLM (siliconflow); lần chạy tốt nhất cho **1 comment non-blocking** (maintainability, hỏi xác nhận việc đổi sang `get_current_user` có chủ đích — đúng, đó chính là bản fix). Coverage một phần, đã bù bằng đọc tay + verify live.
- Baseline `/code-review`: `which claude` PASS; MCP `code-review-graph` không expose trong session này (scope control-tower) → thay bằng verify thủ công + gọi API live.

### Dọn dẹp
Probe rows (customer 13, channel 9) đã xóa, DB scratch đã DROP, order 1 khôi phục về `CANCELLED`, working tree target repo clean tại 7f17d6b.
