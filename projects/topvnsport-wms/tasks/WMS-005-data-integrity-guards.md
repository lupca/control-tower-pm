---
id: WMS-005
title: "Data integrity: over-pick/receive guards, ship status validation, OMS notification outbox"
status: todo
priority: high
risk: high
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: [WMS-004]
files:
  - WMS/backend/routers/fulfillment.py
  - WMS/backend/routers/inbound.py
  - WMS/backend/models.py
flows: [receive, pick, ship]
tests:
  - WMS/backend/tests/
dispatched: null
in_review: null
predicted_success: medium
prediction_factors:
  score: 0.6
  deductions:
    - "risk_high: -0.2"
    - "complex_logic: -0.2"
created: 2026-07-25
updated: 2026-07-25
---

# WMS-005: Data integrity: over-pick/receive guards, ship status validation, OMS notification outbox

> Dự án: [[projects/topvnsport-wms/topvnsport-wms]]

## Tiêu chí nghiệm thu (AC)

- [ ] Over-picking blocked: `picked_qty + scan_qty > quantity` → 400 error
- [ ] Over-receiving: log discrepancy hoặc block
- [ ] Ship chỉ từ PACKED status, không từ PENDING/PICKING
- [ ] Fix wrong OMS notification: PICKED → "PICKED" (không phải "PICKING")
- [ ] Complete pick không force quantities nếu chưa scan đủ
- [ ] Outbox pattern cho OMS notifications (atomic với WMS state)

## Verification

- Pick scan vượt quantity → 400 "Cannot pick X. Max remaining: Y"
- Ship từ PICKING status → 400 "Must be PACKED"
- Complete pick với items chưa đủ → 400 hoặc require force flag

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] Add over-pick validation
- [ ] Add over-receive validation/logging
- [ ] Add ship status check (only from PACKED)
- [ ] Fix OMS notification status string
- [ ] Remove auto-force in complete_pick
- [ ] Implement StatusNotification outbox model
- [ ] Add background worker cho outbox processing

## Reference

- Debt file: `docs/TopVNSport - TODO & Technical Debt/wms/01_race_conditions.md`
