---
id: CTW-012
title: "Knowledge Base load full tree + folder categorization"
status: done
priority: medium
risk: normal
deadline: null
executor: "@gpt-5.6-luna-high"
reviewer: "@claude-sonnet-high"
result_ref: "79fae6e"
depends_on: []
files:
  - src/components/KnowledgeBase.tsx
  - src/lib/data.ts
flows: []
tests: []
dispatched: 2026-07-23
in_review: 2026-07-24
predicted_success: high
prediction_factors:
  score: 0.85
  deductions:
    - "no_tests: -0.1"
    - "recursive_fs: -0.05"
rejections: 0
created: 2026-07-23
updated: 2026-07-23
---

# CTW-012: Knowledge Base load full tree + folder categorization

> Dự án: [[projects/control-tower-web/control-tower-web]]

## Problem

Knowledge Base & ADR Index chỉ load một số file, không lấy hết files trong các thư mục con. Cần load recursive và phân loại theo folder.

## Tiêu chí nghiệm thu (AC)

- [x] **AC1:** Load tất cả .md files từ `knowledge/` recursive (bao gồm subdirs: patterns/, decisions/, metrics/, agents/)
- [x] **AC2:** Phân loại hiển thị theo folder (collapsible tree hoặc tabs)
- [x] **AC3:** ADR Index load đầy đủ từ `knowledge/decisions/ADR-*.md`

## Plan

1. Update data loader to recursively scan knowledge/ directory
2. Group files by parent folder
3. Render as tree view or tabbed sections
4. Special handling for ADR files (prefix ADR-)
