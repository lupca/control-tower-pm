---
id: WMS-002
title: "Fix 414 Request-URI Too Large when fetching stock for many SKUs"
status: done
priority: urgent
risk: high
deadline: null
executor: "@antigravity"
reviewer: "@claude"
result_ref: "7fd6e663d2fc"
depends_on: []
files:
  - WMS/backend/routers/inventory.py
  - web/src/services/sport-api/index.ts
flows:
  - getStringOptions
  - adjust_inventory
  - transfer_inventory
tests:
  - web/src/__tests__/m2_1_forensic.test.ts
  - web/src/tests/wmsStockIntegration.test.ts
  - web/src/tests/challenger_m2_2_empirical.test.ts
dispatched: 2026-07-22
in_review: 2026-07-22
created: 2026-07-22
updated: 2026-07-22
---

# WMS-002: Fix 414 Request-URI Too Large when fetching stock for many SKUs

> Dự án: [[projects/topvnsport-wms/topvnsport-wms]]

## Bối cảnh (Context)

Trên production, khi vào trang sản phẩm (`topvnsport.com/product/...`), frontend gọi API `GET /public/stock?sku_codes=...` với hàng trăm SKU codes trong query string. Khi số lượng SKU lớn (>200), URL vượt quá giới hạn HTTP (~8KB) và server trả về lỗi **414 Request-URI Too Large**.

**Error trace:**
```
GET http://api-wms.topvnsport.com/public/stock?sku_codes=AO7MA-ULTIMATE-GRAY-M%2C...
net::ERR_FAILED 414 (Request-URI Too Large)
```

**Root cause:** API `/public/stock` chỉ hỗ trợ GET với query params. Khi frontend cần fetch stock cho nhiều SKU (ví dụ: trang hiển thị related products, cross-sell), URL trở nên quá dài.

**Blast radius:** HIGH — 500 impacted nodes, 133 files, 7 flows affected (từ code-review-graph).

## Tiêu chí nghiệm thu (AC)

- [x] WMS backend có endpoint mới hoặc endpoint cũ hỗ trợ **POST** method cho `/public/stock` với body JSON `{"sku_codes": ["SKU1", "SKU2", ...]}`
- [x] Frontend (`fetchWmsStock`) sử dụng POST thay vì GET khi gọi WMS stock API
- [x] Backward compatibility: GET vẫn hoạt động cho số lượng SKU nhỏ (<50) để không break các caller khác (nếu có)
- [x] **Test coverage đầy đủ (automated, không manual):**
  - [x] Backend: test POST `/public/stock` với payload JSON (happy path + edge cases: empty array, large array >200 SKUs)
  - [x] Backend: test GET `/public/stock` vẫn hoạt động (backward compat)
  - [x] Frontend: cập nhật `web/src/__tests__/m2_1_forensic.test.ts` — test "Check 3: sportApi.getProducts" đổi từ kiểm tra GET sang POST
  - [x] Frontend: cập nhật `web/src/tests/wmsStockIntegration.test.ts` — test `fetchWmsStock` reflect POST behavior
  - [x] Frontend: cập nhật `web/src/tests/challenger_m2_2_empirical.test.ts` nếu mock stock API cần đổi method
- [x] Tất cả test suite liên quan pass 100% (`pytest` cho backend, `npm test` cho frontend)

## Plan

### 1. Backend — `WMS/backend/routers/inventory.py`

**Thêm POST endpoint** (giữ nguyên GET cho backward compat):

```python
# Thêm schema cho POST body (có thể inline hoặc trong schemas.py)
class PublicStockRequest(schemas.BaseModel):
    sku_codes: List[str]

@public_router.post("/public/stock", response_model=schemas.PublicStockResponse)
def get_public_stock_post(
    payload: PublicStockRequest,
    db: Session = Depends(get_db)
):
    # Reuse logic từ GET handler — extract thành helper function
    return _get_stock_by_skus(payload.sku_codes, db)
```

**Refactor**: Extract logic chung (line 18-77) thành `_get_stock_by_skus(sku_codes: List[str], db)` để cả GET và POST đều gọi.

### 2. Frontend — `web/src/services/sport-api/index.ts`

**Sửa `fetchWmsStock()` (line 8-42)**:

```typescript
async function fetchWmsStock(skuCodes: string[]): Promise<Record<string, number>> {
  const uniqueSkus = Array.from(new Set(skuCodes.filter((sku) => Boolean(sku && sku.trim()))));
  if (uniqueSkus.length === 0) {
    return {};
  }

  try {
    const url = `${WMS_API_URL}/public/stock`;
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sku_codes: uniqueSkus }),
    });
    // ... rest giữ nguyên
  }
}
```

### 3. Backend Tests — Tạo mới `WMS/backend/tests/test_public_stock.py`

- Test POST với payload hợp lệ (1 SKU, nhiều SKU)
- Test POST với empty array → trả về empty
- Test POST với >200 SKUs → vẫn hoạt động (không 414)
- Test GET vẫn hoạt động (backward compat)

### 4. Frontend Tests — Cập nhật 3 file

| File | Thay đổi |
|:---|:---|
| `m2_1_forensic.test.ts:27` | Đổi assertion `toHaveBeenCalledWith` từ URL GET sang expect POST method |
| `wmsStockIntegration.test.ts:32` | Mock `fetch` expect POST + JSON body thay vì GET |
| `challenger_m2_2_empirical.test.ts` | Review mock, đổi nếu cần |

### 5. Verify

```bash
# Backend
cd WMS && docker compose exec api pytest tests/test_public_stock.py -v

# Frontend  
cd web && npm test -- --testPathPattern="(m2_1_forensic|wmsStockIntegration|challenger_m2_2)" --watchAll=false

# Full suite
cd WMS && docker compose exec api pytest
cd web && npm test -- --watchAll=false
```

## Sub-tasks

- [x] (WMS backend) Thêm route handler POST cho `/public/stock` trong `inventory.py`
- [x] (WMS backend) Viết test backend cho POST endpoint (happy path + edge cases)
- [x] (Web frontend) Sửa `fetchWmsStock()` trong `sport-api/index.ts` để dùng POST + JSON body
- [x] (Test) Cập nhật `m2_1_forensic.test.ts` — đổi assertion từ GET sang POST
- [x] (Test) Cập nhật `wmsStockIntegration.test.ts` — mock/expect POST thay vì GET
- [x] (Test) Cập nhật `challenger_m2_2_empirical.test.ts` nếu cần đổi mock method
- [x] (Verify) Chạy full test suite: `pytest` (backend) + `npm test` (frontend) — 100% green

## Notes

- **Test files cần update:** 3 file test frontend đã có sẵn cần sửa để reflect POST behavior (xem AC).
- **Test gap backend:** `WMS/backend/routers/inventory.py` chưa có test riêng — cần viết test mới cho POST endpoint.
- Không cần migration DB — chỉ thay đổi API contract.
