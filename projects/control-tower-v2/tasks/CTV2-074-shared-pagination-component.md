---
id: CTV2-074
title: "Create Shared Pagination Component"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: medium
risk: normal
deadline: null
executor: "@luna"
reviewer: "@claude-opus"
result_ref: "484eae8"
depends_on: []
files:
  - frontend/src/components/common/Pagination.tsx
  - frontend/src/pages/Tasks.tsx
  - frontend/src/pages/Agents.tsx
  - frontend/src/components/TaskTable.tsx
flows: []
tests: []
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: high
prediction_factors:
  score: 0.9
  deductions:
    - "blast_radius: 4 files (-0.0)"
    - "no existing tests (-0.1)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-074: Create Shared Pagination Component

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Tiêu chí nghiệm thu (AC)

- [x] `frontend/src/components/common/Pagination.tsx` exists with props: `currentPage`, `totalPages`, `totalItems`, `pageSize`, `onPageChange`, optional `onPageSizeChange`
- [x] Pagination displays: Previous/Next buttons, "Page X of Y (N items)" text
- [x] Optional page-size selector (10/25/50) when `onPageSizeChange` provided
- [x] `TaskTable.tsx` uses shared Pagination with client-side pagination (default 25 rows)
- [x] `Agents.tsx` refactored to use shared Pagination (remove ad-hoc code at lines 288-309)
- [x] Dark mode styling consistent with existing UI (gray-800/700 buttons, gray-400 text)
- [x] Buttons disabled state when at first/last page

## Verification

- `ls frontend/src/components/common/Pagination.tsx` → file exists
- `grep -c "onPageChange" frontend/src/components/common/Pagination.tsx` → >= 1
- `grep -c "PAGE_SIZE" frontend/src/pages/Agents.tsx` → 0 (ad-hoc removed)
- `grep -c "Pagination" frontend/src/pages/Agents.tsx` → >= 1 (uses shared)
- `grep -c "Pagination" frontend/src/components/TaskTable.tsx` → >= 1
- Visual check: Tasks page shows pagination controls, Agents page pagination unchanged behavior

## Plan

1. Create `frontend/src/components/common/` directory
2. Create `Pagination.tsx` with:
   - Props interface: `currentPage`, `totalPages`, `totalItems`, `pageSize`, `onPageChange(page)`, `onPageSizeChange?(size)`
   - UI: ChevronLeft/Right buttons, "Page X of Y (N items)" span, optional Select for page size
   - Styling: match existing gray-800/700 buttons from Agents.tsx
3. Update `TaskTable.tsx`:
   - Add `useState` for `currentPage` and `pageSize` (default 25)
   - Slice tasks array for current page
   - Render Pagination below table
4. Refactor `Agents.tsx`:
   - Remove `PAGE_SIZE` constant and inline pagination logic (lines ~139-146)
   - Remove ad-hoc pagination UI (lines ~288-309)
   - Import and use shared Pagination component
5. Test both pages visually

## Sub-tasks

- [ ] Create `frontend/src/components/common/Pagination.tsx`
- [ ] Integrate Pagination into `TaskTable.tsx` (client-side, 25 rows default)
- [ ] Refactor `Agents.tsx` to use shared Pagination
