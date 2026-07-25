---
id: OMS-007
title: "Fix race conditions: order number, inventory allocation, OTP consumption"
status: todo
priority: high
risk: high
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: []
files:
  - OMS/backend/routers/orders.py
  - OMS/backend/services/inventory_service.py
flows: [order-create, checkout]
tests:
  - OMS/backend/test_main.py
dispatched: null
in_review: null
predicted_success: medium
prediction_factors:
  score: 0.65
  deductions:
    - "risk_high: -0.2 (concurrency)"
    - "complex_logic: -0.15"
created: 2026-07-25
updated: 2026-07-25
---

# OMS-007: Fix race conditions: order number, inventory allocation, OTP consumption

> Dự án: [[projects/topvnsport-oms/topvnsport-oms]]

## Tiêu chí nghiệm thu (AC)

- [ ] Order number generation sử dụng database sequence hoặc retry logic
- [ ] OTP token consumption có `with_for_update()` row locking
- [ ] Inventory allocation: reserve trong WMS trước khi confirm trong OMS
- [ ] Concurrent order creation test passes (10 parallel requests → 10 unique order numbers)

## Verification

```python
# Test concurrent order creation
import asyncio
results = await asyncio.gather(*[create_order() for _ in range(10)])
order_numbers = [r["order_number"] for r in results]
assert len(set(order_numbers)) == 10  # All unique
```

- OTP test: 2 concurrent requests với same token → chỉ 1 succeed

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] Implement database sequence cho order number generation
- [ ] Add `with_for_update()` cho OTP token query
- [ ] Refactor inventory allocation: reserve-first pattern
- [ ] Add concurrency tests

## Reference

- Debt file: `docs/TopVNSport - TODO & Technical Debt/oms/02_business_logic_bugs.md`
