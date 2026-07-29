---
id: PMI-013
title: "Remove hardcoded secrets từ docker-compose.prod.yml"
status: todo
priority: urgent
risk: high
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: []
files:
  - PMI/docker-compose.prod.yml
  - OMS/docker-compose.prod.yml
  - WMS/docker-compose.prod.yml
  - identity-service/docker-compose.prod.yml
flows: []
tests: []
dispatched: null
in_review: null
predicted_success: high
prediction_factors:
  score: 0.8
  deductions:
    - "risk_high: -0.2 (production secrets)"
created: 2026-07-25
updated: 2026-07-28
---

# PMI-013: Remove hardcoded secrets từ docker-compose.prod.yml

> Dự án: [[projects/topvnsport-pmi/topvnsport-pmi]]

## Tiêu chí nghiệm thu (AC)

- [x] JWT_SECRET_KEY: `${JWT_SECRET_KEY:?}` (done via OMS-011)
- [x] FERNET_KEY: `${FERNET_KEY:?}` (done via OMS-011)
- [x] RDS credentials: `${RDS_*:?}` (done via DEVOPS-001)
- [x] POSTGRES_PASSWORD: N/A — services dùng RDS, không còn local DB
- [ ] ALLOWED_SERVICE_KEYS: còn hardcode `prod-service-api-key-must-change` trong PMI
- [x] `.gitignore` có pattern `.env.prod`
- [x] Document: deploy_prod.sh + GitHub secrets

## Verification

- `grep -r "POSTGRES_PASSWORD=" */docker-compose.prod.yml` → chỉ thấy `${POSTGRES_PASSWORD}` không fallback
- `grep -r "JWT_SECRET" */docker-compose.prod.yml` → tương tự
- `grep -r "FERNET_KEY" */docker-compose.prod.yml` → tương tự
- `docker compose -f PMI/docker-compose.prod.yml config` → không có plaintext secrets

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [x] PMI/docker-compose.prod.yml: JWT_SECRET_KEY done, còn ALLOWED_SERVICE_KEYS
- [x] OMS/docker-compose.prod.yml: done (FERNET_KEY, JWT, RDS all use ${VAR:?})
- [x] WMS/docker-compose.prod.yml: done (JWT, RDS all use ${VAR:?})
- [x] identity-service/docker-compose.prod.yml: done (JWT uses ${VAR:?})
- [x] .gitignore updated
- [x] Document: deploy_prod.sh handles secrets from GitHub

**Remaining:** Chỉ còn `ALLOWED_SERVICE_KEYS=prod-service-api-key-must-change` trong PMI.

## Reference

- Debt file: `docs/TopVNSport - TODO & Technical Debt/pmi/02_security_hardcoded_secrets.md`
