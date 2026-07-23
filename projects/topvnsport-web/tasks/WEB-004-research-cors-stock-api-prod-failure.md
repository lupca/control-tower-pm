---
id: WEB-004
title: "Research: CORS block + stock API vẫn fail trên production"
status: done
type: research
priority: urgent
risk: normal
created: 2026-07-23
updated: 2026-07-23
deadline: 2026-07-24
dispatched: 2026-07-23
executor: "@antigravity-3.1-pro"
reviewer: "@lupca"
depends_on: []
files:
  - web/src/services/sport-api/index.ts
  - WMS/backend/routers/inventory.py
  - docker-compose.yml
  - docker-compose.prod.yml
flows:
  - getStringOptions
  - get_public_stock
  - post_public_stock
tests:
  - web/src/__tests__/m2_1_forensic.test.ts
  - web/src/tests/wmsStockIntegration.test.ts
  - web/src/tests/challenger_m2_2_empirical.test.ts
predicted_success: medium
prediction_factors:
  score: 0.5
  deductions:
    - "blast_radius: 107 files (>15) → -0.5"
  notes: "Research task — blast radius lớn do code area rộng, nhưng triệu chứng CORS rõ ràng, khả năng xác định root cause cao"
confidence_interval: [0.3, 0.7]
---

# WEB-004: Research — CORS block + stock API vẫn fail trên production

> Dự án: [[projects/topvnsport-web/topvnsport-web]]

## Bối cảnh (Context)

Trên production (`topvnsport.com`), frontend gọi `http://api-wms.topvnsport.com/public/stock?sku_codes=...` bị **CORS block** — browser console hiện:

```
Access to fetch at 'http://api-wms.topvnsport.com/public/stock?sku_codes=SP-63627C80-...'
been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the request
```

```
Failed to fetch stock from WMS chunk: TypeError: Failed to fetch
```

**Liên quan task trước:** WMS-002 (Fix 414 Request-URI Too Large) đã done — chuyển `fetchWmsStock` từ GET → POST. Tuy nhiên screenshot prod **vẫn thấy GET requests**.

**IP prod EC2:** `52.203.250.214`

## Tiêu chí nghiệm thu (AC)

- [x] Xác định nginx config trên prod EC2 `52.203.250.214` có CORS headers cho `api-wms.topvnsport.com` không
- [x] Xác nhận WMS container trên prod đang chạy code nào (có commit `7fd6e663d2fc` từ WMS-002 không)
- [x] Xác nhận frontend build trên prod có bao gồm POST change hay vẫn dùng GET
- [x] Root cause documented
- [x] Fix proposal với steps cụ thể

## Root Cause (đã xác minh)

**Nguyên nhân thật: CD pipeline lỗi → `web_frontend` container trên prod chưa được rebuild.**

- Code WMS-002 (GET→POST) đã merge vào repo (`7fd6e663d2fc`) nhưng **CD không chạy thành công** → container `web_frontend` trên prod vẫn dùng JS bundle cũ với GET request.
- Frontend gọi GET với URL dài (hàng trăm SKU codes) → server trả **414 Request-URI Too Large** → response 414 không kèm CORS headers → browser báo "CORS block" (triệu chứng giả, lỗi thật là 414).
- WMS backend (`wms-api`) đã có POST endpoint — không lỗi phía backend.
- CORS config (`CORS_ALLOWED_ORIGINS`) đã có `http://topvnsport.com` — hệ thống dùng HTTP, không cần thêm `https://`.

**Executor đã hotfix trực tiếp trên prod** (rebuild `web_frontend` container), prod đã hết lỗi. Tuy nhiên đây là fix tạm — cần sửa CD pipeline để lần deploy sau không lặp lại.

### Executor report sai ở đâu

Executor (@antigravity-3.1-pro) báo primary root cause là "thiếu `https://` origins trong CORS config" — **không chính xác** vì hệ thống dùng HTTP, `http://topvnsport.com` đã nằm trong allowed origins. Triệu chứng CORS chỉ là hệ quả của lỗi 414 (error response không kèm CORS headers).

## Bài học

- "CORS error" trong browser không phải lúc nào cũng là lỗi CORS thật — bất kỳ response nào thiếu `Access-Control-Allow-Origin` header (kể cả 414, 500, network error) đều bị browser báo là CORS violation.
- CD pipeline cần monitoring — code merge xong mà CD fail thì prod không được update.
