---
id: CTW-004
title: "Fix Gantt Timeline bị che không thao tác được"
status: in-review
priority: high
risk: low
deadline: 2026-07-25
executor: "@gpt-5.6-luna-high"
reviewer: "@gpt-5.6-sol"
result_ref: "504accb"
depends_on: []
files:
  - src/components/timeline/GanttChart.tsx
  - src/pages/timeline.astro
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

# CTW-004: Fix Gantt Timeline bị che không thao tác được

> Dự án: [[projects/control-tower-web/control-tower-web]]

## Problem

Project Schedule & Gantt Timeline page bị che, không thể thao tác được. User không interact được với timeline.

## Tiêu chí nghiệm thu (AC)

- [ ] Gantt chart hiển thị đầy đủ, không bị che
- [ ] Có thể hover/click vào các task bars
- [ ] Có thể scroll horizontal nếu timeline dài
- [ ] Responsive trên các kích thước màn hình

## Verification

- Mở `/timeline` trong browser
- Hover vào task bars → tooltip hiện
- Click vào task → có action (link hoặc modal)
- Resize browser → layout không bị vỡ

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] Check CSS overflow/z-index issues trong GanttChart.tsx
- [ ] Verify container sizing trong timeline.astro
- [ ] Test scroll behavior
- [ ] Fix layout issues
