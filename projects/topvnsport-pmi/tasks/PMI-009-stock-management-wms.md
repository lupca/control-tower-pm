---
id: PMI-009
title: "Di chuyển Stock Management từ PMI sang WMS"
status: done
priority: high
risk: high
deadline: 2026-07-21
executor: null
reviewer: null
result_ref: "commit d14f956"
depends_on: []
files:
  - WMS/backend/api/public.py
  - PMI/web/src/utils/
  - PMI/backend/models.py
  - PMI/backend/alembic/
flows: [product-listing, inventory-lookup, export-csv]
tests: []
dispatched: null
in_review: null
created: 2026-07-21
updated: 2026-07-21
---

# PMI-009: Di chuyển Stock Management từ PMI sang WMS

> Dự án: [[projects/topvnsport-pmi/topvnsport-pmi]]

> Task này được reconcile từ git history — đã implement trước khi control-tower tracking. `⚠️ high-risk` — chạm `models.py` + migration.

## Tiêu chí nghiệm thu (AC)
- [x] WMS có GET /public/stock endpoint cho real-time inventory
- [x] PMI Frontend fetch stock từ WMS và merge vào product data
- [x] Xóa stock column khỏi product_variants (PMI)
- [x] Xóa stock field khỏi tất cả APIs, forms, exports (PMI)

## Ghi chú
- Test: WMS 25 tests (4 new public stock), PMI Backend 121, PMI Frontend 122, E2E 18 (7 new stock flow)
- Migration: `c9a2d4b80123_remove_stock_column.py`

## Plan
*(đã implement trước khi control-tower tracking — không có kế hoạch ghi lại)*

## Sub-tasks
- [x] WMS có GET /public/stock endpoint cho real-time inventory
- [x] PMI Frontend fetch stock từ WMS và merge vào product data
- [x] Xóa stock column khỏi product_variants (PMI)
- [x] Xóa stock field khỏi tất cả APIs, forms, exports (PMI)
