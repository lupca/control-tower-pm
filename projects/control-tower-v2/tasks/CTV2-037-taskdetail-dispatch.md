---
id: CTV2-037
title: "Frontend: TaskDetail Dispatch + Run History"
status: todo
priority: critical
risk: low
deadline: 2026-07-29
executor:
reviewer:
depends_on: [CTV2-036]
files:
  - frontend/src/pages/TaskDetail.tsx
  - frontend/src/components/task/DispatchButton.tsx
  - frontend/src/components/task/RunHistory.tsx
  - frontend/src/components/task/RunCard.tsx
tests:
  - Dispatch button triggers POST /api/dispatch
  - Run history loads from API
  - AgentOutputViewer embedded in RunCard
  - New run appears in history after dispatch
created: 2026-07-26
effort: 4h
---

# CTV2-037: TaskDetail Dispatch Integration

> Phase 2 từ Frontend Strategy (CTV2-035)

## Scope

Wire dispatch button + show run history trong TaskDetail page.

## Components

### 1. DispatchButton
```typescript
// frontend/src/components/task/DispatchButton.tsx
- Select agent từ dropdown
- POST /api/dispatch
- Show loading state
- Toast on success/error
```

### 2. RunHistory
```typescript
// frontend/src/components/task/RunHistory.tsx
- Fetch GET /api/tasks/{id}/runs
- List RunCard components
- Most recent first
```

### 3. RunCard
```typescript
// frontend/src/components/task/RunCard.tsx
- RunStatusBadge
- Agent name, timestamp
- Expandable AgentOutputViewer
- Cancel button (if running)
```

### 4. TaskDetail Integration
```typescript
// Update TaskDetail.tsx
- Add DispatchButton in header
- Add RunHistory section
- Auto-refresh on dispatch
```

## AC

- [ ] AC1: DispatchButton triggers real dispatch
- [ ] AC2: RunHistory shows all runs for task
- [ ] AC3: RunCard expandable với AgentOutputViewer
- [ ] AC4: Toast notifications cho success/error
- [ ] AC5: Cancel button works cho running tasks

## API Endpoints

- `POST /api/dispatch` - trigger run
- `GET /api/tasks/{id}/runs` - list runs (cần thêm)
- `POST /api/runs/{id}/cancel` - cancel run
