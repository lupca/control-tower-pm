---
id: CTV2-013
title: "API endpoints for Knowledge & Stats"
status: todo
priority: high
risk: low
executor:
reviewer:
deadline: 2026-07-28
created: 2026-07-26
updated: 2026-07-26
depends_on: [CTV2-011]
files:
  - backend/app/api/knowledge.py
  - backend/app/api/stats.py
  - backend/app/schemas/knowledge.py
  - backend/app/schemas/stats.py
  - backend/app/main.py
tests:
  - GET /api/knowledge returns filtered list
  - GET /api/stats/overview returns KPIs
  - GET /api/stats/projects returns per-project breakdown
---

# CTV2-013: API endpoints for Knowledge & Stats

## Acceptance Criteria
- [ ] AC1: `GET /api/knowledge` với filter by type
- [ ] AC2: `GET /api/knowledge/{slug}` trả về content
- [ ] AC3: `POST/PATCH /api/knowledge` CRUD
- [ ] AC4: `GET /api/stats/overview` trả về:
  - Total tasks, done, active, by status
  - Total projects, active projects
  - Total agents
- [ ] AC5: `GET /api/stats/projects` trả về per-project:
  - Task count by status
  - Completion rate
  - Active executor/reviewer
- [ ] AC6: `GET /api/stats/agents` trả về:
  - Tasks executed/reviewed
  - Success rate
  - Recent activity

## Technical Notes
- Stats endpoints use SQL aggregation, not iteration
- Cache stats với TTL nếu cần performance
