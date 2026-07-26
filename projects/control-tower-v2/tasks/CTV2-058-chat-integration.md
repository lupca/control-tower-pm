---
id: CTV2-058
title: "Chat UI Phase 3: Integration + Global Chat"
status: todo
priority: high
risk: normal
deadline: null
executor: "@claude-sonnet-medium"
reviewer: null
result_ref: null
depends_on: [CTV2-056, CTV2-057]
files:
  - frontend/src/App.tsx
  - frontend/src/pages/ProjectDetail.tsx
  - frontend/src/contexts/ChatContext.tsx
  - frontend/src/hooks/useChatContext.ts
flows: []
tests: []
dispatched: 2026-07-27
in_review: null
predicted_success: high
prediction_factors:
  score: 0.7
  deductions:
    - "integration complexity (-0.2)"
    - "depends on CTV2-056, CTV2-057 (-0.1)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-058: Chat UI Phase 3: Integration + Global Chat

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Reference

Architecture: `docs/chat-ui-architecture.md` (CTV2-055)

## Tiêu chí nghiệm thu (AC)

- [ ] `ChatContext.tsx`: React context cho global chat state (current session, sessions list, context level)
- [ ] `useChatContext.ts`: Hook để auto-detect context từ current route
- [ ] `App.tsx`: Wrap với ChatProvider, add GlobalChatButton at root
- [ ] `ProjectDetail.tsx`: Add ChatPanel cho project-level chat
- [ ] Global chat accessible từ Dashboard, Projects list, bất kỳ page nào
- [ ] Context auto-switch khi navigate: /tasks/:id → Task, /projects/:id → Project, other → Global

## Verification

- Từ Dashboard: click GlobalChatButton → opens Global chat
- Từ ProjectDetail: chat panel shows với project context pre-selected
- Từ TaskDetail: chat panel shows với task+project context
- Navigate giữa pages: context switches correctly

## Plan

1. Create `ChatContext.tsx` - global state provider
2. Create `useChatContext.ts` - route-based context detection
3. Update `App.tsx` - wrap ChatProvider, add GlobalChatButton
4. Update `ProjectDetail.tsx` - add chat panel with project context
5. Test navigation và context switching
