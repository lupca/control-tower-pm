---
id: WEB-009
title: "App state: error handling + OTP token sessionStorage + checkout validation"
status: todo
priority: medium
risk: normal
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: []
files:
  - web/src/features/appData/appDataSlice.ts
  - web/src/components/CartModal.tsx
  - web/src/App.tsx
flows: [checkout]
tests:
  - web/src/tests/
dispatched: null
in_review: null
predicted_success: high
prediction_factors:
  score: 0.8
  deductions:
    - "multiple_files: -0.1"
    - "state_management: -0.1"
created: 2026-07-25
updated: 2026-07-25
---

# WEB-009: App state: error handling + OTP token sessionStorage + checkout validation

> Dự án: [[projects/topvnsport-web/topvnsport-web]]

## Tiêu chí nghiệm thu (AC)

- [ ] appDataSlice có error state, rejected case lưu error message
- [ ] App.tsx hiển thị error UI với retry button khi fetch fails
- [ ] OTP verification token persist trong sessionStorage
- [ ] Checkout form có Zod validation trước khi submit

## Verification

1. Block network → load app → error UI hiển thị với retry button
2. Verify OTP → navigate away → quay lại → token vẫn còn
3. Submit checkout với phone invalid → validation error hiển thị

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] Add error field trong AppDataState
- [ ] Handle rejected case trong appDataSlice
- [ ] Add error UI component trong App.tsx
- [ ] Persist OTP token trong sessionStorage
- [ ] Add Zod schema cho checkout form
- [ ] Display validation errors trong CartModal

## Reference

- Debt file: `docs/TopVNSport - TODO & Technical Debt/web/01_security_and_state.md`
