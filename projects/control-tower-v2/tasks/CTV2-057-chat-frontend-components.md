---
id: CTV2-057
title: "Chat UI Phase 2: Frontend Components"
status: done
priority: high
risk: normal
deadline: null
executor: "@claude-sonnet-medium"
reviewer: "@claude-opus"
result_ref: "3f7a622"
depends_on: [CTV2-053]
files:
  - frontend/src/components/chat/SessionTabs.tsx
  - frontend/src/components/chat/GlobalChatButton.tsx
  - frontend/src/components/chat/ContextIndicator.tsx
  - frontend/src/components/chat/ChatPanel.tsx
  - frontend/src/components/chat/ChatPanelManager.tsx
  - frontend/src/hooks/useSessions.ts
flows: []
tests: []
dispatched: 2026-07-27
in_review: null
predicted_success: high
prediction_factors:
  score: 0.75
  deductions:
    - "new UI components (-0.15)"
    - "state management (-0.1)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-057: Chat UI Phase 2: Frontend Components

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Reference

Architecture: `docs/chat-ui-architecture.md` (CTV2-055) - Section "Wireframes"

## Tiêu chí nghiệm thu (AC)

- [x] `SessionTabs.tsx`: Tab bar với [Session1] [Session2] [+ New], active indicator, close button
- [x] `GlobalChatButton.tsx`: Floating button bottom-right (fixed position), click → expand
- [x] `ContextIndicator.tsx`: Breadcrumb hiển thị 🌍 Global → 📁 Project → 📋 Task
- [x] `useSessions.ts`: Hook để fetch/create/switch sessions by context
- [x] `ChatPanel.tsx` update: Accept sessions prop, show ContextIndicator, integrate SessionTabs
- [x] `ChatPanelManager.tsx` update: Manage multiple sessions state, fetch sessions on mount

## Verification

- Components render without errors
- SessionTabs: click tab switches session, click + creates new
- GlobalChatButton: visible on all pages, click expands chat
- ContextIndicator: shows correct context based on props

## Review Findings (Round 1)

- [x] F1 (Blocking): Closing sole session keeps writing to it (threadId fallback, key never changes)
- [x] AC2 (Blocking): GlobalChatButton never imported or rendered anywhere
- [x] F2: Impure state updater in useSessions.ts:109 (setSessions calls setActiveSessionId)
- [x] F3: Stale-response race in useSessions.ts:58 (no AbortController)
- [x] F4: Session switch drops in-flight SSE stream (no cleanup in ChatPanel)
- [x] F5: Session load errors invisible (error not destructured from useSessions)
- [x] F6: Index-based labels rename conversations on refetch
- [x] F7: Double-click creates duplicate sessions (no pending state)
- [ ] F8 (Nits): Missing tabIndex/tablist, truncate without min-w-0, projectName not passed

## Review Findings (Round 2)

- [ ] F8 (New): AbortError triggers api.ts retry + showError toast (StrictMode: every panel open)
- [ ] F9 (New): closeSession stale closure over sessions/activeSessionId across await resurrects closed sessions

## Plan

1. Create `useSessions.ts` hook - fetch sessions by context_level/project_id
2. Create `SessionTabs.tsx` - tab UI component
3. Create `GlobalChatButton.tsx` - floating button
4. Create `ContextIndicator.tsx` - breadcrumb component
5. Update `ChatPanel.tsx` - integrate new components
6. Update `ChatPanelManager.tsx` - multi-session state management
