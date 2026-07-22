---
id: CTW-002
title: "Setup npm environment cho control-tower-web"
status: done
executor: "@claude-opus-4.5"
reviewer: "@claude-reviewer"
dispatched: 2026-07-23
result_ref: "03a7776"
updated: 2026-07-23
type: devops
priority: high
created: 2026-07-23
deadline: 2026-07-24
files:
  - package.json
  - astro.config.mjs
  - tailwind.config.mjs
tests: []
flows: []
risk: low
predicted_success: high
prediction_factors:
  score: 0.9
  deductions:
    - "no_tests: -0.1 (devops task, no unit tests expected)"
---

# CTW-002: Setup npm environment cho control-tower-web

> Dự án: [[projects/control-tower-web/control-tower-web]]

## Problem

npm wrapper tại `/home/lupca/.local/bin/npm` chạy `docker exec pim-frontend npm "$@"` — chỉ hỗ trợ project `topvnsport/PMI/frontend`, không hỗ trợ project khác.

Khi chạy `npm install` hoặc `npm run build` trong control-tower-web, packages được cài vào Docker container thay vì local `node_modules/`.

## Acceptance Criteria

- [x] npm commands chạy được trong `/home/lupca/projects/control-tower-web` mà không qua Docker wrapper
- [x] `npm install` tạo `node_modules/` trong project directory
- [x] `npm run build` (astro build) chạy thành công, output vào `dist/`
- [x] CSS được build đầy đủ (Tailwind utilities có trong output CSS)

## Proposed Solutions

1. **Option A: Bypass wrapper** — tạo script `/home/lupca/projects/control-tower-web/npm` gọi trực tiếp real npm binary
2. **Option B: Real npm** — cài npm thực (không wrapper) vào path khác, ví dụ `/usr/local/bin/npm`
3. **Option C: Docker container riêng** — setup container `control-tower-web` tương tự `pim-frontend`

## Plan

**Chọn Option A: Bypass wrapper** — đơn giản nhất, không cần Docker.

### Steps

1. **Tìm real npm binary** trong Docker container hoặc cài npm standalone:
   ```bash
   # Option 1: Extract npm từ node image
   docker run --rm -v /home/lupca/.local/bin:/out node:20 cp -r /usr/local/lib/node_modules/npm /out/npm-real
   
   # Option 2: Cài nvm + node/npm riêng
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
   nvm install 20
   ```

2. **Tạo wrapper script** tại `/home/lupca/projects/control-tower-web/npm`:
   ```bash
   #!/bin/bash
   # Local npm for control-tower-web (bypasses Docker wrapper)
   exec /home/lupca/.local/bin/npm-real/bin/npm-cli.js "$@"
   ```

3. **Test npm install**:
   ```bash
   cd /home/lupca/projects/control-tower-web
   ./npm install
   ls node_modules/  # Verify packages installed locally
   ```

4. **Test astro build**:
   ```bash
   ./npm run build
   ls dist/  # Verify output
   grep "flex" dist/_astro/*.css  # Verify Tailwind utilities present
   ```

### DoD Verification
- [ ] `./npm install` creates `node_modules/` locally
- [ ] `./npm run build` succeeds
- [ ] `dist/_astro/*.css` contains Tailwind utilities (flex, grid, bg-*)
