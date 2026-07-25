---
id: PMI-018
title: "Standardize API clients across frontends"
status: todo
priority: high
risk: normal
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: [PMI-016]
files:
  - PMI/frontend/src/utils/apiClient.ts
  - OMS/frontend/src/utils/api.ts
  - WMS/frontend/src/utils/apiClient.ts
flows: []
tests: []
dispatched: null
in_review: null
predicted_success: high
prediction_factors:
  score: 0.75
  deductions:
    - "depends_on_other_task: -0.15"
    - "multiple_frontends: -0.1"
created: 2026-07-25
updated: 2026-07-25
---

# PMI-018: Standardize API clients across frontends

> Dự án: [[projects/topvnsport-pmi/topvnsport-pmi]]

## Tiêu chí nghiệm thu (AC)

- [ ] Tất cả frontends sử dụng cùng API client interface
- [ ] Consistent error handling (401 → redirect login, retry logic)
- [ ] Consistent request/response interceptors
- [ ] TypeScript types cho API responses

## Verification

- Diff API client implementations → identical hoặc import từ shared
- 401 response → tất cả apps redirect to login
- Network error → consistent retry behavior

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] Define standard API client interface
- [ ] Implement in shared package (sau PMI-016)
- [ ] Migrate PMI frontend
- [ ] Migrate OMS frontend
- [ ] Migrate WMS frontend
- [ ] Add consistent error handling

## Reference

- Debt file: `docs/TopVNSport - TODO & Technical Debt/pmi/07_api_client_standardization.md`
