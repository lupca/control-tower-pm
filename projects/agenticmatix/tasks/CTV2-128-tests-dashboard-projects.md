---
id: CTV2-128
title: "Add Tests for Dashboard and Projects Pages"
repo_root: /home/lupca/projects/control-tower-v2
status: todo
priority: normal
risk: normal
deadline: null
executor: "@gemini-3.6-flash"
reviewer: null
result_ref: null
depends_on: [CTV2-126, CTV2-127]
files:
  - frontend/src/pages/__tests__/Dashboard.test.tsx
  - frontend/src/pages/__tests__/Projects.test.tsx
  - frontend/src/pages/__tests__/ProjectDetail.test.tsx
  - frontend/src/test/mocks/handlers.ts
flows: []
tests:
  - frontend/src/pages/__tests__/Dashboard.test.tsx
  - frontend/src/pages/__tests__/ProjectDetail.test.tsx
predicted_success: high
prediction_factors:
  score: 1.0
  deductions: []
created: 2026-07-28
updated: 2026-07-28
---

# CTV2-128: Add Tests for Dashboard and Projects Pages

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

Phase 5/5 của [[CTV2-118-research-frontend-refactor-strategy]] — nguồn: `docs/research/frontend-refactor-strategy.md` §Test Coverage Recommendations (`Dashboard`/`ProjectsPage`/`ProjectDetailPage` — 0 test hiện tại per `get_knowledge_gaps_tool`). Chạy sau khi UI đã ổn định (CTV2-126/127) để test không phải viết lại do migrate component.

## Tiêu chí nghiệm thu (AC)

- [ ] `Dashboard.test.tsx`: mock API bằng MSW (`test/mocks/handlers.ts`), khẳng định render đúng KPI cards + token telemetry section, và hiển thị banner lỗi khi API fail (case từ CTV2-120/122).
- [ ] `Projects.test.tsx`: khẳng định filter/search hoạt động đúng (case từ CTV2-121), modal tạo project mở/đóng đúng (case từ CTV2-127).
- [ ] `ProjectDetail.test.tsx`: bổ sung case tích hợp — render đủ `ProjectHeader`/`ProjectKpiCards`/`ProjectTaskList` (từ CTV2-125) với dữ liệu mock.
- [ ] `test/mocks/handlers.ts` thêm MSW handler cho `/api/stats/overview`, `/api/projects`, `/api/tasks`.

## Verification
- `npm test -- Dashboard Projects ProjectDetail` → pass, coverage report cho thấy 3 page trên không còn 0%.

## Plan
1. Thêm MSW handlers cần thiết vào `test/mocks/handlers.ts`.
2. Viết `Dashboard.test.tsx` theo React Testing Library, tập trung interaction + integration, không test implementation detail.
3. Viết `Projects.test.tsx`.
4. Bổ sung `ProjectDetail.test.tsx`.
