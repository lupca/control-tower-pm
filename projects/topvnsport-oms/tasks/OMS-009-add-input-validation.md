---
id: OMS-009
title: "Add input validation (schema constraints)"
status: todo
priority: high
risk: normal
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: []
files:
  - OMS/backend/schemas/order.py
  - OMS/backend/schemas/common.py
flows: [order-create]
tests:
  - OMS/backend/test_main.py
dispatched: null
in_review: null
predicted_success: high
prediction_factors:
  score: 0.85
  deductions:
    - "schema_change: -0.15"
created: 2026-07-25
updated: 2026-07-25
---

# OMS-009: Add input validation (schema constraints)

> Dự án: [[projects/topvnsport-oms/topvnsport-oms]]

## Tiêu chí nghiệm thu (AC)

- [ ] `quantity` field có constraint `ge=1, le=9999`
- [ ] `shipping_fee` có constraint `ge=0`
- [ ] `phone` có regex validation cho VN format
- [ ] `items` list có `min_items=1`
- [ ] Invalid input trả về 422 với field-level errors

## Verification

```bash
# Test invalid quantity
curl -X POST /api/orders -d '{"items": [{"quantity": 0}]}'
# → 422: quantity must be >= 1

# Test invalid phone
curl -X POST /api/orders -d '{"customer_phone": "invalid"}'
# → 422: phone format invalid
```

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] Add Field constraints cho OrderItemInput
- [ ] Add phone regex validator
- [ ] Add shipping_fee constraint
- [ ] Add items list min_items constraint
- [ ] Add validation tests

## Reference

- Debt file: `docs/TopVNSport - TODO & Technical Debt/oms/02_business_logic_bugs.md`
