---
id: WEB-003
title: "Fix vitest dependency version conflict in Web Storefront"
status: done
priority: urgent
risk: normal
deadline: null
executor: "@gpt-5.6-luna-high"
reviewer: "@gpt-5.6-sol-high"
result_ref: "topvnsport@feature/promotion-module (commit c1dbb96)"
depends_on: []
files:
  - web/package.json
flows: []
tests: []
dispatched: 2026-07-23
in_review: 2026-07-23
predicted_success: high
prediction_factors:
  score: 1.0
  deductions: []
created: 2026-07-23
updated: 2026-07-23
---

# WEB-003: Fix vitest dependency version conflict in Web Storefront

> Dự án: [[projects/topvnsport-web/topvnsport-web]]

## Bối cảnh

CI "Web Storefront Build" fail do npm dependency conflict:

```
npm error ERESOLVE unable to resolve dependency tree
npm error peer vitest@"3.2.7" from @vitest/coverage-v8@3.2.7
npm error   dev @vitest/coverage-v8@"^3.0.9" from the root project
npm error Found: vitest@4.1.10
```

`@vitest/coverage-v8@3.2.7` requires `vitest@3.2.7` but `vitest@4.1.10` is installed. Need to align versions.

Lỗi xuất hiện sau commit `remove obsolete OMS coupon code` (WEB-002).

## Tiêu chí nghiệm thu (AC)

- [ ] Align `@vitest/coverage-v8` version với `vitest` version trong `web/package.json`
- [ ] `npm ci` trong `web/` chạy thành công (không có ERESOLVE error)
- [ ] CI "Web Storefront Build" job passes

## Verification

- `cd web && rm -rf node_modules package-lock.json && npm install` → success
- `cd web && npm ci` → success (no ERESOLVE)
- `cd web && npm test` → tests pass
- CI "Web Storefront Build" job passes

## Plan

1. Open `web/package.json`
2. Find current `vitest` version (should be `^4.1.9` or similar 4.x)
3. Find `@vitest/coverage-v8` version (currently `^3.0.9`)
4. Update `@vitest/coverage-v8` to `^4.1.9` (or same as vitest version)
5. Delete `web/package-lock.json` and `web/node_modules/`
6. Run `npm install` to regenerate lock file
7. Verify `npm ci` works without ERESOLVE error
8. Run `npm test` to verify tests still pass

## Sub-tasks

- [ ] 1. Check current vitest version in `web/package.json`
- [ ] 2. Update `@vitest/coverage-v8` to match vitest major version (^4.x)
- [ ] 3. Regenerate `package-lock.json`
- [ ] 4. Verify `npm ci` works

## Notes

- Two options: (a) upgrade `@vitest/coverage-v8` to 4.x to match vitest 4.1.10, or (b) downgrade vitest to 3.x to match coverage-v8 3.2.7
- Recommend option (a) - upgrade coverage-v8 to 4.x since vitest 4.x is newer
