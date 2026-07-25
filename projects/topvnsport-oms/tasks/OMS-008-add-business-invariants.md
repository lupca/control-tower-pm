---
id: OMS-008
title: "Add business invariants: block deletion với active orders, partial cancel handling"
status: todo
priority: high
risk: normal
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: []
files:
  - OMS/backend/routers/customers.py
  - OMS/backend/routers/channels.py
  - OMS/backend/routers/orders.py
flows: [customer-delete, order-cancel]
tests:
  - OMS/backend/test_main.py
dispatched: null
in_review: null
predicted_success: high
prediction_factors:
  score: 0.8
  deductions:
    - "business_logic: -0.2"
created: 2026-07-25
updated: 2026-07-25
---

# OMS-008: Add business invariants: block deletion với active orders, partial cancel handling

> Dự án: [[projects/topvnsport-oms/topvnsport-oms]]

## Tiêu chí nghiệm thu (AC)

- [ ] Delete customer với active orders → 409 Conflict
- [ ] Delete channel với active orders → 409 Conflict
- [ ] Partial WMS cancellation → CANCELLATION_PENDING status + error log
- [ ] Soft delete thay vì hard delete cho customers

## Verification

- Create customer → create order → delete customer → 409
- Cancel order với 2 fulfillments, 1 fails → status = CANCELLATION_PENDING
- Customer bị delete → `is_deleted=True`, không xóa khỏi DB

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] Add active orders check trước khi delete customer
- [ ] Add active orders check trước khi delete channel
- [ ] Implement partial cancellation handling với error collection
- [ ] Add soft delete columns (is_deleted, deleted_at) cho Customer model
- [ ] Add tests cho business invariants

## Reference

- Debt file: `docs/TopVNSport - TODO & Technical Debt/oms/02_business_logic_bugs.md`
