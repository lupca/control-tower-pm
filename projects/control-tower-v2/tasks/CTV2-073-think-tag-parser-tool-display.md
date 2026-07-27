---
id: CTV2-073
title: "Parse <think> tags + Collapsible Thought Process UI + Tool Usage Display"
repo_root: /home/lupca/projects/control-tower-v2
status: done
rejections: 1
priority: high
risk: normal
deadline: null
executor: "@gpt-5.6-luna"
reviewer: "@claude-opus"
result_ref: "cbed065"
depends_on: []
files:
  - frontend/src/components/chat/MessageContent.tsx
  - frontend/src/components/chat/ChatMessage.tsx
  - frontend/src/components/chat/ChatPanel.tsx
  - backend/app/services/providers/openai_adapter.py
flows: []
tests: []
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: high
prediction_factors:
  score: 0.9
  deductions:
    - "no existing tests: -0.1"
created: 2026-07-27
updated: 2026-07-27
confidence_interval: [0.75, 0.95]
---

# CTV2-073: Parse <think> tags + Collapsible Thought Process UI + Tool Usage Display

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Tiêu chí nghiệm thu (AC)

- [x] `parseThinkingContent(content: string)` parser exists, returns `{ thinkingContent: string | null, finalContent: string, isThinking: boolean }`
- [x] Parser handles both closed `<think>...</think>` and unclosed `<think>...` (streaming) cases
- [x] Thought process renders as collapsible accordion: collapsed by default with badge "Thought process" + brain icon
- [x] While streaming with unclosed `</think>`, show "Thinking..." label with pulse animation
- [x] Clicking accordion expands/collapses thought content
- [x] Tool usage from SSE events displayed as collapsible blocks (tool name + arguments + result)
- [x] Final response content (`finalContent`) renders normally via ReactMarkdown below the thought/tool accordions

## Verification

- `cd /home/lupca/projects/control-tower-v2/frontend && npm run build` → 0 errors
- Manual test: send message to model that produces `<think>` tags → accordion appears collapsed, expandable
- Manual test: during streaming before `</think>` closes → "Thinking..." with pulse animation visible
- Manual test: send message that triggers tool use → tool block appears with name/args/result

## Plan

1. **Create `parseThinkingContent` utility** (`frontend/src/utils/parseThinking.ts` or inline in MessageContent):
   - Regex pattern: `/<think>([\s\S]*?)(<\/think>|$)/`
   - Return `{ thinkingContent, finalContent, isThinking: !hasClosingTag }`
   - Handle edge case: multiple `<think>` blocks (concat all)

2. **Create `ThinkingAccordion` component** (`frontend/src/components/chat/ThinkingAccordion.tsx`):
   - Props: `content: string`, `isStreaming: boolean`, `defaultExpanded?: boolean`
   - Collapsed state: badge with brain icon + "Thought process" text
   - While `isStreaming && !hasClosingTag`: show "Thinking..." + pulse animation
   - Use Lucide icons (`Brain`, `ChevronDown`, `ChevronUp`)
   - Tailwind for styling (match existing chat bubble design)

3. **Create `ToolCallBlock` component** (`frontend/src/components/chat/ToolCallBlock.tsx`):
   - Props: `name: string`, `arguments: object`, `result?: string`, `isExecuting?: boolean`
   - Collapsible block showing tool name as header
   - Expand to show JSON args + result
   - While `isExecuting`: spinner/pulse indicator

4. **Update `ChatPanel.tsx` SSE handling**:
   - Add event type handling for `tool_start`, `tool_result` if backend sends them
   - Track tool calls in message state: `toolCalls?: Array<{name, args, result, status}>`

5. **Update `MessageContent.tsx`**:
   - Call `parseThinkingContent(content)`
   - Render `<ThinkingAccordion>` if `thinkingContent` exists
   - Render `<ToolCallBlock>` for each tool call
   - Render `<ReactMarkdown>` for `finalContent`

6. **Update `ChatMessage.tsx`**:
   - Pass `isStreaming` from message to `MessageContent`
   - Pass `toolCalls` array if available

## Sub-tasks

- [x] Add `parseThinkingContent` utility function in `MessageContent.tsx` or new utils file
- [x] Create `ThinkingAccordion` component (collapsed badge + expand/collapse toggle + pulse during streaming)
- [x] Create `ToolCallBlock` component (collapsible block showing tool name, arguments JSON, result)
- [x] Extend SSE event handling in `ChatPanel.tsx` to capture `tool_call` events (if backend sends them) or parse from content
- [x] Update `MessageContent.tsx` to use parser and render accordions before final content
- [x] Update `ChatMessage.tsx` to pass `isStreaming` prop for streaming state detection
- [ ] **FIX:** Backend `openai_adapter.py` phải combine `reasoning_content` + `content` với `<think>` tags

## Findings (Round 1)

- [ ] Backend `openai_adapter.py:158-162,331-336` dùng `content OR reasoning_content` thay vì combine cả hai. Kimi K3/GLM 5.2 trả cả 2 fields, cần wrap `reasoning_content` trong `<think>` tags rồi prepend vào `content`.
