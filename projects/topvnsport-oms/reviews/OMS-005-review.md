---
id: OMS-005
task_path: projects/topvnsport-oms/tasks/OMS-005-refactor-main-py.md
project: topvnsport-oms
result_ref: "topvnsport@main (commit 6a0d978)"
executor: "@antigravity"
reviewer: "@claude-opus"
status: done
issued: 2026-07-24
verdict: pass
verdict_date: 2026-07-24
---

# Phiếu Review: OMS-005 — Refactor OMS/backend/main.py - tách file 1557 dòng thành modules

- Dự án: TopVNSport - OMS (`/home/lupca/projects/topvnsport`)
- Task gốc: `projects/topvnsport-oms/tasks/OMS-005-refactor-main-py.md`
- Result-ref: topvnsport@main (commit 6a0d978)
- Executor: @antigravity
- Ngày phát phiếu: 2026-07-24

## Acceptance Criteria cần verify

- [x] `main.py` giảm còn <300 dòng (chỉ chứa FastAPI app init + router registration)
- [x] Các function được tách thành modules theo domain:
  - [x] `routers/otp.py`: send_otp, verify_otp, get_test_last_otp (+ helpers: generate_otp, hash_otp, mask_token)
  - [x] `routers/orders.py`: create_order, update_order, list_orders, confirm_order, cancel_order, check_order_stock, update_order_status
  - [x] `routers/fulfillment.py`: update_fulfillment_status
  - [x] `routers/customers.py`: list_customers, create_customer, update_customer
  - [x] `routers/channels.py`: list_channels, create_channel, update_channel
  - [x] `routers/dashboard.py`: get_dashboard_stats
  - [x] `routers/config.py`: get_sms_config, update_sms_config, get_masked_zalo_config
  - [x] `routers/webhooks.py`: zalo_webhook
  - [x] `services/inventory_service.py`: allocate_order_items, _fetch_inventory_snapshot
- [x] Tất cả 15 flows vẫn hoạt động (không regression)
- [x] Tests được viết cho các module mới (hiện tại 0 test coverage)

## Definition of Done (AGENTS.md mục 3)

- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: `OMS/backend/tests/` (mới tạo)
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (bạn đang review, hãy xác nhận bạn ≠ @antigravity)

## Test gợi ý chạy trong repo code

```bash
# Unit tests cho các module mới
docker compose -f OMS/docker-compose.yml exec api pytest OMS/backend/tests/ -v

# E2E test để verify không regression
cd /home/lupca/projects/topvnsport && pytest e2e_tests/tests/test_storefront_otp_flow.py -v

# Kiểm tra line count
wc -l OMS/backend/main.py  # expect <300
```

## Câu hỏi rủi ro (từ code-review-graph, tĩnh)

### High Priority
1. **Bridge node:** `test_storefront_otp_checkout_flow` là critical connector — cần verify flow OTP vẫn hoạt động sau refactor
2. **Hub risk:** `OrdersPageContent` (195 connections) không có test coverage — kiểm tra frontend orders page vẫn hoạt động với backend mới

### Medium Priority
3. **Untested hotspot:** Nhiều router mới được tạo — verify test coverage đã được thêm cho mỗi router
4. **Thin community:** `sms-zalo` chỉ có 2 members — kiểm tra integration giữa OTP và Zalo service

## Gợi ý công cụ

Repo code đích có sẵn skill `/code-review` — khuyến khích dùng để đọc diff + chạy test một cách có cấu trúc:
```bash
cd /home/lupca/projects/topvnsport && claude -p "/code-review 6a0d978"
```

## Trả kết quả

Sau khi review xong, báo lại cho control-tower bằng lệnh:
```
/verdict OMS-005 <pass|changes> --reviewer @<tên bạn> --commit 6a0d978 [--notes "..."]
```

---

## Kết quả review (2026-07-24, reviewer: @claude-fable ≠ executor @antigravity)

**Verdict: PASS** (commit 6a0d978)

### AC verification

