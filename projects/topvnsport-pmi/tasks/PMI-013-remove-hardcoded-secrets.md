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
updated: 2026-07-25
---

# PMI-013: Remove hardcoded secrets từ docker-compose.prod.yml

> Dự án: [[projects/topvnsport-pmi/topvnsport-pmi]]

## Tiêu chí nghiệm thu (AC)

- [ ] Không còn plaintext password/secret trong docker-compose.prod.yml (4 services: PMI, OMS, WMS, identity-service)
- [ ] Tạo `.env.prod.example` với placeholder values cho mỗi service
- [ ] `.gitignore` có pattern `.env.prod`
- [ ] Compose files sử dụng `env_file:` hoặc `${VAR}` syntax không có fallback
- [ ] Document: hướng dẫn generate secrets và deploy

## Verification

- `grep -r "POSTGRES_PASSWORD=" */docker-compose.prod.yml` → chỉ thấy `${POSTGRES_PASSWORD}` không fallback
- `grep -r "JWT_SECRET" */docker-compose.prod.yml` → tương tự
- `grep -r "FERNET_KEY" */docker-compose.prod.yml` → tương tự
- `docker compose -f PMI/docker-compose.prod.yml config` → không có plaintext secrets

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] PMI/docker-compose.prod.yml: remove fallback values, add env_file
- [ ] OMS/docker-compose.prod.yml: remove FERNET_KEY fallback
- [ ] WMS/docker-compose.prod.yml: remove hardcoded secrets
- [ ] identity-service/docker-compose.prod.yml: remove hardcoded secrets
- [ ] Create .env.prod.example for each service
- [ ] Update .gitignore
- [ ] Document secret rotation procedure

## Reference

- Debt file: `docs/TopVNSport - TODO & Technical Debt/pmi/02_security_hardcoded_secrets.md`
