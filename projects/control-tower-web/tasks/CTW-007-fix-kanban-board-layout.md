---
id: CTW-007
title: "Fix Kanban Board bảng bé che hết task"
status: done
priority: high
risk: low
deadline: 2026-07-25
executor: "@gpt-5.6-luna-high"
reviewer: "@gpt-5.6-sol"
result_ref: "98523be"
depends_on: []
files:
  - src/components/kanban/KanbanBoard.tsx
  - src/pages/kanban.astro
flows: []
tests: []
dispatched: 2026-07-23
in_review: 2026-07-23
predicted_success: high
prediction_factors:
  score: 0.85
  deductions:
    - "no_tests: -0.1"
    - "ui_component: -0.05 (visual verification needed)"
created: 2026-07-23
updated: 2026-07-23
---

# CTW-007: Fix Kanban Board bảng bé che hết task

> Dự án: [[projects/control-tower-web/control-tower-web]]

## Problem

Task Kanban Board bảng bé, che hết cả task. Các mục (columns) lớn rúm hết lại với nhau, không xem được nội dung task.

## Tiêu chí nghiệm thu (AC)

- [ ] Kanban columns có width hợp lý, không bị rúm
- [ ] Task cards hiển thị đầy đủ title + status
- [ ] Có thể scroll horizontal nếu nhiều columns
- [ ] Responsive layout cho các screen sizes

## Verification

- Mở `/kanban` trong browser
- Các columns (todo, ready, dispatched, in-review, done) hiển thị rõ ràng
- Task cards đọc được nội dung
- Drag & drop hoạt động (nếu có)

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] Check CSS grid/flex layout trong KanbanBoard.tsx
- [ ] Fix column min-width và card sizing
- [ ] Add horizontal scroll container
- [ ] Test với nhiều tasks
