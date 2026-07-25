---
id: PMI-016
title: "Extract shared packages - giảm code duplication 4x"
status: todo
priority: high
risk: high
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: []
files:
  - PMI/frontend/src/utils/apiClient.ts
  - OMS/frontend/src/utils/api.ts
  - WMS/frontend/src/utils/apiClient.ts
  - identity-service/frontend/src/utils/apiClient.ts
flows: []
tests: []
dispatched: null
in_review: null
predicted_success: medium
prediction_factors:
  score: 0.5
  deductions:
    - "blast_radius_large: -0.3 (4 frontends)"
    - "risk_high: -0.2 (major refactor)"
created: 2026-07-25
updated: 2026-07-25
---

# PMI-016: Extract shared packages - giảm code duplication 4x

> Dự án: [[projects/topvnsport-pmi/topvnsport-pmi]]

## Tiêu chí nghiệm thu (AC)

- [ ] Tạo `packages/` directory với shared code (apiClient, types, utils)
- [ ] 4 frontends import từ shared package thay vì duplicate code
- [ ] Workspace config (npm/pnpm) được setup
- [ ] Build pipeline hoạt động với monorepo structure
- [ ] Giảm ít nhất 50% duplicate code lines

## Verification

- `ls packages/` → có shared-utils, shared-types, shared-api
- `grep -r "from '@topvnsport/shared" */frontend/src/` → imports từ shared
- `npm run build` từ root → tất cả packages build thành công
- `npm run test` → tests pass

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] Setup monorepo workspace (npm workspaces hoặc pnpm)
- [ ] Extract apiClient vào packages/shared-api
- [ ] Extract common types vào packages/shared-types
- [ ] Update PMI frontend imports
- [ ] Update OMS frontend imports
- [ ] Update WMS frontend imports
- [ ] Update identity-service frontend imports
- [ ] Update CI/CD pipeline

## Reference

- Debt file: `docs/TopVNSport - TODO & Technical Debt/pmi/05_code_deduplication.md`
- Architecture: `docs/TopVNSport - TODO & Technical Debt/architecture/05_shared_packages/`
