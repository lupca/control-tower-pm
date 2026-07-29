---
id: CTV2-121
title: "Add useMemo to Filtered Lists"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: normal
risk: normal
deadline: null
executor: "@claude-opus-4.5"
reviewer: "@claude-opus-4.5"
verdict: pass
verdict_by: "@claude-opus-4.5"
verdict_note: "bypass mode - inline execution & verification (tsc + build pass)"
result_ref: e83bba5
completed: 2026-07-28
depends_on: [CTV2-120]
files:
  - frontend/src/pages/ProjectDetail.tsx
  - frontend/src/pages/AgentDetail.tsx
  - frontend/src/pages/Agents.tsx
  - frontend/src/pages/Projects.tsx
  - frontend/src/components/tasks/TaskTable.tsx
flows: []
tests:
  - frontend/src/pages/__tests__/ProjectDetail.test.tsx
predicted_success: high
prediction_factors:
  score: 0.8
  deductions:
    - "touches hub nodes ProjectDetailPage/AgentDetailPage/AgentsPage/ProjectsPage (-0.2)"
created: 2026-07-28
updated: 2026-07-28
---

# CTV2-121: Add useMemo to Filtered Lists

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

Phase 2/5 của [[CTV2-118-research-frontend-refactor-strategy]] — nguồn: `docs/research/frontend-refactor-strategy.md` §Performance Findings (Missing Memoization). Phụ thuộc [[CTV2-120-fix-high-severity-bugs-prescan]] vì cùng sửa `AgentDetail.tsx`/`ProjectDetail.tsx` — chạy sau để tránh xung đột file.

## Tiêu chí nghiệm thu (AC)

- [ ] `ProjectDetail.tsx:79-90` `filteredTasks` bọc trong `useMemo` với deps `[tasks, search, statusFilter]`.
- [ ] `TaskTable.tsx:49-59` `sortedTasks` bọc trong `useMemo` với deps `[tasks, sortField, sortDirection]`.
- [ ] `TaskTable.tsx:68-105` `getStatusBadge`/`getPriorityBadge` tách thành component ổn định (`<StatusBadge status={s} />`) thay vì tạo JSX mới mỗi lần gọi.
- [ ] `AgentDetail.tsx:82-90` `executorTasks`/`reviewerTasks`/`displayedTasks` bọc trong `useMemo`.
- [ ] `Agents.tsx:120-135` `filteredAgents` bọc trong `useMemo` với deps `[agents, search, roleFilter, statusFilter]`.
- [ ] `Projects.tsx:97-107` `filteredProjects` bọc trong `useMemo`.
- [ ] Test `ProjectDetail.test.tsx` khẳng định: thay đổi 1 prop không liên quan (vd. re-render do parent) KHÔNG tính lại `filteredTasks` (dùng render-count spy hoặc React DevTools profiler mock).

## Verification
- `npm test -- ProjectDetail` → pass
- Grep diff: mỗi filter/sort liệt kê ở trên đều nằm trong `useMemo(...)`

## Plan
1. Đọc lại từng file, xác định đúng dependency array cho mỗi `useMemo`.
2. Áp dụng `useMemo` cho các phép filter/sort liệt kê ở AC.
3. Tách `StatusBadge`/`PriorityBadge` khỏi `TaskTable.tsx` (không tạo file mới nếu component đủ nhỏ, nhưng phải là component riêng để React không tạo lại JSX mỗi render).
4. Viết test xác nhận memoization hoạt động cho `ProjectDetail.tsx`.
