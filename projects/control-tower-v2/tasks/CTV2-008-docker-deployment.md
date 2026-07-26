---
id: CTV2-008
title: "Docker Compose + Deployment"
status: done
priority: high
risk: low
deadline: 2026-08-20
executor: "@antigravity-3.6-high"
reviewer: "@antigravity"
result_ref: "f41e472"
depends_on:
  - CTV2-001
  - CTV2-002
  - CTV2-006
  - CTV2-007
files:
  - docker-compose.yml
  - backend/Dockerfile
  - frontend/chat/Dockerfile
  - frontend/dashboard/Dockerfile
  - .env.example
  - scripts/deploy.sh
flows: []
tests: []
dispatched: 2026-07-26
in_review: 2026-07-26
predicted_success: high
prediction_factors:
  score: 0.85
  deductions:
    - "Standard Docker patterns (+0.05)"
created: 2026-07-26
updated: 2026-07-26
---

# CTV2-008: Docker Compose + Deployment

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Tiêu chí nghiệm thu (AC)

- [x] `docker-compose up` starts all services
- [x] Services: db, backend, chat, dashboard
- [x] Health checks cho tất cả services
- [x] Volume mounts cho DB persistence
- [x] Environment variables từ .env
- [x] `docker-compose down -v` clean shutdown
- [x] README với deployment instructions

## docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: control_tower
      POSTGRES_USER: ct
      POSTGRES_PASSWORD: ${DB_PASSWORD:-secret}
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ct -d control_tower"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://ct:${DB_PASSWORD:-secret}@db/control_tower
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  chat:
    build: ./frontend/chat
    environment:
      BACKEND_URL: http://backend:8000
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
    ports:
      - "8080:8080"
    depends_on:
      - backend

  dashboard:
    build: ./frontend/dashboard
    environment:
      BACKEND_URL: http://backend:8000
    ports:
      - "8501:8501"
    depends_on:
      - backend

volumes:
  pgdata:
```

## .env.example

```bash
# Database
DB_PASSWORD=your_secure_password

# Claude API
ANTHROPIC_API_KEY=sk-ant-...

# Optional
LOG_LEVEL=INFO
```

## Backend Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run migrations on startup
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

## Plan

1. Tạo Dockerfiles cho backend, chat, dashboard
2. Tạo docker-compose.yml với health checks
3. Tạo .env.example
4. Test `docker-compose up --build`
5. Verify all services healthy
6. Document trong README

## Verification

```bash
docker-compose up --build -d
docker-compose ps  # all healthy
curl localhost:8000/health
curl localhost:8080  # chat UI
curl localhost:8501  # dashboard
docker-compose down -v
```
