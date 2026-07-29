---
id: CTV2-122
title: "Parallelize API Calls (Promise.all)"
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
result_ref: e029f31
completed: 2026-07-28
depends_on: [CTV2-121]
files:
  - frontend/src/pages/ProjectDetail.tsx
  - frontend/src/pages/AgentDetail.tsx
  - frontend/src/pages/Dashboard.tsx
  - frontend/src/hooks/useDashboardStats.ts
flows: []
tests:
  - frontend/src/pages/__tests__/Dashboard.test.tsx
predicted_success: high
prediction_factors:
  score: 0.8
  deductions:
    - "touches hub nodes ProjectDetailPage/AgentDetailPage/Dashboard (-0.2)"
created: 2026-07-28
updated: 2026-07-28
---

# CTV2-122: Parallelize API Calls (Promise.all)

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

Phase 2/5 của [[CTV2-118-research-frontend-refactor-strategy]] — nguồn: `docs/research/frontend-refactor-strategy.md` §Performance Findings (N+1 / Sequential API Calls). Phụ thuộc [[CTV2-121-usememo-filtered-lists]] vì cùng sửa `ProjectDetail.tsx`/`AgentDetail.tsx`.

## Tiêu chí nghiệm thu (AC)

- [ ] `ProjectDetail.tsx:43-52`: gộp fetch project + tasks bằng `Promise.all([api.get('/projects/${id}'), api.get('/tasks?project=${id}')])`.
- [ ] `AgentDetail.tsx:42-60`: gộp fetch agent + stats + tasks bằng `Promise.all`.
- [ ] `Dashboard.tsx:88-105`: đưa fetch `projectStats` (hiện đang chạy riêng sau, dòng 101-105) vào chung `Promise.all` ban đầu với overview/projects/usage/comparison.
- [ ] Tạo hook `useDashboardStats.ts` (mới) để tách logic fetch của `Dashboard.tsx` ra khỏi component.
- [ ] Test `Dashboard.test.tsx` khẳng định: khi mount, tất cả API call (overview, projects, usage, comparison, projectStats) được gọi trong cùng 1 tick (không tuần tự) — mock `api.get` và kiểm tra call order/timing.

## Verification
- `npm test -- Dashboard` → pass
- Grep diff: không còn `await` tuần tự cho các fetch liệt kê ở AC (đều nằm trong `Promise.all`)

## Plan
1. `ProjectDetail.tsx`: gộp 2 fetch bằng `Promise.all`.
2. `AgentDetail.tsx`: gộp 3 fetch bằng `Promise.all`.
3. Tách `frontend/src/hooks/useDashboardStats.ts`, đưa toàn bộ fetch logic của `Dashboard.tsx` (bao gồm `projectStats`) vào 1 `Promise.all`.
4. Cập nhật `Dashboard.tsx` dùng hook mới.
5. Viết test `Dashboard.test.tsx` xác nhận các call chạy song song.
