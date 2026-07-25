---
id: WMS-004
title: "Fix race conditions: receive scan, pick scan + row locking"
status: todo
priority: high
risk: high
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: []
files:
  - WMS/backend/routers/inbound.py
  - WMS/backend/routers/fulfillment.py
flows: [receive, pick]
tests:
  - WMS/backend/tests/
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

# WMS-004: Fix race conditions: receive scan, pick scan + row locking

> Dự án: [[projects/topvnsport-wms/topvnsport-wms]]

## Tiêu chí nghiệm thu (AC)

- [ ] Receive scan có `with_for_update()` khi update `received_qty`
- [ ] Pick scan có `with_for_update()` khi update `picked_qty`
- [ ] Concurrent receive test: 10 operators scan cùng barcode → total = 10
- [ ] Concurrent pick test: 10 pickers cùng order → correct total

## Verification

```python
# Test concurrent receive
results = await asyncio.gather(*[receive_scan(qty=1) for _ in range(10)])
shipment = get_shipment(1)
assert shipment.items[0].received_qty == 10  # Not less due to race
```

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] Add `with_for_update()` trong receive scan query
- [ ] Add `with_for_update()` trong pick scan query
- [ ] Add `db.flush()` sau update để persist ngay
- [ ] Add concurrency tests

## Reference

- Debt file: `docs/TopVNSport - TODO & Technical Debt/wms/01_race_conditions.md`
