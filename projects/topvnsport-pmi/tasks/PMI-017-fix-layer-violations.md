---
id: PMI-017
title: "Fix HTTP exceptions trong service layer"
status: todo
priority: high
risk: normal
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: []
files:
  - PMI/backend/services/
flows: []
tests:
  - PMI/backend/tests/
dispatched: null
in_review: null
predicted_success: high
prediction_factors:
  score: 0.8
  deductions:
    - "blast_radius_medium: -0.1"
    - "no_specific_tests: -0.1"
created: 2026-07-25
updated: 2026-07-25
---

# PMI-017: Fix HTTP exceptions trong service layer

> Dự án: [[projects/topvnsport-pmi/topvnsport-pmi]]

## Tiêu chí nghiệm thu (AC)

- [ ] Service layer không raise HTTPException trực tiếp
- [ ] Services raise domain exceptions (NotFoundError, ValidationError, etc.)
- [ ] Routers catch domain exceptions và convert to HTTPException
- [ ] Exception handler middleware được setup

## Verification

- `grep -r "HTTPException" PMI/backend/services/` → empty
- `grep -r "raise.*Error" PMI/backend/services/` → domain exceptions
- Unit tests cho services không import fastapi

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] Create `PMI/backend/exceptions.py` với domain exceptions
- [ ] Refactor services để raise domain exceptions
- [ ] Add exception handler trong main.py
- [ ] Update routers để catch và convert exceptions

## Reference

- Debt file: `docs/TopVNSport - TODO & Technical Debt/pmi/06_layer_violations.md`
