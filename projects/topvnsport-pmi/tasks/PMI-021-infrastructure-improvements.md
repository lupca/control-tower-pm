---
id: PMI-021
title: "Infrastructure: health checks, limits, cache, resilience"
status: todo
priority: medium
risk: normal
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: []
files:
  - PMI/docker-compose.prod.yml
  - OMS/docker-compose.prod.yml
  - WMS/docker-compose.prod.yml
  - gateway/nginx/
flows: []
tests: []
dispatched: null
in_review: null
predicted_success: high
prediction_factors:
  score: 0.8
  deductions:
    - "infrastructure_change: -0.2"
created: 2026-07-25
updated: 2026-07-25
---

# PMI-021: Infrastructure: health checks, limits, cache, resilience

> Dự án: [[projects/topvnsport-pmi/topvnsport-pmi]]

## Tiêu chí nghiệm thu (AC)

- [ ] Health check endpoints cho mỗi service (/health, /ready)
- [ ] Docker healthcheck configured cho containers
- [ ] Resource limits (memory, CPU) được set trong compose
- [ ] Redis/caching layer cho frequently accessed data
- [ ] Graceful shutdown handling

## Verification

- `curl http://service/health` → 200 OK với status info
- `docker inspect container` → healthcheck configured
- `docker stats` → memory limits enforced
- Service restart → no data loss, graceful shutdown

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] Add /health endpoint cho PMI, OMS, WMS backends
- [ ] Add Docker healthcheck trong compose files
- [ ] Set resource limits (memory: 512m-1g per service)
- [ ] Add Redis service cho caching
- [ ] Implement cache layer cho product list
- [ ] Add graceful shutdown handlers

## Reference

- Debt file: `docs/TopVNSport - TODO & Technical Debt/pmi/10_infrastructure_improvements.md`
