---
id: CTW-010
title: "Kanban Board - collapsible columns"
status: done
priority: medium
risk: normal
deadline: null
executor: "@gpt-5.6-luna-high"
reviewer: "@claude-sonnet-high"
result_ref: "9b5205a"
depends_on: []
files:
  - src/components/kanban/KanbanBoard.tsx
flows: []
tests: []
dispatched: 2026-07-23
in_review: 2026-07-24
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

# CTW-010: Kanban Board - collapsible columns

> Dự án: [[projects/control-tower-web/control-tower-web]]

## Problem

Kanban board có nhiều columns (todo, ready, dispatched, in-review, done...) phải kéo ngang nhiều. User muốn thu gọn (collapse) những columns không cần nhìn.

## Tiêu chí nghiệm thu (AC)

- [x] **AC1:** Mỗi column có nút collapse/expand (icon chevron hoặc minus/plus)
- [x] **AC2:** Column collapsed chỉ hiện header + task count, không hiện task cards
- [x] **AC3:** State collapse persist trong localStorage (reload page vẫn giữ)

## Plan

1. Add collapse state per column (useState or localStorage)
2. Add collapse button to column header
3. When collapsed: hide task list, show only header + count badge
4. Save/load state from localStorage
