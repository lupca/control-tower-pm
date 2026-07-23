---
id: CTW-011
title: "Add task detail & agent detail pages"
status: done
priority: high
risk: normal
deadline: null
executor: "@gpt-5.6-luna-high"
reviewer: "@claude-sonnet-high"
result_ref: "59aab72"
depends_on: []
files:
  - src/pages/task/[id].astro
  - src/pages/agent/[id].astro
flows: []
tests: []
dispatched: 2026-07-23
in_review: 2026-07-24
predicted_success: high
prediction_factors:
  score: 0.85
  deductions:
    - "no_tests: -0.1"
    - "new_pages: -0.05"
rejections: 0
created: 2026-07-23
updated: 2026-07-23
---

# CTW-011: Add task detail & agent detail pages

> Dự án: [[projects/control-tower-web/control-tower-web]]

## Problem

Chưa có trang chi tiết cho task và agent. Click vào task/agent trên dashboard không đi đâu cả.

## Tiêu chí nghiệm thu (AC)

- [x] **AC1:** `/task/[id]` page hiển thị đầy đủ task info: title, status, AC list, executor, reviewer, plan, dates
- [x] **AC2:** `/agent/[id]` page hiển thị agent profile: stats, strengths, task history, performance chart
- [x] **AC3:** Links từ Kanban/Agent Roster dẫn đến detail pages

## Plan

1. Create `/task/[id].astro` - read task markdown, render full content
2. Create `/agent/[id].astro` - read agent profile, show stats + history
3. Update KanbanBoard task cards to link to `/task/[id]`
4. Update AgentRoster to link to `/agent/[id]`
