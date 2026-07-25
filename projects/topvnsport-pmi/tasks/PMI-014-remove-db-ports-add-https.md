---
id: PMI-014
title: "Remove DB port exposure + Add HTTPS/TLS production"
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
  - gateway/docker-compose.prod.yml
  - gateway/nginx/conf.d/locations.prod.conf
flows: []
tests: []
dispatched: null
in_review: null
predicted_success: high
prediction_factors:
  score: 0.8
  deductions:
    - "risk_high: -0.2 (infrastructure change)"
created: 2026-07-25
updated: 2026-07-25
---

# PMI-014: Remove DB port exposure + Add HTTPS/TLS production

> Dự án: [[projects/topvnsport-pmi/topvnsport-pmi]]

## Tiêu chí nghiệm thu (AC)

- [ ] DB ports (15433, 15434, 15435) không còn expose ra host trong production compose
- [ ] Gateway expose port 443 và có TLS server block
- [ ] HTTP → HTTPS redirect hoạt động
- [ ] SSL certificate được mount đúng cách
- [ ] HSTS header được set

## Verification

- `grep -r "ports:" */docker-compose.prod.yml | grep 543` → empty (no DB ports)
- `curl -I http://domain.com` → 301 redirect to https
- `curl -I https://domain.com` → 200 với HSTS header
- External port scan: 15433-15435 không reachable

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] Remove `ports:` section từ db service trong PMI/OMS/WMS compose.prod.yml
- [ ] Add port 443 expose trong gateway compose
- [ ] Create TLS server block trong nginx config
- [ ] Add certbot setup instructions
- [ ] Test HTTP→HTTPS redirect

## Reference

- Debt file: `docs/TopVNSport - TODO & Technical Debt/pmi/03_security_https_database.md`
