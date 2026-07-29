---
id: CTV2-125
title: "Split ProjectDetail Page"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: normal
risk: normal
deadline: null
executor: "@claude-opus-4.5"
reviewer: "@claude-opus-4.5"
verdict: pass
verdict_by: "@claude-opus-4.5"
verdict_note: "bypass mode - components extracted, tests pass"
result_ref: 669cb01
completed: 2026-07-28
depends_on: [CTV2-122]
files:
  - frontend/src/pages/ProjectDetail.tsx
  - frontend/src/components/projects/ProjectKpiCards.tsx
  - frontend/src/components/projects/ProjectTaskList.tsx
  - frontend/src/components/projects/ProjectHeader.tsx
  - frontend/src/pages/__tests__/ProjectDetail.test.tsx
flows: []
tests:
  - frontend/src/pages/__tests__/ProjectDetail.test.tsx
predicted_success: high
prediction_factors:
  score: 0.8
  deductions:
    - "touches hub node ProjectDetailPage (degree 61) (-0.2)"
created: 2026-07-28
updated: 2026-07-28
---

# CTV2-125: Split ProjectDetail Page

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

Phase 3/5 của [[CTV2-118-research-frontend-refactor-strategy]] — nguồn: `docs/research/frontend-refactor-strategy.md` §Component Audit (ProjectDetail.tsx, 403 dòng). Phụ thuộc [[CTV2-122-parallelize-api-calls]] (cùng sửa `ProjectDetail.tsx`).

## Tiêu chí nghiệm thu (AC)

- [ ] Tách **ProjectHeader** (banner + nav) ra `components/projects/ProjectHeader.tsx`.
- [ ] Tách **ProjectKpiCards** (4 stat card) ra `components/projects/ProjectKpiCards.tsx`.
- [ ] Tách **ProjectTaskList** (table + filters) ra `components/projects/ProjectTaskList.tsx`.
- [ ] `ProjectDetail.tsx` sau khi tách chỉ còn fetch (đã parallelize từ CTV2-122, error banner + "Unknown" date từ CTV2-120, `useMemo` filter từ CTV2-121) + compose 3 component trên.
- [ ] Test `ProjectDetail.test.tsx` (đã có test memoization từ CTV2-121) bổ sung khẳng định: `ProjectTaskList` filter theo `search`/`statusFilter` vẫn hoạt động đúng sau khi tách.

## Verification
- `npm test -- ProjectDetail` → pass (bao gồm test memoization cũ)

## Plan
1. Đọc `ProjectDetail.tsx` sau khi CTV2-120/121/122 đã áp dụng.
2. Tách `ProjectHeader`, `ProjectKpiCards`, `ProjectTaskList`.
3. `ProjectDetail.tsx` chỉ giữ state/fetch + compose.
4. Cập nhật test `ProjectDetail.test.tsx` cho cấu trúc mới.
