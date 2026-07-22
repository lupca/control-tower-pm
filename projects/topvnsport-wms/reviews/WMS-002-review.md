---
id: WMS-002
task_path: projects/topvnsport-wms/tasks/WMS-002.md
project: topvnsport-wms
result_ref: feature/WMS-002-fix-414-stock-api
executor: @antigravity
reviewer: null
status: pending
issued: 2026-07-22
verdict: null
verdict_date: null
---

# Phiếu Review: WMS-002 — Fix 414 Request-URI Too Large when fetching stock for many SKUs

- Dự án: topvnsport-wms (`/home/lupca/projects/topvnsport`)
- Task gốc: `projects/topvnsport-wms/tasks/WMS-002-fix-414-stock-api-uri-too-large.md`
- Result-ref: `feature/WMS-002-fix-414-stock-api`
- Executor: @antigravity
- Ngày phát phiếu: 2026-07-22

---

## Acceptance Criteria cần verify

- [ ] WMS backend có endpoint mới hoặc endpoint cũ hỗ trợ **POST** method cho `/public/stock` với body JSON `{"sku_codes": ["SKU1", "SKU2", ...]}`
- [ ] Frontend (`fetchWmsStock`) sử dụng POST thay vì GET khi gọi WMS stock API
- [ ] Backward compatibility: GET vẫn hoạt động cho số lượng SKU nhỏ (<50) để không break các caller khác (nếu có)
- [ ] **Test coverage đầy đủ (automated, không manual):**
  - [ ] Backend: test POST `/public/stock` với payload JSON (happy path + edge cases: empty array, large array >200 SKUs)
  - [ ] Backend: test GET `/public/stock` vẫn hoạt động (backward compat)
  - [ ] Frontend: cập nhật `web/src/__tests__/m2_1_forensic.test.ts` — test "Check 3: sportApi.getProducts" đổi từ kiểm tra GET sang POST
  - [ ] Frontend: cập nhật `web/src/tests/wmsStockIntegration.test.ts` — test `fetchWmsStock` reflect POST behavior
  - [ ] Frontend: cập nhật `web/src/tests/challenger_m2_2_empirical.test.ts` nếu mock stock API cần đổi method
- [ ] Tất cả test suite liên quan pass 100% (`pytest` cho backend, `npm test` cho frontend)

---

## Definition of Done (AGENTS.md mục 3)

- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%:
  - `web/src/__tests__/m2_1_forensic.test.ts`
  - `web/src/tests/wmsStockIntegration.test.ts`
  - `web/src/tests/challenger_m2_2_empirical.test.ts`
  - `WMS/backend/tests/test_public_stock.py` (mới tạo)
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (bạn đang review, hãy xác nhận bạn ≠ @antigravity)

---

## Test gợi ý chạy trong repo code

```bash
# Backend — WMS
cd /home/lupca/projects/topvnsport
docker compose -f WMS/docker-compose.yml exec api pytest tests/test_public_stock.py -v
docker compose -f WMS/docker-compose.yml exec api pytest  # full suite

# Frontend — web
cd /home/lupca/projects/topvnsport/web
npm test -- --testPathPattern="(m2_1_forensic|wmsStockIntegration|challenger_m2_2)" --watchAll=false
npm test -- --watchAll=false  # full suite
```

---

## Câu hỏi rủi ro (từ code-review-graph, tĩnh — không thay thế việc bạn tự đọc diff)

**Liên quan trực tiếp đến task này:**
- Files thay đổi: `WMS/backend/routers/inventory.py`, `web/src/services/sport-api/index.ts`
- Flows ảnh hưởng: `getStringOptions`, `adjust_inventory`, `transfer_inventory`
- Risk: HIGH (500 impacted nodes, 133 files)

**Câu hỏi chung từ graph (priority high):**
1. Hub node `upgrade` (migration) có 204 connections nhưng không có test coverage — không liên quan trực tiếp đến task này.
2. `ProductList` (PMI) là bridge node quan trọng — không liên quan trực tiếp đến task này.

---

## Gợi ý công cụ

Repo code đích có thể có sẵn skill `/code-review` (hoặc tương đương) — khuyến khích dùng để đọc diff + chạy test một cách có cấu trúc.

---

## Trả kết quả

Sau khi review xong, báo lại cho control-tower bằng lệnh:

```
/verdict WMS-002 pass --reviewer @<tên bạn> --commit <hash>
```

hoặc nếu cần sửa:

```
/verdict WMS-002 changes --reviewer @<tên bạn> --notes "..."
```
