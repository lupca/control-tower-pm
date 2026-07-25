---
id: WEB-008
title: "Cart reliability: localStorage persistence + quantity update + nanoid"
status: todo
priority: high
risk: normal
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: []
files:
  - web/src/features/cart/cartSlice.ts
flows: [cart, checkout]
tests:
  - web/src/tests/
dispatched: null
in_review: null
predicted_success: high
prediction_factors:
  score: 0.85
  deductions:
    - "state_management: -0.15"
created: 2026-07-25
updated: 2026-07-25
---

# WEB-008: Cart reliability: localStorage persistence + quantity update + nanoid

> Dự án: [[projects/topvnsport-web/topvnsport-web]]

## Tiêu chí nghiệm thu (AC)

- [ ] Cart items persist qua page refresh (localStorage)
- [ ] `updateCartItemQuantity` reducer được implement
- [ ] Cart item IDs sử dụng nanoid thay vì Date.now()
- [ ] Clear cart on successful checkout

## Verification

1. Add items to cart → refresh page → items vẫn còn
2. Update quantity → verify state update đúng
3. Rapid clicks add to cart → no duplicate IDs

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] Add localStorage load/save helpers
- [ ] Load cart từ localStorage trong initialState
- [ ] Save cart sau mỗi mutation
- [ ] Add updateCartItemQuantity reducer
- [ ] Replace Date.now() với nanoid()
- [ ] Clear localStorage on checkout success

## Reference

- Debt file: `docs/TopVNSport - TODO & Technical Debt/web/01_security_and_state.md`
