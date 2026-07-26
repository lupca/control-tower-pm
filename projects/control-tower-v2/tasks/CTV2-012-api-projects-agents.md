---
id: CTV2-012
title: "API endpoints for Projects & Agents"
status: done
priority: high
risk: low
executor: "@antigravity-3.6-high"
reviewer: "@gpt-5.6-sol"
done: 2026-07-26
deadline: 2026-07-28
created: 2026-07-26
updated: 2026-07-26
depends_on: [CTV2-011]
files:
  - backend/app/api/projects.py
  - backend/app/api/agents.py
  - backend/app/schemas/project.py
  - backend/app/schemas/agent.py
  - backend/app/main.py
tests:
  - GET /api/projects returns list
  - GET /api/projects/{id} returns detail with task count
  - GET /api/agents returns list with stats
  - CRUD operations work
---

# CTV2-012: API endpoints for Projects & Agents

## Acceptance Criteria
- [x] AC1: `GET /api/projects` trả về list projects với stats (task count by status)
- [x] AC2: `GET /api/projects/{id}` trả về project detail
- [x] AC3: `GET /api/projects/{id}/tasks` trả về tasks của project
- [x] AC4: `POST/PATCH /api/projects` CRUD operations
- [x] AC5: `GET /api/agents` trả về list agents với performance stats
- [x] AC6: `GET /api/agents/{id}` trả về agent detail
- [x] AC7: `POST/PATCH /api/agents` CRUD operations
- [x] AC8: Pydantic schemas cho request/response validation

## Technical Notes
- Follow existing pattern in `tasks.py`
- Include pagination for list endpoints
- Stats computed via SQL aggregation

