---
id: CTW-008
title: "Fix dashboard data loading bugs"
status: done
priority: high
risk: normal
deadline: null
executor: "@gpt-5.6-luna-high"
reviewer: "@claude-sonnet-high"
result_ref: "fcd6e04"
depends_on: []
files:
  - src/pages/projects/[project].astro
  - src/components/kanban/KanbanBoard.tsx
  - src/lib/api.ts
flows: []
tests: []
dispatched: 2026-07-23
in_review: 2026-07-23
predicted_success: high
prediction_factors:
  score: 0.85
  deductions:
    - "no_tests: -0.1"
    - "ui_component: -0.05"
rejections: 0
created: 2026-07-23
updated: 2026-07-23
---

# CTW-008: Fix dashboard data loading bugs

> Dự án: [[projects/control-tower-web/control-tower-web]]

## Problem

3 bugs liên quan đến data loading trên dashboard:
1. **Project detail page**: Một số project (vd: PMI) không lấy được data
2. **Kanban board**: Không load được task của một số project
3. **Kanban column overflow**: Cột bị kéo dài khi có nhiều task — cần giới hạn chiều cao + scroll

## Tiêu chí nghiệm thu (AC)

- [x] **AC1:** Project detail page (`/projects/[project]`) hiển thị đúng data cho tất cả projects trong registry
- [x] **AC2:** Kanban board load được tasks của mọi project, không bị miss
- [x] **AC3:** Kanban columns có `max-height` + `overflow-y: auto` để scroll khi nhiều task

## Verification

```bash
# Start dev server
npm run dev

# Test in browser:
# 1. /projects/topvnsport-pmi — should show project data
# 2. /kanban — should show all tasks from all projects
# 3. Add 10+ tasks to one column — should scroll, not stretch page
```

## Plan

1. Debug project detail page (`/projects/[project].astro`) — check API call, file path resolution
2. Debug kanban data loading — check if all projects' tasks are fetched
3. Add CSS `max-height` + `overflow-y: auto` to kanban columns
4. Test all 3 fixes in browser
