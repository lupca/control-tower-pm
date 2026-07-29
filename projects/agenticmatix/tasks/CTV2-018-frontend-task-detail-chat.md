---
id: CTV2-018
title: "Frontend - Task Detail page + Chat Panel"
status: done
priority: high
risk: medium
executor: "@gemini-3.6-flash"
reviewer: "@gpt-5.6-sol"
deadline: 2026-07-30
created: 2026-07-26
updated: 2026-07-26
depends_on: [CTV2-015]
files:
  - frontend/src/pages/TaskDetail.tsx
  - frontend/src/components/task/TaskHeader.tsx
  - frontend/src/components/task/TaskSpec.tsx
  - frontend/src/components/task/TaskMeta.tsx
  - frontend/src/components/chat/ChatPanel.tsx
  - frontend/src/components/chat/ChatMessage.tsx
  - frontend/src/components/chat/ChatInput.tsx
  - frontend/src/components/chat/ChatPanelManager.tsx
tests:
  - Task detail loads with all data
  - Chat panel opens and streams messages
  - Multi-panel support (max 3)
  - Persistence via localStorage
---

# CTV2-018: Frontend Task Detail + Chat

## Reference
- control-tower-web `src/pages/task/[id].astro`
- control-tower-web `src/components/chat/` (from CTW-014)

## Acceptance Criteria

### Task Detail
- [ ] AC1: Header: ID, Title, Status, Priority, Risk badges
- [ ] AC2: Spec section: Acceptance Criteria list, Files, Tests
- [ ] AC3: Plan section: Implementation plan (markdown rendered)
- [ ] AC4: Meta sidebar: Executor, Reviewer, Dates, Verdict
- [ ] AC5: Audit trail section (collapsible)
- [ ] AC6: "Open Chat" button

### Chat Panel
- [ ] AC7: Slide-over panel từ phải
- [ ] AC8: Load message history từ `/api/tasks/{id}/messages`
- [ ] AC9: Send message → stream response từ `/api/chat`
- [ ] AC10: SSE streaming hiển thị real-time
- [ ] AC11: Minimize/Expand/Close buttons
- [ ] AC12: Multi-panel manager (max 3 panels)
- [ ] AC13: Persist open panels trong localStorage

## Technical Notes
- Reuse ChatPanel components từ CTW-014
- SSE streaming với EventSource hoặc fetch + ReadableStream
- Panel position: fixed right, z-index cao
