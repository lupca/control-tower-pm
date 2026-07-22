---
id: CTW-003
title: "Fix dev server startup - ERR_CONNECTION_REFUSED on port 3004"
status: done
priority: high
risk: low
deadline: 2026-07-24
executor: "@gpt-5.6-luna-high"
reviewer: "@gpt-5.6-sol"
result_ref: "7317699"
depends_on: []
files:
  - astro.config.mjs
  - package.json
flows: []
tests: []
dispatched: 2026-07-23
in_review: 2026-07-23
predicted_success: high
prediction_factors:
  score: 0.9
  deductions:
    - "no_tests: -0.1 (devops/config task, no unit tests expected)"
created: 2026-07-23
updated: 2026-07-23
---

# CTW-003: Fix dev server startup - ERR_CONNECTION_REFUSED on port 3004

> Dự án: [[projects/control-tower-web/control-tower-web]]

## Problem

Khi start app (`npm run dev`) và truy cập `http://localhost:3004/`, browser báo:
```
Failed to Load Page
ERR_CONNECTION_REFUSED (-102)
URL: http://localhost:3004/
```

## Tiêu chí nghiệm thu (AC)

- [x] `npm run dev` (hoặc `./npm run dev`) start thành công, không error
- [x] `http://localhost:3004/` accessible trong browser
- [x] Không còn ERR_CONNECTION_REFUSED

## Verification

- `./npm run dev` → server starts, logs "Local: http://localhost:3004"
- `curl -s http://localhost:3004/ | head -1` → returns HTML (not connection refused)

## Possible Causes (để executor investigate)

1. **Port mismatch**: astro.config.mjs có thể config port khác 3004
2. **Host binding**: server bind `127.0.0.1` nhưng truy cập qua hostname khác
3. **npm script không đúng**: package.json thiếu/sai `dev` script
4. **Dependencies chưa install**: node_modules/ chưa có hoặc corrupt

## Plan

1. **Check astro.config.mjs** — verify `server.port` config (default 4321, user expects 3004)
2. **Check package.json** — verify `scripts.dev` command has correct port flag
3. **Verify dependencies** — `ls node_modules/` or run `./npm install` if missing
4. **Fix port config** — set port 3004 in astro.config.mjs or package.json script
5. **Test** — `./npm run dev` → verify `http://localhost:3004/` loads

## Sub-tasks

- [x] Check `astro.config.mjs` for server port/host config
- [x] Check `package.json` scripts.dev command
- [x] Verify node_modules/ exists và dependencies installed
- [x] Fix config và test `npm run dev`
