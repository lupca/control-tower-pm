---
id: CTV2-038
title: "Frontend: Dashboard Real Data + Auto-refresh"
status: todo
priority: high
risk: low
deadline: 2026-07-30
executor:
reviewer:
depends_on: [CTV2-034]
files:
  - frontend/src/pages/Dashboard.tsx
  - frontend/src/components/dashboard/KpiCards.tsx
  - frontend/src/components/dashboard/StatusChart.tsx
  - frontend/src/components/dashboard/ActiveRuns.tsx
  - backend/app/api/stats.py
tests:
  - KPI cards show real numbers from API
  - Status chart reflects actual distribution
  - Active runs section shows running agents
  - Auto-refresh every 30s
created: 2026-07-26
effort: 7h
---

# CTV2-038: Dashboard Real Data

> Phase 3 từ Frontend Strategy (CTV2-035)

## Scope

Fix Dashboard để hiển thị real data + thêm active runs section.

## Changes

### 1. Backend: Align API response
```python
# backend/app/api/stats.py
# Đảm bảo response format match frontend expectations
# Hoặc add Pydantic alias_generator cho camelCase
```

### 2. KpiCards - wire real data
```typescript
// Map API fields correctly:
// total_tasks → totalTasks
// done_tasks → completedTasks  
// by_status.dispatched → activeGates
```

### 3. StatusChart - real distribution
```typescript
// Use by_status từ API
// Pie chart với actual counts
```

### 4. ActiveRuns section (new)
```typescript
// frontend/src/components/dashboard/ActiveRuns.tsx
- Fetch GET /api/runs?status=running
- Show list of active agent runs
- Link to TaskDetail
- SSE subscribe for live updates
```

### 5. Auto-refresh
```typescript
// Poll every 30s or SSE for updates
// Visual indicator khi refreshing
```

## AC

- [ ] AC1: KPI cards show real numbers
- [ ] AC2: Status chart shows real distribution
- [ ] AC3: ActiveRuns shows running agents
- [ ] AC4: Auto-refresh every 30s
- [ ] AC5: Loading states đúng

## API Changes Needed

- Align `GET /api/stats/overview` response format
- Add `GET /api/runs?status=running` endpoint
