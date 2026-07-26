---
id: CTV2-015
title: "Frontend setup - React + Vite + Tailwind"
status: todo
priority: high
risk: low
executor:
reviewer:
deadline: 2026-07-29
created: 2026-07-26
updated: 2026-07-26
files:
  - frontend/package.json
  - frontend/vite.config.ts
  - frontend/tailwind.config.js
  - frontend/src/main.tsx
  - frontend/src/App.tsx
  - frontend/Dockerfile
tests:
  - npm run dev starts successfully
  - Tailwind styles work
  - API proxy to backend works
  - Docker build succeeds
---

# CTV2-015: Frontend Setup

## Context
Setup React frontend thay thế Streamlit dashboard + Chainlit chat.

## Tech Stack
- React 19 + TypeScript
- Vite (build tool)
- TailwindCSS (styling)
- React Router (routing)
- React Query (data fetching)
- Zustand (state management)

## Acceptance Criteria
- [ ] AC1: Vite project với React 19 + TypeScript
- [ ] AC2: TailwindCSS configured với dark mode
- [ ] AC3: React Router với routes: /, /tasks, /kanban, /task/:id, /projects, /agents
- [ ] AC4: React Query setup với API client
- [ ] AC5: Zustand store cho global state (user preferences, open panels)
- [ ] AC6: Dockerfile cho production build
- [ ] AC7: Vite proxy `/api` → `http://backend:8000`

## Structure
```
frontend/
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── routes.tsx
│   ├── components/
│   │   └── shared/
│   │       └── Layout.tsx
│   ├── lib/
│   │   ├── api.ts
│   │   └── store.ts
│   └── styles/
│       └── globals.css
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
└── Dockerfile
```
