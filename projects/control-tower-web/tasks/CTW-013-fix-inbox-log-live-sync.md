---
id: CTW-013
title: "Fix inbox & log pages read from live control-tower repo"
status: done
priority: high
risk: normal
deadline: null
executor: "@gpt-5.6-luna-high"
reviewer: "@claude-sonnet-high"
result_ref: "846d79c"
depends_on: []
files:
  - src/pages/inbox.astro
  - src/lib/log-parser.ts
  - src/lib/data.ts
flows: []
tests: []
dispatched: 2026-07-24
in_review: null
predicted_success: high
prediction_factors:
  score: 0.9
  deductions:
    - "simple_fix: -0.1"
rejections: 0
created: 2026-07-24
updated: 2026-07-24
---

# CTW-013: Fix inbox & log pages read from live control-tower repo

> Dự án: [[projects/control-tower-web/control-tower-web]]

## Problem

Current error:
```
TypeError: (0 , __vite_ssr_import_5__.getControlTowerRoot) is not a function
pages/inbox.astro:7:16
```

`getControlTowerRoot()` import không work trong inbox.astro. Cần fix cách import hoặc export function này.

## Tiêu chí nghiệm thu (AC)

- [x] **AC1:** `/inbox` page loads successfully, shows content from `control-tower/inbox.md`
- [x] **AC2:** `/log` page loads successfully, shows content from `control-tower/log.md`
- [x] **AC3:** `npm run dev` và `npm run build` pass without errors

## Context

- `getControlTowerRoot()` is defined in `src/lib/data.ts`
- It should return path to control-tower repo (sibling directory)
- inbox.astro and log-parser.ts need to use this function

## Plan

1. Check if `getControlTowerRoot` is properly exported from `src/lib/data.ts`
2. Fix export/import issues
3. Test both `/inbox` and `/log` pages
4. Verify build passes
