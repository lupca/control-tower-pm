---
id: PMI-010
title: "Fix TypeScript type error in PromotionList renderStatusBadge"
status: done
priority: urgent
risk: high
deadline: null
executor: "@gpt-5.6-luna-high"
reviewer: "@gpt-5.6-sol-high"
result_ref: "topvnsport@feature/promotion-module (commit c1dbb96)"
depends_on: []
files:
  - PMI/frontend/src/components/promotions/PromotionList.tsx
flows: [PromotionsPage]
tests:
  - PMI/frontend/tests/e2e/promotions.spec.ts
dispatched: 2026-07-23
in_review: 2026-07-23
predicted_success: high
prediction_factors:
  score: 0.8
  deductions:
    - "hub_node: PromotionList (84 degree) (-0.2)"
created: 2026-07-23
updated: 2026-07-23
---

# PMI-010: Fix TypeScript type error in PromotionList renderStatusBadge

> Dự án: [[projects/topvnsport-pmi/topvnsport-pmi]]

## Bối cảnh

CI bị fail do type error trong `renderStatusBadge` function. Config object định nghĩa thiếu `text` property mà TypeScript type yêu cầu.

```typescript
// Line 195: Type expects { bg: string; text: string; label: string; icon: any }
// But objects only have { bg: "...", label: "...", icon: ... } - missing text
```

Lỗi xuất hiện sau commit `remove obsolete OMS coupon code` (WEB-002).

## Tiêu chí nghiệm thu (AC)

- [ ] Add `text` property to all status config objects in `renderStatusBadge` (line 196-200)
- [ ] TypeScript compilation passes (`npm run type-check` hoặc `npx tsc --noEmit`)
- [ ] PMI Frontend Tests CI job passes

## Verification

- `cd PMI/frontend && npx tsc --noEmit` → 0 errors
- `cd PMI/frontend && npm test` → 100% pass
- CI "PMI Frontend Tests" job passes

## Plan

1. Open `PMI/frontend/src/components/promotions/PromotionList.tsx`
2. Locate `renderStatusBadge` function (line 194-211)
3. Find the config Record on line 195-200
4. For each status entry (DRAFT, SCHEDULED, ACTIVE, PAUSED, ENDED), extract the text color class from the `bg` string and add as separate `text` property:
   - DRAFT: `text: "text-gray-700"` (from `bg-gray-100 text-gray-700 border-gray-200`)
   - SCHEDULED: `text: "text-blue-700"`
   - ACTIVE: `text: "text-emerald-700"`
   - PAUSED: `text: "text-amber-700"`
   - ENDED: check actual value
5. Update the `bg` property to contain only the background classes (remove text color)
6. Run `npx tsc --noEmit` to verify TypeScript compiles
7. Run `npm test` to verify no regressions

## Sub-tasks

- [ ] 1. Add `text` property to DRAFT config (extract from `bg` classes)
- [ ] 2. Add `text` property to SCHEDULED config
- [ ] 3. Add `text` property to ACTIVE config
- [ ] 4. Add `text` property to PAUSED config
- [ ] 5. Add `text` property to ENDED config (if exists)
- [ ] 6. Verify TypeScript compilation

## Notes

- `PromotionList` is a hub node (84 degree) + bridge node — any change has wide blast radius, hence `risk: high`
- The `text` property likely should contain just the text color class (e.g., `text-gray-700`) extracted from the combined `bg` string
