---
id: PMI-020
title: "Add React Error Boundaries cho all frontends"
status: todo
priority: medium
risk: normal
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: []
files:
  - PMI/frontend/src/components/
  - OMS/frontend/src/components/
  - WMS/frontend/src/components/
flows: []
tests: []
dispatched: null
in_review: null
predicted_success: high
prediction_factors:
  score: 0.85
  deductions:
    - "multiple_frontends: -0.15"
created: 2026-07-25
updated: 2026-07-25
---

# PMI-020: Add React Error Boundaries cho all frontends

> Dự án: [[projects/topvnsport-pmi/topvnsport-pmi]]

## Tiêu chí nghiệm thu (AC)

- [ ] ErrorBoundary component được tạo (hoặc dùng react-error-boundary)
- [ ] Wrap root App component với ErrorBoundary
- [ ] Wrap critical sections (data tables, forms) với ErrorBoundary
- [ ] User-friendly fallback UI khi error xảy ra
- [ ] Error được log (console hoặc error tracking service)

## Verification

- Trigger JS error trong component → fallback UI hiển thị, app không crash
- Error details được log
- User có thể retry hoặc navigate away

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] Create/install ErrorBoundary component
- [ ] Add to PMI frontend App.tsx
- [ ] Add to OMS frontend App.tsx
- [ ] Add to WMS frontend App.tsx
- [ ] Add to identity-service frontend
- [ ] Create fallback UI component
- [ ] Add error logging

## Reference

- Debt file: `docs/TopVNSport - TODO & Technical Debt/pmi/09_error_boundaries.md`
