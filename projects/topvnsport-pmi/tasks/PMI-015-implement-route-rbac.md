---
id: PMI-015
title: "Implement route-level RBAC authorization cho PMI"
status: todo
priority: urgent
risk: high
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: []
files:
  - PMI/backend/utils/dependency.py
  - PMI/backend/routers/products.py
  - PMI/backend/routers/categories.py
  - PMI/backend/routers/channels.py
  - PMI/backend/routers/attributes.py
flows: [product-create, product-update, category-manage]
tests:
  - PMI/backend/tests/test_auth.py
dispatched: null
in_review: null
predicted_success: medium
prediction_factors:
  score: 0.65
  deductions:
    - "risk_high: -0.2 (authorization logic)"
    - "blast_radius_large: -0.15 (touches many routers)"
created: 2026-07-25
updated: 2026-07-25
---

# PMI-015: Implement route-level RBAC authorization cho PMI

> Dự án: [[projects/topvnsport-pmi/topvnsport-pmi]]

## Tiêu chí nghiệm thu (AC)

- [ ] `require_permission(Permission.XXX)` dependency được tạo trong `utils/dependency.py`
- [ ] Mỗi mutation route (POST/PUT/DELETE) có permission check phù hợp
- [ ] Viewer role không thể delete product/category
- [ ] Admin role có full access
- [ ] Test cases cho permission denied scenarios

## Verification

- Login as viewer → DELETE /api/v1/products/1 → 403 Forbidden
- Login as admin → DELETE /api/v1/products/1 → 200 OK
- Login as product_manager → POST /api/v1/products → 200 OK
- `pytest PMI/backend/tests/test_auth.py -v` → pass

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] Create `PMI/backend/utils/permissions.py` với Permission enum + ROLE_PERMISSIONS mapping
- [ ] Add `require_permission()` dependency trong dependency.py
- [ ] Apply permission checks to products router
- [ ] Apply permission checks to categories router
- [ ] Apply permission checks to channels router
- [ ] Apply permission checks to attributes router
- [ ] Write test cases cho permission scenarios

## Reference

- Debt file: `docs/TopVNSport - TODO & Technical Debt/pmi/04_rbac_authorization.md`
