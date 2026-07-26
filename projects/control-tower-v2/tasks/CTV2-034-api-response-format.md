---
id: CTV2-034
title: "Fix API response format - snake_case to camelCase"
status: done
priority: high
risk: low
deadline: 2026-07-28
executor: "@gpt-5.6-luna-high"
reviewer: "@gpt-5.6-sol"
files:
  - backend/app/api/stats.py
  - backend/app/api/tasks.py
  - backend/app/api/projects.py
  - frontend/src/pages/Dashboard.tsx
tests:
  - Dashboard displays real data from API
  - All API responses use camelCase
created: 2026-07-26
---

# CTV2-034: Fix API Response Format

## Problem

API returns snake_case but frontend expects camelCase:

| API returns | Frontend expects |
|-------------|------------------|
| `total_tasks` | `totalTasks` |
| `done_tasks` | `completedTasks` |
| `by_status` | `tasksByStatus` |
| `active_tasks` | `activeGates` |

## Solution Options

1. **Backend**: Add Pydantic `alias_generator` for camelCase output
2. **Frontend**: Transform snake_case → camelCase in API client

## AC

- [ ] AC1: `/api/stats/overview` returns camelCase fields
- [ ] AC2: Dashboard KPI cards show real numbers
- [ ] AC3: Status chart shows real distribution
