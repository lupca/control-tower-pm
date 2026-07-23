---
id: OMS-005
title: "Refactor OMS/backend/main.py - tách file 1557 dòng thành modules"
status: done
priority: medium
risk: high
deadline: null
executor: "@antigravity"
reviewer: "@claude-fable"
result_ref: "topvnsport@main (commit 6a0d978)"
depends_on: []
files:
  - OMS/backend/main.py
flows:
  - verify_otp
  - send_otp
  - create_order
  - confirm_order
  - update_order
  - cancel_order
  - check_order_stock
  - update_fulfillment_status
  - get_dashboard_stats
  - create_customer
  - create_channel
  - zalo_webhook
  - update_sms_config
  - get_sms_config
  - get_test_last_otp
tests: []
dispatched: 2026-07-24
in_review: 2026-07-24
predicted_success: medium
prediction_factors:
  score: 0.4
  deductions:
    - "blast_radius: 94 files (-0.5)"
    - "no_existing_tests (-0.1)"
created: 2026-07-24
updated: 2026-07-24
---

# OMS-005: Refactor OMS/backend/main.py - tách file 1557 dòng thành modules

> Dự án: [[projects/topvnsport-oms/topvnsport-oms]]

## Tiêu chí nghiệm thu (AC)

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

## Verification

- `docker compose -f OMS/docker-compose.yml exec api pytest OMS/backend/tests/ -v` → 100% pass
- `wc -l OMS/backend/main.py` → <300 lines
- `curl -X POST http://localhost:8001/orders` → 200 OK (create_order flow)
- `curl http://localhost:8001/dashboard/stats` → 200 OK (dashboard flow)

## Plan

1. **Create router structure** — mkdir `OMS/backend/routers/` if not exists
2. **Extract OTP router** (`routers/otp.py`):
   - Move: `send_otp` (L1176-1328), `verify_otp` (L1331-1401), `get_test_last_otp` (L1168-1173)
   - Move helpers: `generate_otp`, `hash_otp`, `mask_token`
   - Import from `services/zalo_service.py` (already exists)
3. **Extract orders router** (`routers/orders.py`):
   - Move: `create_order` (L720-829), `list_orders` (L833-872), `update_order` (L882-948), `confirm_order` (L962-1019), `check_order_stock` (L1023-1042), `cancel_order` (L1045-1065), `update_order_status` (L1080-1106)
4. **Extract inventory service** (`services/inventory_service.py`):
   - Move: `allocate_order_items` (L378-452), `_fetch_inventory_snapshot` (L309-375)
   - Used by orders router
5. **Extract remaining routers**:
   - `routers/fulfillment.py`: `update_fulfillment_status`
   - `routers/customers.py`: `list_customers`, `create_customer`, `update_customer`
   - `routers/channels.py`: `list_channels`, `create_channel`, `update_channel`
   - `routers/dashboard.py`: `get_dashboard_stats`
   - `routers/config.py`: `get_sms_config`, `update_sms_config`, `get_masked_zalo_config`
   - `routers/webhooks.py`: `zalo_webhook`, `_extract_zalo_message_id`
6. **Extract shared utils** (`utils/api_utils.py`):
   - Move: `utcnow`, `call_api`, `validation_exception_handler`
7. **Update main.py** — keep only:
   - FastAPI app init
   - Middleware (CORS)
   - Lifespan events (startup/shutdown)
   - Router includes: `app.include_router(otp.router, prefix="/otp", tags=["OTP"])`
8. **Write tests** — create `tests/test_routers/` with unit tests for each extracted router
9. **Verify** — run `pytest` + manual e2e flow check

## Sub-tasks

- [x] Extract OTP functions → `routers/otp.py` (send_otp 153 lines, verify_otp 71 lines)
- [x] Extract order functions → `routers/orders.py` (create_order 110 lines, update_order 67 lines, confirm_order 58 lines)
- [x] Extract inventory logic → `services/inventory_service.py` (allocate_order_items 75 lines, _fetch_inventory_snapshot 67 lines)
- [x] Extract channel/customer/dashboard/config/webhook routers
- [x] Extract shared utilities → `utils/` (utcnow, call_api, validation_exception_handler)
- [x] Update main.py to only register routers
- [x] Write tests for extracted modules (knowledge gap - currently 0 coverage)
- [x] Run e2e test `test_storefront_otp_checkout_flow` để verify không regression

## Causal Analysis

- **Root cause:** Monolithic main.py (1557 lines) tích lũy dần khi features được thêm mà không có kiến trúc phân tách
- **Mechanism:** Tất cả endpoints, services, utilities nằm chung 1 file → coupling cao, khó maintain, không test isolation
- **Counterfactual:** Không refactor → mỗi feature mới tăng risk merge conflicts, làm testing khó hơn, giảm code discoverability
- **Pattern ID:** monolith-decomposition (preventive refactoring)

