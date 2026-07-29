---
id: CTV2-040
title: "Frontend: Verdict Flow + Task Timeline"
status: todo
priority: medium
risk: low
deadline: 2026-07-31
executor:
reviewer:
depends_on: [CTV2-037]
files:
  - frontend/src/components/task/VerdictPanel.tsx
  - frontend/src/components/task/TaskTimeline.tsx
  - frontend/src/pages/TaskDetail.tsx
tests:
  - Verdict panel shows for in-review tasks
  - Pass/Changes buttons work
  - Timeline shows task history
  - Four-eyes validation (reviewer ≠ executor)
created: 2026-07-26
effort: 6h
---

# CTV2-040: Verdict Flow

> Phase 5 từ Frontend Strategy (CTV2-035)

## Scope

UI cho review verdict + task history timeline.

## Components

### 1. VerdictPanel
```typescript
// frontend/src/components/task/VerdictPanel.tsx
// Shows when task.status === 'in-review'
// - Pass button (green)
// - Changes Requested button (orange)
// - Comment textarea
// - Four-eyes warning if user === executor
```

### 2. TaskTimeline
```typescript
// frontend/src/components/task/TaskTimeline.tsx
// Vertical timeline showing:
// - Created
// - Dispatched (with agent)
// - Review started
// - Verdict (pass/changes)
// - Done
```

### 3. TaskDetail Integration
```typescript
// Add VerdictPanel khi in-review
// Add TaskTimeline section
// Wire POST /api/tasks/{id}/verdict
```

## AC

- [ ] AC1: VerdictPanel appears for in-review tasks
- [ ] AC2: Pass button calls POST /api/verdict pass
- [ ] AC3: Changes button calls POST /api/verdict changes
- [ ] AC4: TaskTimeline shows history
- [ ] AC5: Four-eyes warning displayed
- [ ] AC6: Task refreshes after verdict

## API

- `POST /api/tasks/{id}/verdict` - submit verdict
- `GET /api/tasks/{id}/history` - timeline data (cần thêm)