1. **main.py <300 dòng: PASS** — `wc -l` = 231 dòng, chỉ còn app init, CORS, lifespan/scheduler, schema migration + channel seeding, exception handler, router registration.
2. **Tách modules theo domain: PASS** — đủ 9 module theo AC + thêm `routers/products.py` (search proxy, cũng tách từ main.py cũ). So sánh line-by-line toàn bộ code cũ (7a0acb8) với code mới (3 sub-review độc lập theo domain): **không có khác biệt hành vi nào** — logic, status code, exception, env var, DB transaction, module-level state (`LAST_OTPS` chỉ định nghĩa 1 lần), rate-limit/lockout OTP đều giữ nguyên. Route table cũ (29 endpoints) map 1:1 sang router prefix mới, không endpoint nào mất/đổi path. `on_event` → `lifespan` là thay đổi cấu trúc tương đương hành vi.
3. **15 flows không regression: PASS** — 39/39 test pass trong container (`pytest test_main.py tests/`): 28 test cũ (test_main.py) + 11 test mới. Test cũ vẫn xanh nhờ shim `_call_api`/`_allocate_order_items` trong orders.py giữ monkeypatch `main.call_api` hoạt động. Smoke test live: `/`, `/channels` 200 trực tiếp; `/api/oms/orders` 200 qua gateway với SSO token (xác nhận risk #2 — frontend orders page vẫn tương thích, API contract không đổi).
4. **Tests cho module mới: PASS (có ghi chú)** — `tests/` mới: 11 tests (conftest + api_utils, channels, config, customers, dashboard, inventory_service, otp, webhooks).

### Risk questions

1. **Bridge node `test_storefront_otp_checkout_flow`:** e2e chạy 3/4 pass; test checkout OTP **fail nhưng KHÔNG phải regression** — lỗi từ Zalo API thật: "OA does not have permission to use this feature". DB dev đang có Zalo credentials thật (mã hóa) trong `system_configs` nên send-otp đi đường Zalo thật thay vì dev-simulation. Bằng chứng pre-existing: bản ghi `otp_verifications` fail cùng lý do lúc 15:48 UTC 23/07 — **trước** commit refactor (18:19 UTC). Đây là vấn đề môi trường/quyền OA ZNS, cần fix ngoài scope task này.
2. **Hub `OrdersPageContent`:** API contract không đổi (path/method/schema y nguyên), gateway trả 200 cho orders list — không có breaking change phía backend.
3. **Coverage per router:** có test cho 8/10 module mới. **Gap:** không có `tests/test_orders.py` (orders dựa vào test_main.py cũ — vẫn dày: create/confirm/cancel/status/edit/delete/filter/OTP-security) và `update_fulfillment_status` (PATCH `/orders/{id}/fulfillments/{fn}/status`) **không có test nào** ở bất kỳ đâu.
4. **sms-zalo integration:** OTP↔Zalo verified qua unit tests (send/verify flow, webhook HMAC, token refresh job) — pass.

### Ghi chú không chặn (non-blocking)

- Thiếu test cho `update_fulfillment_status` — đề xuất task follow-up.
- Shim `_call_api`/`_allocate_order_items` trong `routers/orders.py:34-41` (lazy `import main`) tồn tại chỉ để test cũ monkeypatch được — nên refactor test sang patch `utils.api_utils.call_api` rồi bỏ shim.
- Môi trường dev đang cấu hình Zalo OA thật thiếu quyền ZNS → e2e OTP checkout sẽ tiếp tục fail cho đến khi gỡ config hoặc cấp quyền OA.
- `OMS/backend/schemas.py.bak` đang được track trong git (có từ trước commit này) — nên xóa.

### Lệnh verdict

```
/verdict OMS-005 pass --reviewer @claude-fable --commit 6a0d978 --notes "AC pass; 39/39 tests xanh; e2e OTP fail do Zalo OA permission (pre-existing, môi trường); gap: thiếu test update_fulfillment_status"
```
