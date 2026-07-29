---
id: CTV2-085
title: "UI Tool Palette từ GET /api/tools + deprecate COMMANDS dict"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: low
risk: normal
deadline: null
executor: "@claude-sonnet-medium"
reviewer: "@claude-opus"
result_ref: "3e1936a"
depends_on:
  - CTV2-077
files:
  - frontend/src/components/chat/ChatPanel.tsx
  - backend/app/services/command_router.py
flows: []
tests:
  - frontend/src/components/chat/__tests__/
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: high
prediction_factors:
  score: 0.85
  deductions:
    - "frontend test setup cho palette mới (-0.1)"
    - "UX autocomplete cần thống nhất với slash syntax (-0.05)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-085: UI Tool Palette (ADR-001 Phase 4)

> Dự án: [[projects/control-tower-v2/control-tower-v2]]
> Thiết kế: `docs/adr/ADR-001-unified-tool-architecture.md` §6 Phase 4, fix P5 (discoverability)

## Tiêu chí nghiệm thu (AC)

- [x] ChatPanel: gõ `/` hiện palette autocomplete lấy data từ `GET /api/tools` (name, slash_alias, description, group)
- [x] `/help` render từ cùng nguồn (không còn hardcode danh sách lệnh)
- [x] `COMMANDS` dict hardcode trong `command_router.py` chỉ còn là projection từ registry (đã làm ở CTV2-077) — xác nhận không còn danh sách lệnh trùng lặp nào khác trong FE/BE
- [x] Tool call status hiển thị canonical name thống nhất với palette

## Verification

- FE tests xanh; palette hiện đúng danh sách tool từ API (mock)
- Grep FE/BE không còn hardcoded command list ngoài registry

## Plan

1. Hook `useTools()` (React Query) gọi `/api/tools`.
2. Palette component + keyboard navigation, filter theo prefix.
3. `/help` + tool status dùng cùng data.
4. E2E test (theo quy ước E2E-over-browser).

## Sub-tasks

- [x] useTools + palette
- [x] /help từ API
- [x] Thống nhất hiển thị tên
- [x] Tests
