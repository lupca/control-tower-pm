---
id: CTW-006
title: "Fix Task Completion hiện 0% sai data"
status: done
priority: high
risk: low
deadline: 2026-07-25
executor: "@gpt-5.6-luna-high"
reviewer: "@gpt-5.6-sol"
result_ref: "0ea54ae"
depends_on: []
files:
  - src/components/dashboard/StatusChart.tsx
  - src/lib/data.ts
flows: []
tests: []
dispatched: 2026-07-23
in_review: 2026-07-23
predicted_success: high
prediction_factors:
  score: 0.85
  deductions:
    - "no_tests: -0.1"
    - "data_logic: -0.05 (needs data source verification)"
created: 2026-07-23
updated: 2026-07-23
---

# CTW-006: Fix Task Completion hiện 0% sai data

> Dự án: [[projects/control-tower-web/control-tower-web]]

## Problem

Project Task Completion chart hiện 0%, tất cả task đều hiện "todo" dù thực tế có task đã done.

## Tiêu chí nghiệm thu (AC)

- [ ] Task completion % tính đúng từ data thực tế
- [ ] Chart hiển thị đúng tỷ lệ done/todo/in-progress
- [ ] Data sync với control-tower markdown files

## Verification

- Mở dashboard `/`
- Task Completion chart hiện % > 0 (nếu có task done)
- So sánh với `projects/*/tasks/*.md` thực tế

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] Check data loading logic trong data.ts
- [ ] Verify status parsing từ markdown frontmatter
- [ ] Fix StatusChart calculation
- [ ] Test với real data từ control-tower
