---
id: WEB-014
title: "Remove Docker files from standalone web repo (Vercel-only)"
repo_root: /home/lupca/projects/topvnsport.com
status: done
priority: medium
risk: normal
deadline: 2026-08-01
executor: "@gpt-5.6-sol"
reviewer: "@claude-opus"
result_ref: "d6099b2e"
depends_on: [WEB-013]
files:
  - Dockerfile
  - Dockerfile.dev
  - docker-compose.yml
  - docker-compose.prod.yml
flows: []
tests: []
dispatched: 2026-07-29
in_review: 2026-07-29
predicted_success: high
prediction_factors:
  score: 0.9
  deductions:
    - "simple deletion task (-0.1)"
created: 2026-07-29
updated: 2026-07-29
---

# WEB-014: Remove Docker files from standalone web repo (Vercel-only)

> Dự án: [[projects/topvnsport-web/topvnsport-web]]

## Context

Repo `topvnsport.com` đã tách khỏi monorepo và deploy trên Vercel. Docker files còn lại reference cấu trúc monorepo cũ (broken paths) và không cần thiết cho Vercel deployment.

## Tiêu chí nghiệm thu (AC)

- [x] Xóa `Dockerfile` (nếu có)
- [x] Xóa `Dockerfile.dev`
- [x] Xóa `docker-compose.yml`
- [x] Xóa `docker-compose.prod.yml`
- [x] Xóa `nginx.conf` (nếu chỉ dùng cho Docker)
- [x] Verify: `npm run build` vẫn pass
- [x] Verify: `npm run test` vẫn pass

## Verification

```bash
cd ~/projects/topvnsport.com
ls Dockerfile* docker-compose* nginx.conf 2>/dev/null && echo "FAIL: files still exist" || echo "OK: files removed"
npm run build
npm run test
```

## Plan

1. `cd ~/projects/topvnsport.com`
2. `rm -f Dockerfile Dockerfile.dev docker-compose.yml docker-compose.prod.yml nginx.conf`
3. `npm run build` — verify build works
4. `npm run test` — verify tests pass
5. Commit changes

## Sub-tasks

- [ ] Delete Docker-related files
- [ ] Verify build/test still work
