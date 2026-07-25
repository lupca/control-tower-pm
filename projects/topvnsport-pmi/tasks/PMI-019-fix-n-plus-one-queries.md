---
id: PMI-019
title: "Fix N+1 queries + transaction boundaries"
status: todo
priority: medium
risk: normal
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: []
files:
  - PMI/backend/routers/products.py
  - PMI/backend/services/product_service.py
flows: [product-list]
tests:
  - PMI/backend/tests/test_products.py
dispatched: null
in_review: null
predicted_success: high
prediction_factors:
  score: 0.85
  deductions:
    - "performance_change: -0.15"
created: 2026-07-25
updated: 2026-07-25
---

# PMI-019: Fix N+1 queries + transaction boundaries

> Dự án: [[projects/topvnsport-pmi/topvnsport-pmi]]

## Tiêu chí nghiệm thu (AC)

- [ ] Product list query sử dụng eager loading (joinedload/selectinload)
- [ ] Không còn N+1 query patterns khi list products với variants
- [ ] Transaction boundaries rõ ràng cho write operations
- [ ] Query count giảm đáng kể (đo bằng SQL logging)

## Verification

- Enable SQL logging → list 100 products → đếm số queries
- Before: ~101 queries (1 + N), After: ~2-3 queries
- `pytest PMI/backend/tests/test_products.py -v` → pass

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] Audit current queries với SQL logging
- [ ] Add joinedload cho product-variant relationship
- [ ] Add selectinload cho product-category relationship
- [ ] Wrap write operations trong explicit transactions
- [ ] Add query count assertions trong tests

## Reference

- Debt file: `docs/TopVNSport - TODO & Technical Debt/pmi/08_performance_n1_queries.md`
