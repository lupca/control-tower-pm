---
id: CTV2-129
title: "Add Tests for Agents and ChatPanel"
repo_root: /home/lupca/projects/control-tower-v2
status: todo
priority: normal
risk: normal
deadline: null
executor: "@gemini-3.6-flash"
reviewer: null
result_ref: null
depends_on: [CTV2-126, CTV2-127]
files:
  - frontend/src/pages/__tests__/Agents.test.tsx
  - frontend/src/pages/__tests__/AgentDetail.test.tsx
  - frontend/src/components/chat/__tests__/ChatPanel.test.tsx
  - frontend/src/test/setup.ts
flows: []
tests:
  - frontend/src/pages/__tests__/AgentDetail.test.tsx
  - frontend/src/components/chat/__tests__/ChatMessage.test.tsx
predicted_success: high
prediction_factors:
  score: 1.0
  deductions: []
created: 2026-07-28
updated: 2026-07-28
---

# CTV2-129: Add Tests for Agents and ChatPanel

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

Phase 5/5 của [[CTV2-118-research-frontend-refactor-strategy]] — nguồn: `docs/research/frontend-refactor-strategy.md` §Test Coverage Recommendations (`AgentsPage`/`AgentDetailPage` — degree 75/67, `ChatPanel` — bridge node, ưu tiên High). `ChatPanel.test.tsx` đã có khung từ CTV2-123, task này mở rộng coverage tương tác thật (gửi tin nhắn, chuyển model).

## Tiêu chí nghiệm thu (AC)

- [ ] `Agents.test.tsx`: khẳng định filter theo role/status hoạt động (case CTV2-121), modal tạo agent mở/đóng đúng (case CTV2-127).
- [ ] `AgentDetail.test.tsx` (đã có case null-id từ CTV2-120, KPI cards từ CTV2-124) bổ sung case tích hợp: render đủ 3 sub-component.
- [ ] `ChatPanel.test.tsx` (đã có khung từ CTV2-123) bổ sung: gửi tin nhắn thành công cập nhật `MessageList`, chuyển model thất bại hiển thị lỗi (case CTV2-120's `showError` fix).
- [ ] `test/setup.ts` đảm bảo mock SSE/WebSocket cho test `ChatPanel` chạy ổn định trong CI (không flaky).

## Verification
- `npm test -- Agents AgentDetail ChatPanel` → pass, không flaky khi chạy lại 3 lần liên tiếp.

## Plan
1. Rà `test/setup.ts`, đảm bảo mock SSE/WebSocket đầy đủ và ổn định.
2. Viết `Agents.test.tsx`.
3. Mở rộng `AgentDetail.test.tsx` cho cấu trúc đã tách (CTV2-124).
4. Mở rộng `ChatPanel.test.tsx` (khung từ CTV2-123) với case gửi tin nhắn + chuyển model lỗi.
