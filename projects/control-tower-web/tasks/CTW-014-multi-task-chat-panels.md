---
id: CTW-014
title: "Multi-task Chat Panels - Per-task conversation UI"
status: done
done: 2026-07-26
in_review: 2026-07-26
review_verdict: pass
priority: high
risk: medium
executor: "@antigravity-3.6-high"
reviewer: "@antigravity"
dispatched: 2026-07-26 
deadline: 2026-07-28
created: 2026-07-26
updated: 2026-07-26
files:
  - src/components/chat/ChatPanel.tsx
  - src/components/chat/ChatMessage.tsx
  - src/components/chat/ChatInput.tsx
  - src/pages/task/[id].astro
  - src/lib/api.ts
  - src/lib/websocket.ts
tests:
  - Chat panel renders correctly
  - Messages send and receive via API
  - Multiple panels can be open simultaneously
  - WebSocket reconnection works
  - Session state persists per task
---

# CTW-014: Multi-task Chat Panels

## Context
Hiện tại control-tower-v2 có LangGraph backend + Chainlit chat, nhưng chỉ hỗ trợ 1 task/session. User muốn:
- Click task trong list → mở chat panel riêng cho task đó
- Mở nhiều chat panels cùng lúc (như nhiều tab Claude)
- Mỗi task có conversation history riêng (thread_id)

## Acceptance Criteria
- [x] AC1: Component `ChatPanel` hiển thị conversation history của 1 task
- [x] AC2: Click task row/card → mở ChatPanel trong slide-over hoặc modal
- [x] AC3: Có thể mở tối đa 3 ChatPanels cùng lúc (tabbed hoặc tiled)
- [x] AC4: Gửi message → call API `/api/chat` với `thread_id` = task.session_id
- [x] AC5: Streaming response hiển thị real-time (SSE hoặc WebSocket)
- [x] AC6: Panel có nút close, minimize, expand
- [x] AC7: Persist open panels trong localStorage (reload không mất)

## Plan

### Phase 1: Backend API Extension (control-tower-v2)
1. Thêm endpoint `POST /api/chat` nhận `{thread_id, message}`, trả về stream
2. Thêm endpoint `GET /api/tasks/{id}/messages` lấy history
3. Đảm bảo mỗi task có unique `session_id` (tạo khi task được tạo)

### Phase 2: Chat Components (control-tower-web)
1. `ChatPanel.tsx` - Container chính
   - Props: `taskId`, `onClose`, `isMinimized`
   - State: messages[], isLoading, isConnected
   - Fetch history on mount
   - Send message via API
   - Stream response via EventSource

2. `ChatMessage.tsx` - Single message bubble
   - Props: `role`, `content`, `timestamp`
   - Markdown rendering
   - Code syntax highlighting

3. `ChatInput.tsx` - Input box
   - Textarea auto-resize
   - Send on Enter (Shift+Enter for newline)
   - Disable while loading

### Phase 3: Multi-Panel Manager
1. `ChatPanelManager.tsx` - Quản lý nhiều panels
   - State: openPanels: {taskId, position, minimized}[]
   - Max 3 panels
   - Drag to reorder
   - Save/restore từ localStorage

2. Update `TaskTable` và `KanbanCard`
   - Add "Chat" button/icon
   - onClick → ChatPanelManager.open(taskId)

### Phase 4: Real-time Updates
1. WebSocket connection cho live updates
   - Task status changes
   - New messages from other sessions
2. Reconnection logic với exponential backoff

## Technical Notes
- Backend: control-tower-v2 (port 8001)
- Frontend: control-tower-web (Astro + React)
- API proxy cần config trong astro.config.mjs
- LLM: Kimi-K3 via SiliconFlow (đã config)

## Dependencies
- control-tower-v2 backend running (docker compose)
- CORS config cho cross-origin requests
