---
id: CTV2-045
title: "Fix Chat Panel Scroll - Prevent UI Stretch"
status: done
priority: high
risk: low
deadline: 2026-07-30
executor: "@gpt-5.6-luna-high"
reviewer: "@gpt-5.6-sol"
dispatched: 2026-07-26
result_ref: "48ffec7"
in_review: 2026-07-26
reviewer:
files:
  - frontend/src/components/chat/ChatPanel.tsx
  - frontend/src/components/chat/ChatPanelManager.tsx
  - frontend/src/pages/TaskDetail.tsx
tests:
  - Long chat content scrollable
  - Chat panel has fixed max-height
  - Scroll to bottom on new message
  - UI layout not affected by chat length
created: 2026-07-26
effort: 1h
updated: 2026-07-26
---

# CTV2-045: Fix Chat Panel Scroll

## Problem

Khi chat dài, UI bị kéo dài ra thay vì có scroll.

## Fix

1. **ChatPanel Container**:
   ```tsx
   <div className="flex flex-col h-full max-h-[calc(100vh-200px)]">
     <div className="flex-1 overflow-y-auto">
       {messages}
     </div>
     <div className="flex-shrink-0">
       {input}
     </div>
   </div>
   ```

2. **Auto-scroll to bottom** on new message

3. **Sticky input** - Input always visible at bottom

## AC

- [ ] AC1: Chat messages scrollable when content exceeds viewport
- [ ] AC2: Chat input stays fixed at bottom
- [ ] AC3: New messages auto-scroll to bottom
- [ ] AC4: TaskDetail layout unaffected by chat length
