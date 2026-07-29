---
id: DEVOPS-004
title: "Domain migration voma.vn + HTTPS cho PIM/OMS/WMS"
repo_root: /home/lupca/projects/topvnsport
status: done
priority: high
risk: high
deadline: 2026-08-05
executor: "@gpt-5.6-sol"
reviewer: "@claude-opus"
result_ref: "77a6d256"
depends_on: []
files:
  - gateway/nginx/conf.d/upstream.prod.conf
  - gateway/nginx/conf.d/locations.prod.conf
  - gateway/nginx/conf.d/locations.http-prod.conf
  - .github/workflows/deploy.yml
  - PMI/backend/.env.prod.example
  - OMS/backend/.env.prod.example
  - WMS/backend/.env.prod.example
flows: []
tests: []
dispatched: 2026-07-29
in_review: 2026-07-29
predicted_success: medium
prediction_factors:
  score: 0.6
  deductions:
    - "touches gateway + 3 services (-0.2)"
    - "production config changes (-0.2)"
created: 2026-07-29
updated: 2026-07-29
---

# DEVOPS-004: Domain migration voma.vn + HTTPS cho PIM/OMS/WMS

> Dự án: [[projects/topvnsport-devops/topvnsport-devops]]

## Context

Chuyển tất cả services sang domain voma.vn với HTTPS:
- api-pim.voma.vn (hiện tại: api-pmi.topvnsport.com)
- api-oms.voma.vn
- api-wms.voma.vn
- pim.voma.vn, oms.voma.vn, wms.voma.vn (frontends)
- identity.voma.vn

Externalize env vars để quản lý qua GitHub Actions secrets thay vì hardcode.

## Tiêu chí nghiệm thu (AC)

### Gateway Config
- [x] Update `upstream.prod.conf`: server names match new domain pattern
- [x] Update `locations.prod.conf`: SSL certs cho *.voma.vn
- [x] Update `locations.http-prod.conf`: redirect HTTP → HTTPS cho voma.vn
- [x] Tất cả endpoints enforce HTTPS (không có http://)

### Environment Externalization
- [x] PIM: `.env.prod.example` chứa placeholders, không hardcode URLs
- [x] OMS: `.env.prod.example` chứa placeholders, không hardcode URLs
- [x] WMS: `.env.prod.example` chứa placeholders, không hardcode URLs
- [x] GitHub Actions `deploy.yml`: inject env vars từ secrets

### CORS
- [x] Gateway CORS config allow voma.vn origins
- [x] Backend services CORS config (nếu có) allow voma.vn

### Verification
- [x] `docker compose -f gateway/docker-compose.prod.yml config` pass
- [x] Không còn reference đến topvnsport.com trong production configs (trừ redirect legacy)

## Verification

```bash
# Config valid
cd ~/projects/topvnsport/gateway && docker compose -f docker-compose.prod.yml config

# No old domain in prod configs (except redirects)
grep -r "topvnsport.com" gateway/nginx/conf.d/*.prod.conf | grep -v "return 301"

# Check HTTPS enforcement
grep -r "http://" PMI/backend/.env.prod.example OMS/backend/.env.prod.example WMS/backend/.env.prod.example
```

## Plan

### Phase 1: Gateway nginx config
1. Update `gateway/nginx/conf.d/upstream.prod.conf` — no changes needed (upstreams are internal Docker names)
2. Update `gateway/nginx/conf.d/locations.prod.conf`:
   - Change `server_name` from `*.topvnsport.com` to `*.voma.vn`
   - Update SSL cert paths to `/etc/letsencrypt/live/voma.vn/`
3. Update `gateway/nginx/conf.d/locations.http-prod.conf`:
   - Same domain changes
   - Keep legacy topvnsport.com redirects

### Phase 2: Environment externalization
4. Create/update `.env.prod.example` files in PMI/OMS/WMS backends:
   - Replace hardcoded URLs with `${VAR_NAME}` placeholders
   - Document required env vars
5. Update `.github/workflows/deploy.yml`:
   - Add secrets injection for API URLs
   - Use GitHub Secrets for sensitive config

### Phase 3: CORS
6. Verify gateway CORS (`$http_origin`) handles voma.vn
7. Check backend CORS_ALLOWED_ORIGINS configs

### Phase 4: Validation
8. `docker compose -f gateway/docker-compose.prod.yml config`
9. Grep for remaining topvnsport.com references

## Sub-tasks

- [ ] Update gateway nginx configs for voma.vn domain
- [ ] Update SSL cert paths for voma.vn
- [ ] Create/update .env.prod.example files with placeholders
- [ ] Update deploy.yml to inject secrets
- [ ] Verify CORS allows voma.vn origins
- [ ] Test config validation
