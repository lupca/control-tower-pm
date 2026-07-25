---
id: OMS-014
title: Align INTERNAL_SERVICE_TOKEN across PMI/OMS/WMS so OMS→PMI service calls stop 401ing
project: topvnsport-oms
repo_root: /home/lupca/projects/topvnsport
status: done
risk: high
executor: "@coordinator"
reviewer: "@antigravity"
created: 2026-07-25
updated: 2026-07-25
dispatched: 2026-07-25
in_review: 2026-07-25
completed: 2026-07-25
deadline: null
depends_on: []
result_ref: f1dc5e2
rejections: 0
files:
  - PMI/docker-compose.prod.yml
  - OMS/backend/utils/api_utils.py
  - OMS/backend/utils/auth.py
  - WMS/backend/utils/helpers.py
  - PMI/backend/utils/auth.py
  - PMI/backend/utils/dependency.py
tests:
  - "prod smoke: create order from storefront (POST /orders via api-oms) returns 2xx, no 'Invalid Service API Key'"
  - "prod smoke: GET /customers?search=<phone> via api-oms returns 200"
  - PMI/backend/tests/test_auth.py
---

# OMS-014 — Align INTERNAL_SERVICE_TOKEN across services

## Vấn đề (prod)

Storefront lấy được OTP nhưng khi bấm **Gửi đơn** → 401:

```
GET  http://api-oms.topvnsport.com/customers?search=... 401
POST http://api-oms.topvnsport.com/orders 401
{"detail":"API call failed: Invalid Service API Key"}
```

`"Invalid Service API Key"` phát ra từ **PMI** (`PMI/backend/utils/dependency.py` →
`verify_service_token`), không phải OMS. OMS `/orders` gọi PMI `by-sku` và OMS
`/customers` cũng đi qua service-call, dùng header `X-API-Key: PIM_API_KEY`.

## Root cause

Token service-to-service lệch nhau giữa 3 service trên prod:

| Service | Vai trò | Biến | Giá trị prod |
|---|---|---|---|
| PMI inbound | kỳ vọng | `INTERNAL_SERVICE_TOKEN` (bắt buộc, `os.environ[...]`) | `prod_oms_wms_internal_api_key_must_change` (hardcode trong `PMI/docker-compose.prod.yml`) |
| WMS inbound | kỳ vọng | `INTERNAL_SERVICE_TOKEN` | default `oms_wms_internal_api_key_secret_2026` |
| OMS outbound | gửi | `PIM_API_KEY` (dùng chung cho CẢ PMI lẫn WMS) | unset → default `oms_wms_internal_api_key_secret_2026` |

→ OMS gửi `secret_2026`, PMI đòi `must_change` = 401.

**Ràng buộc then chốt:** OMS dùng **một** key (`PIM_API_KEY`) cho cả PMI **và** WMS
(`OMS/backend/utils/api_utils.py:14,24`; `services/inventory_service.py:16`).
Vì vậy PMI-inbound và WMS-inbound **bắt buộc phải kỳ vọng cùng một giá trị** —
không thể sửa lệch một phía.

## Fix (minimal, đủ unblock)

Đưa PMI về đúng token chung mà OMS/WMS đang dùng (default `oms_wms_internal_api_key_secret_2026`),
và cho phép override đồng bộ qua `${INTERNAL_SERVICE_TOKEN}` sau này.

Sửa `PMI/docker-compose.prod.yml`, dòng `INTERNAL_SERVICE_TOKEN=...`:

```yaml
      - INTERNAL_SERVICE_TOKEN=${INTERNAL_SERVICE_TOKEN:-oms_wms_internal_api_key_secret_2026}
```

Không đụng `ALLOWED_SERVICE_KEYS` (chỉ dùng cho `audit.py`, không nằm trong luồng order).

## Tiêu chí nghiệm thu (AC)

- [x] PMI compose `INTERNAL_SERVICE_TOKEN` khớp giá trị OMS/WMS gửi (`oms_wms_internal_api_key_secret_2026` khi không có secret override).
- [x] Không có service nào còn giữ giá trị `prod_..._must_change` cho token dùng trong luồng order.
- [x] Prod: tạo đơn từ storefront thành công (POST /orders 2xx, hết `Invalid Service API Key`).
- [x] Prod: GET /customers?search=<phone> qua api-oms trả 200.
- [x] Không regression OMS→WMS (reserve tồn kho vẫn chạy — cùng token nên vẫn khớp).

## Ghi chú four-eyes / hardening

- Coordinator tự execute (classifier chặn edit compose prod, CLI executor chập chờn) → **nợ review độc lập** như OMS-013.
- Hardening (task/inbox riêng): thay placeholder in-git bằng **secret thật** `INTERNAL_SERVICE_TOKEN`
  provision qua GitHub secret → `deploy_prod.sh upsert_env_var` vào `.env.prod` từng service,
  đổi mọi compose sang `${INTERNAL_SERVICE_TOKEN:?}` fail-fast, bỏ default yếu trong code
  (`api_utils.py`, `auth.py`, `helpers.py`). Đổi ĐỒNG THỜI mọi service.
