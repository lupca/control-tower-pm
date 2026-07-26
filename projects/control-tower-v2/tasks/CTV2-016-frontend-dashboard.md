---
id: CTV2-016
title: "Frontend - Dashboard page with KPIs"
status: todo
priority: high
risk: low
executor:
reviewer:
deadline: 2026-07-29
created: 2026-07-26
updated: 2026-07-26
depends_on: [CTV2-015, CTV2-013]
files:
  - frontend/src/pages/Dashboard.tsx
  - frontend/src/components/dashboard/KpiCards.tsx
  - frontend/src/components/dashboard/StatusChart.tsx
  - frontend/src/components/dashboard/ProjectCards.tsx
  - frontend/src/components/dashboard/RecentActivity.tsx
tests:
  - Dashboard loads with KPI data
  - Charts render correctly
  - Project cards show progress
---

# CTV2-016: Frontend Dashboard

## Reference
Lấy design từ control-tower-web `src/pages/index.astro`

## Acceptance Criteria
- [ ] AC1: KPI Cards hiển thị: Total Tasks, Done, Active, High Risk
- [ ] AC2: Status Chart (pie/donut) hiển thị task distribution
- [ ] AC3: Project Cards với progress bar và stats
- [ ] AC4: Recent Activity list (từ audit_log)
- [ ] AC5: Responsive layout (mobile-friendly)
- [ ] AC6: Dark theme matching control-tower-web style
- [ ] AC7: Data từ `/api/stats/overview` và `/api/stats/projects`

## Components
```tsx
<Dashboard>
  <KpiCards stats={stats} />
  <div className="grid grid-cols-2 gap-6">
    <StatusChart data={statusCounts} />
    <ProjectCards projects={projects} />
  </div>
  <RecentActivity entries={auditLog} />
</Dashboard>
```
