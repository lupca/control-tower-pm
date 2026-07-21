---
id: PMI-003
title: "Triển khai Identity Service SSO tập trung"
status: done
priority: high
risk: normal
deadline: 2026-07-14
executor: null
reviewer: null
result_ref: "commit 0d22c38"
depends_on: []
files:
  - Identity/
  - Gateway/
  - PMI/backend/utils/auth.py
  - OMS/backend/utils/auth.py
  - WMS/backend/utils/auth.py
flows: []
tests:
  - Identity/backend/tests/
  - PMI/backend/tests/test_auth*.py
dispatched: null
in_review: null
created: 2026-07-14
updated: 2026-07-21
---

# PMI-003: Triển khai Identity Service SSO tập trung

> Dự án: [[projects/topvnsport-pmi/_project|topvnsport-pmi]]

> Task này được reconcile từ git history — đã implement trước khi control-tower tracking.

## Tiêu chí nghiệm thu (AC)
- [x] Backend FastAPI cho auth, staff, roles endpoints
- [x] Frontend Next.js 14 (login, dashboard, CRUD pages)
- [x] Nginx Gateway với auth_request centralized authentication
- [x] PMI/OMS/WMS backend đọc X-User-* headers từ gateway

## Plan
*(đã implement trước khi control-tower tracking — không có kế hoạch ghi lại)*

## Sub-tasks
- [x] Backend FastAPI cho auth, staff, roles endpoints
- [x] Frontend Next.js 14 (login, dashboard, CRUD pages)
- [x] Nginx Gateway với auth_request centralized authentication
- [x] PMI/OMS/WMS backend đọc X-User-* headers từ gateway
