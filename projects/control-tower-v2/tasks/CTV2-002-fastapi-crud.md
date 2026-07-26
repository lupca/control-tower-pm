---
id: CTV2-002
title: "FastAPI CRUD + Pydantic Schemas"
status: done
priority: high
risk: low
deadline: 2026-08-07
executor: "@antigravity-3.6-high"
reviewer: "@antigravity"
result_ref: "f41e472"
depends_on:
  - CTV2-001
files:
  - backend/app/main.py
  - backend/app/api/tasks.py
  - backend/app/api/sessions.py
  - backend/app/api/audit.py
  - backend/app/schemas/task.py
  - backend/app/schemas/session.py
flows: []
tests:
  - backend/tests/test_api_tasks.py
  - backend/tests/test_api_sessions.py
dispatched: 2026-07-26
in_review: 2026-07-26
predicted_success: high
prediction_factors:
  score: 0.85
  deductions:
    - "Standard FastAPI patterns (+0.0)"
created: 2026-07-26
updated: 2026-07-26
---

# CTV2-002: FastAPI CRUD + Pydantic Schemas

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Tiêu chí nghiệm thu (AC)

- [x] FastAPI app với `/health` endpoint
- [x] Pydantic schemas cho Task, Session, AuditLog
- [x] CRUD endpoints: `/api/tasks` (GET, POST, GET/:id, PATCH/:id)
- [x] CRUD endpoints: `/api/sessions` (GET, POST, GET/:id)
- [x] Query filters: `?status=todo&project=web`
- [x] Pagination: `?limit=20&offset=0`
- [x] Auto audit log on task mutations
- [x] OpenAPI docs at `/docs`
- [x] Tests pass với TestClient

## Endpoints

```
GET    /health                    → {"status": "ok"}
GET    /api/tasks                 → [Task]
POST   /api/tasks                 → Task
GET    /api/tasks/{id}            → Task
PATCH  /api/tasks/{id}            → Task
GET    /api/tasks/{id}/history    → [AuditLog]

GET    /api/sessions              → [Session]
POST   /api/sessions              → Session
GET    /api/sessions/{id}         → Session
PATCH  /api/sessions/{id}         → Session

GET    /api/audit                 → [AuditLog]
```

## Pydantic Schemas

```python
class TaskCreate(BaseModel):
    project: str
    title: str
    priority: str | None = None
    deadline: date | None = None

class TaskUpdate(BaseModel):
    status: str | None = None
    executor: str | None = None
    reviewer: str | None = None
    acceptance_criteria: list[str] | None = None
    plan: str | None = None
    result_ref: str | None = None
    verdict: str | None = None

class Task(BaseModel):
    id: str
    project: str
    title: str
    status: str
    # ... all fields
    
    class Config:
        from_attributes = True
```

## Plan

1. Tạo Pydantic schemas trong `app/schemas/`
2. Tạo FastAPI routers trong `app/api/`
3. Implement dependency injection cho DB session
4. Auto-generate task ID từ project prefix + sequence
5. Add audit log middleware/dependency
6. Write tests với pytest + httpx

## Verification

```bash
uvicorn app.main:app --reload
curl localhost:8000/health
curl localhost:8000/docs  # OpenAPI
pytest backend/tests/test_api_*.py -v
```
