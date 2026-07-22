---
id: CTW-005
title: "Fix Knowledge Base không click xem chi tiết được"
status: done
priority: high
risk: low
deadline: 2026-07-25
executor: "@gpt-5.6-luna-high"
reviewer: "@gpt-5.6-sol"
result_ref: "98523be"
depends_on: []
files:
  - src/pages/knowledge/index.astro
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

# CTW-005: Fix Knowledge Base không click xem chi tiết được

> Dự án: [[projects/control-tower-web/control-tower-web]]

## Problem

Knowledge Base & ADR Index đang có mấy items nhưng không bấm xem chi tiết được. Links không hoạt động hoặc không có.

## Tiêu chí nghiệm thu (AC)

- [ ] Mỗi knowledge item có link clickable
- [ ] Click vào item → navigate đến detail page hoặc mở modal
- [ ] Hiển thị nội dung chi tiết của ADR/knowledge file

## Verification

- Mở `/knowledge` trong browser
- Click vào một ADR item → xem được nội dung
- Back button hoạt động

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] Check current link implementation trong index.astro
- [ ] Add detail page routing hoặc modal component
- [ ] Implement knowledge content rendering
- [ ] Test navigation flow
