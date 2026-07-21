---
id: PMI-005
title: "Hoàn thành API Gateway migration & centralize authentication"
status: done
priority: high
risk: normal
deadline: 2026-07-15
executor: null
reviewer: null
result_ref: "commit b279b90"
depends_on: [PMI-003]
files:
  - Gateway/
  - OMS/backend/
  - OMS/web/
  - WMS/backend/
  - WMS/web/
flows: []
tests:
  - "E2E auth tests"
dispatched: null
in_review: null
created: 2026-07-15
updated: 2026-07-21
---

# PMI-005: Hoàn thành API Gateway migration & centralize authentication

> Dự án: [[projects/topvnsport-pmi/topvnsport-pmi]]

> Task này được reconcile từ git history — đã implement trước khi control-tower tracking.

## Tiêu chí nghiệm thu (AC)
- [x] API Gateway hoạt động cho tất cả services
- [x] OMS/WMS frontend & backend auth hoạt động qua gateway

## Plan
*(đã implement trước khi control-tower tracking — không có kế hoạch ghi lại)*

## Sub-tasks
- [x] API Gateway hoạt động cho tất cả services
- [x] OMS/WMS frontend & backend auth hoạt động qua gateway
