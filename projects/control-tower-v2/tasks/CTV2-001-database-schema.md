---
id: CTV2-001
title: "Database Schema + Alembic Migrations"
status: done
priority: high
risk: low
deadline: 2026-08-05
executor: "@antigravity-3.6-high"
reviewer: "@antigravity"
result_ref: "f41e472"
depends_on: []
files:
  - backend/app/db/models.py
  - backend/app/db/base.py
  - backend/alembic/versions/001_initial.py
  - backend/alembic.ini
  - docker-compose.yml
flows: []
tests:
  - backend/tests/test_db.py
dispatched: 2026-07-26
in_review: 2026-07-26
predicted_success: high
prediction_factors:
  score: 0.85
  deductions:
    - "Greenfield project, no legacy constraints (+0.1)"
    - "Standard SQLAlchemy patterns (+0.0)"
created: 2026-07-26
updated: 2026-07-26
---

# CTV2-001: Database Schema + Alembic Migrations

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Tiêu chí nghiệm thu (AC)

- [x] PostgreSQL container chạy trong docker-compose
- [x] SQLAlchemy models cho: `tasks`, `sessions`, `audit_log`
- [x] Alembic migration `001_initial.py` tạo tất cả tables
- [x] `alembic upgrade head` chạy thành công
- [x] `alembic downgrade -1` rollback được
- [x] Connection pooling configured (pool_size=5, max_overflow=10)
- [x] Test: insert/query task hoạt động

## Schema

```sql
-- Tasks
CREATE TABLE tasks (
    id VARCHAR(20) PRIMARY KEY,
    project VARCHAR(50) NOT NULL,
    title TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'todo',
    priority VARCHAR(10),
    risk VARCHAR(10),
    executor VARCHAR(50),
    reviewer VARCHAR(50),
    acceptance_criteria JSONB DEFAULT '[]',
    files JSONB DEFAULT '[]',
    tests JSONB DEFAULT '[]',
    flows JSONB DEFAULT '[]',
    plan TEXT,
    result_ref VARCHAR(100),
    findings JSONB DEFAULT '[]',
    verdict VARCHAR(10),
    predicted_success VARCHAR(10),
    prediction_factors JSONB,
    deadline DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    dispatched_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Sessions (LangGraph + Chat)
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id VARCHAR(20) REFERENCES tasks(id),
    thread_id VARCHAR(100),
    current_gate VARCHAR(20),
    messages JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Audit log
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(20),
    action VARCHAR(50) NOT NULL,
    actor VARCHAR(50),
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_project ON tasks(project);
CREATE INDEX idx_sessions_task ON sessions(task_id);
CREATE INDEX idx_audit_task ON audit_log(task_id);
```

## Plan

1. Setup docker-compose với PostgreSQL 16
2. Tạo `backend/app/db/base.py` với engine + sessionmaker
3. Tạo `backend/app/db/models.py` với SQLAlchemy models
4. Init Alembic: `alembic init alembic`
5. Tạo migration: `alembic revision --autogenerate -m "initial"`
6. Test migration up/down
7. Viết basic CRUD test

## Verification

```bash
docker-compose up -d db
alembic upgrade head
python -c "from app.db import engine; print(engine.execute('SELECT 1').scalar())"
pytest backend/tests/test_db.py -v
```
