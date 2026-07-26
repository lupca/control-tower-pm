---
id: WMS-004
title: "Fix race conditions: receive scan, pick scan + row locking"
status: completed
priority: high
risk: high
deadline: null
executor: "@antigravity-3.6-high"
reviewer: null
result_ref: 570cb7c216c0566766c6878c05b11ce3c43922d9
depends_on: []
files:
  - WMS/backend/routers/inbound.py
  - WMS/backend/routers/fulfillment.py
flows: [receive, pick]
tests:
  - WMS/backend/tests/
dispatched: 2026-07-26
in_review: null
predicted_success: medium
prediction_factors:
  score: 0.65
  deductions:
    - "risk_high: -0.2 (concurrency)"
    - "complex_logic: -0.15"
created: 2026-07-25
updated: 2026-07-26
---

# WMS-004: Fix race conditions: receive scan, pick scan + row locking

> Dự án: [[projects/topvnsport-wms/topvnsport-wms]]

## Tiêu chí nghiệm thu (AC)

- [x] Receive scan có `with_for_update()` khi update `received_qty`
- [x] Pick scan có `with_for_update()` khi update `picked_qty`
- [x] Concurrent receive test: 10 operators scan cùng barcode → total = 10
- [x] Concurrent pick test: 10 pickers cùng order → correct total

## Verification

```python
# Test concurrent receive
results = await asyncio.gather(*[receive_scan(qty=1) for _ in range(10)])
shipment = get_shipment(1)
assert shipment.items[0].received_qty == 10  # Not less due to race
```

## Plan

1. **`WMS/backend/routers/inbound.py`**:
   - In `receive_scan_inbound_shipment`: Add `.with_for_update()` to the query for `models.InboundItem`.
   - Call `db.flush()` immediately after updating `received_qty` to persist the change within the transaction before returning.
2. **`WMS/backend/routers/fulfillment.py`**:
   - In `scan_pick_fulfillment_order`: Add `.with_for_update()` to the query for `models.PickListItem`.
   - Call `db.flush()` immediately after updating `picked_qty` to persist the lock and value.

## Sub-tasks

- [x] Add `with_for_update()` trong receive scan query
- [x] Add `with_for_update()` trong pick scan query
- [x] Add `db.flush()` sau update để persist ngay
- [x] Add concurrency tests

## Reference

- Debt file: `docs/TopVNSport - TODO & Technical Debt/wms/01_race_conditions.md`
