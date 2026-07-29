---
id: CTV2-017
title: "Frontend - Task Table & Kanban views"
status: done
priority: high
risk: medium
executor: "@gemini-3.6-flash"
reviewer: "@gpt-5.6-sol"
deadline: 2026-07-29
created: 2026-07-26
updated: 2026-07-26
depends_on: [CTV2-015, CTV2-012]
files:
  - frontend/src/pages/Tasks.tsx
  - frontend/src/pages/Kanban.tsx
  - frontend/src/components/tasks/TaskTable.tsx
  - frontend/src/components/tasks/TaskFilters.tsx
  - frontend/src/components/kanban/KanbanBoard.tsx
  - frontend/src/components/kanban/KanbanColumn.tsx
  - frontend/src/components/kanban/KanbanCard.tsx
tests:
  - Task table loads with data
  - Filters work (project, status, executor)
  - Kanban drag-drop works
  - Status updates via API
---

# CTV2-017: Frontend Task Table & Kanban

## Reference
- control-tower-web `src/pages/tasks.astro`
- control-tower-web `src/pages/kanban.astro`

## Acceptance Criteria

### Task Table
- [ ] AC1: Table với columns: ID, Title, Status, Project, Executor, Reviewer, Updated
- [ ] AC2: Sortable columns
- [ ] AC3: Filter by: project, status, executor, search text
- [ ] AC4: Pagination
- [ ] AC5: Click row → navigate to task detail
- [ ] AC6: Chat button mở chat panel

### Kanban Board
- [ ] AC7: Columns: Todo, Dispatched, In Review, Changes Requested, Done
- [ ] AC8: Cards hiển thị: ID, Title, Project, Executor
- [ ] AC9: Drag-drop giữa columns → update status via API
- [ ] AC10: Filter by project
- [ ] AC11: Chat button on card

## Technical Notes
- Use @tanstack/react-table for table
- Use @hello-pangea/dnd for drag-drop (hoặc dnd-kit)
- Optimistic updates khi drag-drop
