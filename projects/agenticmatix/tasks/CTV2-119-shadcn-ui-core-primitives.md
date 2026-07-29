---
id: CTV2-119
title: "Install shadcn/ui and Extract Core Primitives"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: normal
risk: normal
deadline: null
executor: "@claude-opus-4.5"
reviewer: "@claude-opus-4.5"
verdict: pass
verdict_by: "@claude-opus-4.5"
verdict_note: "bypass mode - inline execution & verification (tests pass)"
result_ref: 81c2cdd
depends_on: []
files:
  - frontend/package.json
  - frontend/tailwind.config.js
  - frontend/vitest.config.ts
  - frontend/src/components/ui/stat-card.tsx
  - frontend/src/components/ui/alert-banner.tsx
  - frontend/src/components/ui/status-badge.tsx
flows: []
tests:
  - frontend/src/components/ui/__tests__/stat-card.test.tsx
predicted_success: high
prediction_factors:
  score: 1.0
  deductions: []
created: 2026-07-28
updated: 2026-07-28
completed: 2026-07-28
dispatched: 2026-07-28
rejections: 1
---

# CTV2-119: Install shadcn/ui and Extract Core Primitives

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

Phase 1/5 của [[CTV2-118-research-frontend-refactor-strategy]] — nguồn: `docs/research/frontend-refactor-strategy.md` §Component Reuse Recommendation + §Phase 1.

## Tiêu chí nghiệm thu (AC)

- [ ] Chạy shadcn/ui CLI để scaffold `frontend/src/components/ui/`, cấu hình đúng `tailwind.config.js` hiện có (không phá vỡ theme/dark-mode hiện tại).
- [ ] Tạo `StatCard` (icon, label, value, trend) tại `components/ui/stat-card.tsx`.
- [ ] Tạo `AlertBanner` (severity error/warning/info, message, retry action) tại `components/ui/alert-banner.tsx`.
- [ ] Tạo `StatusBadge` (status → color mapping) tại `components/ui/status-badge.tsx`.
- [ ] Test `stat-card.test.tsx` khẳng định: render đúng `label`/`value` truyền vào, và render đúng icon khi có prop `icon`.
- [ ] Không có regression: build frontend (`npm run build`) pass, không file page nào bị sửa trong task này (chỉ tạo primitives, chưa migrate — migrate ở CTV2-126/127).

## Verification
- `npm run build` (frontend) → exit 0
- `npm test -- stat-card` → pass

## Plan
1. Kiểm tra `frontend/package.json`/`tailwind.config.js` hiện tại trước khi thêm dependency.
2. Cài shadcn/ui CLI, scaffold `components/ui/`.
3. Viết 3 primitive component theo class Tailwind đã dùng lặp lại (xem doc §Duplicated Patterns).
4. Viết test cho `StatCard`.

## Findings từ reviewer
- [x] Missing '@' alias in frontend/vitest.config.ts causes stat-card.test.tsx to fail with 'Failed to resolve import @/lib/utils'. Add resolve.alias '@' -> ./src to vitest.config.ts. **Fixed in 81c2cdd**
- [ ] All AC/logic otherwise verified pass (tsc clean, 6 files, no page regressions).
