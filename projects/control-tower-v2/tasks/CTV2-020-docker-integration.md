---
id: CTV2-020
title: "Docker Compose update & Integration"
status: todo
priority: high
risk: medium
executor:
reviewer:
deadline: 2026-07-30
created: 2026-07-26
updated: 2026-07-26
depends_on: [CTV2-015, CTV2-011]
files:
  - docker-compose.yml
  - frontend/Dockerfile
  - frontend/nginx.conf
  - .env.example
tests:
  - docker compose up starts all services
  - Frontend accessible at port 3000
  - API proxy works
  - Hot reload works in dev mode
---

# CTV2-020: Docker Compose Integration

## Context
Update docker-compose để:
1. Bỏ Chainlit (chat integrated vào frontend)
2. Thay Streamlit bằng React frontend
3. Single unified web interface

## Target Architecture
```
┌─────────────────────────────────────────────────┐
│                 docker-compose                   │
├─────────────────────────────────────────────────┤
│  ┌─────────┐  ┌──────────┐  ┌───────────────┐  │
│  │   db    │  │ backend  │  │   frontend    │  │
│  │ :5432   │  │  :8000   │  │    :3000      │  │
│  │ postgres│  │ FastAPI  │  │ React + Nginx │  │
│  └─────────┘  └──────────┘  └───────────────┘  │
└─────────────────────────────────────────────────┘
```

## Acceptance Criteria
- [ ] AC1: Remove `chat` service (Chainlit)
- [ ] AC2: Remove `dashboard` service (Streamlit)
- [ ] AC3: Add `frontend` service với:
  - Nginx serving React build
  - Proxy `/api` → backend:8000
- [ ] AC4: Dev mode với hot reload (vite dev server)
- [ ] AC5: `.env.example` với all variables
- [ ] AC6: Health checks cho tất cả services
- [ ] AC7: Volume mounts cho development

## docker-compose.yml
```yaml
services:
  db:
    image: postgres:16-alpine
    ports: ["5433:5432"]
    
  backend:
    build: ./backend
    ports: ["8001:8000"]
    depends_on: [db]
    
  frontend:
    build: ./frontend
    ports: ["3000:80"]
    depends_on: [backend]
```
