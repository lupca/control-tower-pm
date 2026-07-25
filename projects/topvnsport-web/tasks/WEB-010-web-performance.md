---
id: WEB-010
title: "Performance: remove simulated latency + code splitting"
status: todo
priority: medium
risk: normal
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: []
files:
  - web/src/services/sport-api/constants.ts
  - web/src/services/sport-api/index.ts
  - web/src/App.tsx
flows: []
tests: []
dispatched: null
in_review: null
predicted_success: high
prediction_factors:
  score: 0.9
  deductions:
    - "simple_change: -0.1"
created: 2026-07-25
updated: 2026-07-25
---

# WEB-010: Performance: remove simulated latency + code splitting

> Dự án: [[projects/topvnsport-web/topvnsport-web]]

## Tiêu chí nghiệm thu (AC)

- [ ] `SIMULATED_LATENCY` = 0 trong production build
- [ ] Heavy components sử dụng React.lazy() + Suspense
- [ ] Bundle size giảm cho initial load
- [ ] Lighthouse performance score cải thiện

## Verification

- `grep SIMULATED_LATENCY dist/` → 0 hoặc không có
- Network tab: main bundle < 200KB
- Lighthouse: Performance > 80

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] Gate SIMULATED_LATENCY với `import.meta.env.DEV`
- [ ] Add React.lazy() cho ProductDetail, Cart components
- [ ] Add Suspense với loading fallback
- [ ] Verify bundle splitting với build analyzer

## Reference

- Debt file: `docs/TopVNSport - TODO & Technical Debt/web/02_performance.md`
