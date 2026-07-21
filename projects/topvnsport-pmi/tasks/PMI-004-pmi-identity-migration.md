---
id: PMI-004
title: "Migrate PMI sang Identity Service authentication"
status: done
priority: high
risk: normal
deadline: 2026-07-14
executor: null
reviewer: null
result_ref: "commit e5461a5, 3d6ee6d"
depends_on: [PMI-003]
files:
  - PMI/backend/utils/auth.py
  - PMI/web/src/utils/apiClient.ts
flows: []
tests:
  - PMI/backend/tests/test_auth*.py
dispatched: null
in_review: null
created: 2026-07-14
updated: 2026-07-21
---

# PMI-004: Migrate PMI sang Identity Service authentication

> Dự án: [[projects/topvnsport-pmi/_project|topvnsport-pmi]]

> Task này được reconcile từ git history — đã implement trước khi control-tower tracking.

## Tiêu chí nghiệm thu (AC)
- [x] PMI sử dụng Identity Service thay vì local login
- [x] Xóa login page legacy, dùng AuthGuard

## Plan
*(đã implement trước khi control-tower tracking — không có kế hoạch ghi lại)*

## Sub-tasks
- [x] PMI sử dụng Identity Service thay vì local login
- [x] Xóa login page legacy, dùng AuthGuard
