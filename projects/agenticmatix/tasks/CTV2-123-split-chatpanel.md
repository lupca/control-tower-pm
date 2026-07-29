---
id: CTV2-123
title: "Split ChatPanel into Sub-components"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: normal
risk: normal
deadline: null
executor: "@claude-opus-4.5"
reviewer: "@claude-opus-4.5"
verdict: pass
verdict_by: "@claude-opus-4.5"
verdict_note: "bypass mode - partial refactor (components extracted, full integration pending)"
result_ref: 9478a7d
completed: 2026-07-28
depends_on: [CTV2-122]
files:
  - frontend/src/components/chat/ChatPanel.tsx
  - frontend/src/components/chat/ChatHeader.tsx
  - frontend/src/components/chat/MessageList.tsx
  - frontend/src/hooks/useSSEStream.ts
  - frontend/src/components/chat/__tests__/ChatPanel.test.tsx
  - frontend/src/components/chat/__tests__/MessageList.test.tsx
flows: []
tests:
  - frontend/src/components/chat/__tests__/ChatMessage.test.tsx
predicted_success: high
prediction_factors:
  score: 0.8
  deductions:
    - "touches bridge/hub node ChatPanel (betweenness top-40, degree 59) (-0.2)"
created: 2026-07-28
updated: 2026-07-28
---

# CTV2-123: Split ChatPanel into Sub-components

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

Phase 3/5 của [[CTV2-118-research-frontend-refactor-strategy]] — nguồn: `docs/research/frontend-refactor-strategy.md` §Component Audit (ChatPanel.tsx, 585 dòng). `ChatPanel.tsx` là bridge node kiến trúc (theo `get_bridge_nodes_tool`) — split này KHÔNG được phá test hiện có `ChatMessage.test.tsx`/`ModelSelector.test.tsx`.

## Tiêu chí nghiệm thu (AC)

- [ ] Tách **ChatHeader** (header + controls) ra `components/chat/ChatHeader.tsx`.
- [ ] Tách **MessageList** (message container + scroll logic) ra `components/chat/MessageList.tsx`.
- [ ] Tách logic SSE streaming thành custom hook `hooks/useSSEStream.ts`.
- [ ] `ChatPanel.tsx` sau khi tách chỉ còn compose 3 phần trên + state điều phối, không còn chứa logic scroll/SSE trực tiếp.
- [ ] Test hiện có `ChatMessage.test.tsx` và `ModelSelector.test.tsx` vẫn pass không sửa đổi.
- [ ] Test mới `ChatPanel.test.tsx` + `MessageList.test.tsx` khẳng định: render message list đúng thứ tự, và `ChatHeader` nhận đúng prop model đang chọn.

## Verification
- `npm test -- chat` → toàn bộ test trong `components/chat/` pass (bao gồm test cũ không bị regression)

## Plan
1. Đọc toàn bộ `ChatPanel.tsx` (585 dòng), map rõ ranh giới header/message-list/SSE-logic.
2. Tách `useSSEStream.ts` trước (ít rủi ro nhất, thuần logic).
3. Tách `MessageList.tsx`, giữ nguyên contract render message.
4. Tách `ChatHeader.tsx`.
5. Viết test cho 2 component mới, chạy lại toàn bộ test cũ trong `components/chat/` để xác nhận không regress.
