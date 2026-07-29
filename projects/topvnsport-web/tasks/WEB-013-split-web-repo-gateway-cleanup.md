---
id: WEB-013
title: "Split web to separate repo + gateway cleanup + CI/CD for new repo"
repo_root: /home/lupca/projects/topvnsport
status: done
priority: high
risk: high
deadline: 2026-08-05
executor: "@gpt-5.6-sol"
reviewer: "@claude-opus"
result_ref: "9599b4da"
depends_on: []
files:
  - gateway/nginx/conf.d/upstream.prod.conf
  - gateway/nginx/conf.d/locations.prod.conf
  - gateway/nginx/conf.d/locations.http-prod.conf
  - .github/workflows/ci.yml
flows: []
tests: []
dispatched: 2026-07-29
in_review: 2026-07-29
predicted_success: medium
prediction_factors:
  score: 0.6
  deductions:
    - "blast_radius: 8+ files across 2 repos (-0.3)"
    - "touches nginx gateway config - infra risk (-0.1)"
created: 2026-07-29
updated: 2026-07-29
---

# WEB-013: Split web to separate repo + gateway cleanup + CI/CD for new repo

> Dự án: [[projects/topvnsport-web/topvnsport-web]]

## Context

Web đã được tách sang repo riêng:
- **New repo**: `~/projects/topvnsport.com` (https://github.com/lupca/topvnsport.com)
- **Deploy**: Vercel (auto-deploy from GitHub)
- **Old monorepo**: `~/projects/topvnsport` cần cleanup gateway + CI references

## Tiêu chí nghiệm thu (AC)

### Part A: Gateway Cleanup (monorepo topvnsport)
- [x] Remove `web_frontend` upstream from `gateway/nginx/conf.d/upstream.prod.conf` (lines 44-46)
- [x] Update `gateway/nginx/conf.d/locations.prod.conf` — topvnsport.com server block: redirect to Vercel URL OR remove entirely (chọn redirect để không break bookmark)
- [x] Update `gateway/nginx/conf.d/locations.http-prod.conf` — same: redirect topvnsport.com → Vercel
- [x] Gateway restart không lỗi: `docker compose -f gateway/docker-compose.prod.yml config` pass

### Part B: CI Cleanup (monorepo topvnsport)
- [x] Remove `web:` from paths-filter outputs in `.github/workflows/ci.yml` (line 35, 50-51)
- [x] Remove `web-build` job (lines 283-320)
- [x] Remove `web/docker-compose.prod.yml` validation (line 371)
- [x] Remove `web-build` from `ci-success` job dependencies (lines 387, 399, 410)
- [x] CI workflow runs without error on PR (no web/ path to trigger)

### Part C: New Repo CI/CD (topvnsport.com)
- [x] Create `.github/workflows/ci.yml` với: lint (eslint), typecheck (tsc), test (vitest), build (vite)
- [x] Vercel auto-deploy đã hoạt động (verify: push → preview deploy)
- [x] Test workflow chạy pass trên PR

### Part D: Control-tower Registry Update
- [x] Update `index.md` PROJECT REGISTRY: `topvnsport-web` repo_root → `/home/lupca/projects/topvnsport.com`

## Verification

```bash
# A: Gateway config valid
cd ~/projects/topvnsport/gateway && docker compose -f docker-compose.prod.yml config

# B: CI workflow syntax valid
cd ~/projects/topvnsport && gh workflow view ci.yml

# C: New repo CI exists and passes
cd ~/projects/topvnsport.com && gh workflow run ci.yml && gh run list --limit 1

# D: Registry updated (manual check)
grep "topvnsport-web" ~/projects/control-tower/index.md
```

## Plan

### Phase 1: Gateway Cleanup (monorepo ~/projects/topvnsport)

1. **Edit `gateway/nginx/conf.d/upstream.prod.conf`**:
   - Remove lines 44-46 (web_frontend upstream block)

2. **Edit `gateway/nginx/conf.d/locations.prod.conf`**:
   - Replace topvnsport.com server block (lines ~37-61) with 301 redirect to Vercel:
     ```nginx
     server {
         listen 443 ssl http2;
         server_name topvnsport.com www.topvnsport.com;
         ssl_certificate /etc/letsencrypt/live/topvnsport.com/fullchain.pem;
         ssl_certificate_key /etc/letsencrypt/live/topvnsport.com/privkey.pem;
         return 301 https://topvnsport-com.vercel.app$request_uri;
     }
     ```

3. **Edit `gateway/nginx/conf.d/locations.http-prod.conf`**:
   - Replace topvnsport.com server block with same redirect pattern (for HTTP→HTTPS→Vercel chain)

4. **Validate**: `docker compose -f gateway/docker-compose.prod.yml config`

### Phase 2: CI Cleanup (monorepo)

5. **Edit `.github/workflows/ci.yml`**:
   - Remove `web:` output (line 35)
   - Remove `web:` path filter (lines 50-51)
   - Remove entire `web-build` job (lines 283-320)
   - Remove `web/docker-compose.prod.yml` validation (line 371)
   - Remove `web-build` from `ci-success` needs + result checks

6. **Push + verify CI passes** (no web/ dir = no web job triggered)

### Phase 3: New Repo CI (~/projects/topvnsport.com)

7. **Create `.github/workflows/ci.yml`**:
   ```yaml
   name: CI
   on: [push, pull_request]
   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: actions/setup-node@v4
           with: { node-version: '22' }
         - run: npm ci
         - run: npm run lint
         - run: npm run typecheck
         - run: npm run test
         - run: npm run build
   ```

8. **Verify Vercel auto-deploy**: push → check Vercel dashboard for preview deploy

### Phase 4: Control-tower Update

9. **Edit `index.md`**: Update PROJECT REGISTRY row for `topvnsport-web`:
   - `repo_root` → `/home/lupca/projects/topvnsport.com`
   - Note: Graph build = pending (new repo, needs initial build)

## Sub-tasks

- [ ] A1: Remove `web_frontend` upstream from `upstream.prod.conf`
- [ ] A2: Update `locations.prod.conf` — redirect topvnsport.com to Vercel
- [ ] A3: Update `locations.http-prod.conf` — same redirect
- [ ] A4: Validate gateway config
- [ ] B1: Remove web paths-filter from ci.yml
- [ ] B2: Remove web-build job from ci.yml
- [ ] B3: Remove web-build from ci-success dependencies
- [ ] C1: Create `.github/workflows/ci.yml` in new repo
- [ ] C2: Verify Vercel auto-deploy works
- [ ] D1: Update control-tower PROJECT REGISTRY
