---
id: CTV2-062
title: "Fix Chat UI Markdown Rendering"
status: done
priority: high
risk: normal
deadline: 2026-07-28
executor: "@gpt-5.6-luna-high"
reviewer: "@claude-opus"
result_ref: "1b33c05"
depends_on: []
files:
  - frontend/src/components/chat/ChatMessage.tsx
  - frontend/src/components/chat/MessageContent.tsx
flows: [chat-session]
tests:
  - frontend/src/components/chat/__tests__/ChatMessage.test.tsx
dispatched: 2026-07-27
in_review: 2026-07-27
done: 2026-07-27
predicted_success: high
prediction_factors:
  score: 0.9
  deductions:
    - "simple UI fix (-0.0)"
    - "well-defined scope (-0.0)"
    - "may need new dependency (-0.1)"
created: 2026-07-27
updated: 2026-07-27
planned: 2026-07-27
---

# CTV2-062: Fix Chat UI Markdown Rendering

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Context

Chat UI hiện đang hiển thị raw markdown text thay vì rendered markdown. User thấy `**bold**`, `# heading`, ```code``` thay vì formatted output.

## Tiêu chí nghiệm thu (AC)

- [x] AC1: Chat messages render markdown correctly
  - Headers (h1-h6)
  - Bold, italic, strikethrough
  - Code blocks với syntax highlighting
  - Lists (ordered, unordered)
  - Links
  - Tables
- [x] AC2: Code blocks có copy button
- [x] AC3: Dark/light theme compatible
- [x] AC4: No XSS vulnerabilities (sanitize HTML)

## Verification

- Visual test: send message với markdown, verify rendered correctly
- `npm test -- ChatMessage` → pass
- Check code blocks render với syntax highlighting
- Verify copy button works

## Plan

### Phase 1: Add Dependencies
1. Install `react-markdown` for markdown parsing
2. Install `react-syntax-highlighter` for code block highlighting
3. Install `rehype-sanitize` for XSS protection

### Phase 2: Create MessageContent Component
1. Create `MessageContent.tsx`:
   - Wrap content với `<ReactMarkdown>`
   - Configure code block renderer với syntax highlighting
   - Add copy button cho code blocks
   - Sanitize HTML output

### Phase 3: Update ChatMessage
1. Update `ChatMessage.tsx`:
   - Replace raw text với `<MessageContent>`
   - Ensure proper styling for markdown elements
   - Support dark/light theme

### Phase 4: Testing
1. Visual test với various markdown content
2. Verify code blocks render correctly
3. Test copy button functionality
4. Check dark/light theme compatibility

## Sub-tasks

- [ ] Add markdown rendering library (react-markdown hoặc marked)
- [ ] Update ChatMessage component to render markdown
- [ ] Add syntax highlighting for code blocks (highlight.js hoặc prism)
- [ ] Add copy button for code blocks
- [ ] Style for dark/light theme
- [ ] Add XSS sanitization
