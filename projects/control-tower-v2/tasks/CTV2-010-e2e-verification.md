---
id: CTV2-010
title: "E2E Verification - Run and Test Full Stack"
status: in-review
priority: high
risk: medium
deadline: 2026-07-27
executor: "@coordinator"
reviewer: "@coordinator"
result_ref: "01d4a08"
depends_on:
  - CTV2-001
  - CTV2-002
  - CTV2-003
  - CTV2-004
  - CTV2-005
  - CTV2-006
  - CTV2-007
  - CTV2-008
  - CTV2-009
files:
  - docker-compose.yml
  - backend/
  - frontend/
flows: []
tests:
  - backend/tests/
dispatched: null
in_review: null
predicted_success: medium
prediction_factors:
  score: 0.7
  deductions:
    - "First real run, may have issues (-0.2)"
    - "Dependencies may conflict (-0.1)"
created: 2026-07-26
updated: 2026-07-26
---

# CTV2-010: E2E Verification - Run and Test Full Stack

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Tiêu chí nghiệm thu (AC)

### Setup
- [ ] `docker-compose up --build` runs without errors
- [ ] All 4 containers healthy (db, backend, chat, dashboard)
- [ ] Database migrations applied successfully

### Backend API
- [ ] `GET /health` returns `{"status": "ok"}`
- [ ] `POST /api/tasks` creates a task
- [ ] `GET /api/tasks` returns task list
- [ ] `GET /api/tasks/{id}` returns task detail

### Unit Tests
- [ ] `pytest backend/tests/` passes
- [ ] All gate tests pass
- [ ] Four-eyes test passes

### Frontend
- [ ] Chat UI loads at :8081
- [ ] Dashboard loads at :8502
- [ ] Dashboard shows tasks from API

### LangGraph
- [ ] Graph builds without error
- [ ] State transitions work

## Verification Steps

```bash
# 1. Build and run
cd /home/lupca/projects/control-tower-v2
docker-compose up --build -d

# 2. Wait for healthy
docker-compose ps

# 3. Test API
curl http://localhost:8001/health
curl http://localhost:8001/api/tasks

# 4. Run unit tests
docker-compose exec backend pytest tests/ -v

# 5. Check frontends
curl -I http://localhost:8081
curl -I http://localhost:8502
```

## Plan

1. Start docker-compose
2. Verify all containers healthy
3. Test API endpoints
4. Run pytest
5. Check frontend accessibility
6. Document any issues found
