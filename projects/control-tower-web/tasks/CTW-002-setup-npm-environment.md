---
id: CTW-002
title: "Setup npm environment cho control-tower-web"
status: todo
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

- [ ] npm commands chạy được trong `/home/lupca/projects/control-tower-web` mà không qua Docker wrapper
- [ ] `npm install` tạo `node_modules/` trong project directory
- [ ] `npm run build` (astro build) chạy thành công, output vào `dist/`
- [ ] CSS được build đầy đủ (Tailwind utilities có trong output CSS)

## Proposed Solutions

1. **Option A: Bypass wrapper** — tạo script `/home/lupca/projects/control-tower-web/npm` gọi trực tiếp real npm binary
2. **Option B: Real npm** — cài npm thực (không wrapper) vào path khác, ví dụ `/usr/local/bin/npm`
3. **Option C: Docker container riêng** — setup container `control-tower-web` tương tự `pim-frontend`

## Plan

*(Filled in at Plan Gate)*
