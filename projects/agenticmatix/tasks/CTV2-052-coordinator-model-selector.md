---
id: CTV2-052
title: "Coordinator Model Selector UI"
status: done
dispatched: 2026-07-26
result_ref: "65c5af4"
in_review: 2026-07-26
priority: medium
risk: normal
deadline: 2026-08-02
executor: "@gpt-5.6-luna-high"
reviewer: "@claude-opus"
files:
  - frontend/src/components/chat/ChatInput.tsx
  - frontend/src/components/chat/ModelSelector.tsx
  - frontend/src/components/chat/ChatPanel.tsx
  - frontend/src/hooks/useChat.ts
  - backend/app/api/sessions.py
tests:
  - frontend/src/components/chat/ModelSelector.test.tsx
created: 2026-07-26
effort: 3h
updated: 2026-07-26
plan_approved: 2026-07-26
---

# CTV2-052: Coordinator Model Selector UI

## Context

CTV2-051 implemented CLI-based coordinator with model switching (Claude ↔ Gemini). Backend supports `selected_model`/`selected_provider` in session via PATCH `/api/sessions/{id}`. Missing: UI to switch models.

## Objective

Add dropdown to chat UI for selecting coordinator model. Display current model, persist selection to session.

## Deliverables

1. **ModelSelector component** (`frontend/src/components/chat/ModelSelector.tsx`)
   - Dropdown with model options: Claude Sonnet, Claude Opus, Gemini Pro, Gemini Flash
   - Show current selection from session
   - Compact design fitting in ChatInput area

2. **Integration with ChatInput/ChatPanel**
   - Add ModelSelector to ChatInput or ChatPanel header
   - Pass selected model to chat API calls
   - Update session via PATCH when selection changes

3. **Visual feedback**
   - Show model icon/badge (Anthropic logo for Claude, Google for Gemini)
   - Indicate when model switch is in progress
   - Toast/notification on successful switch

## Models to support

| Display Name | model value | provider |
|--------------|-------------|----------|
| Claude Sonnet | claude-sonnet-4-20250514 | anthropic |
| Claude Opus | claude-opus-4-5-20251101 | anthropic |
| Gemini Pro | gemini-2.5-pro | google |
| Gemini Flash | gemini-2.5-flash | google |

## AC

- [ ] AC1: ModelSelector dropdown shows 4 model options
- [ ] AC2: Current session model displayed as selected
- [ ] AC3: Changing model calls PATCH /api/sessions/{id} with selected_model
- [ ] AC4: Chat messages sent with new model after switch
- [ ] AC5: Model switch persists across page refresh
- [ ] AC6: Provider icon shown next to model name
- [ ] AC7: Loading state shown during model switch API call

## Plan

1. **Create ModelSelector component** (`ModelSelector.tsx`)
   - Define MODELS constant with display name, value, provider, icon
   - Dropdown using existing UI primitives (or simple select)
   - Props: `currentModel`, `onModelChange`, `disabled`, `isLoading`
   - Show provider icon (Anthropic: purple, Google: blue/green)

2. **Add API hook** (in `useChat.ts` or new `useSession.ts`)
   - `updateSessionModel(sessionId, model)` → PATCH /api/sessions/{id}
   - Handle loading/error states
   - Return updated session

3. **Integrate into ChatInput**
   - Add ModelSelector before textarea or in header row
   - Get current model from session state
   - On change: call updateSessionModel, update local state
   - Pass model to sendMessage API call

4. **Update ChatPanel to pass session**
   - Ensure ChatPanel passes session.selected_model to ChatInput
   - Re-fetch session after model switch or use optimistic update

5. **Tests**
   - Test ModelSelector renders all options
   - Test selection triggers onChange
   - Test API call on model change
