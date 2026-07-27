---
id: CTV2-069
title: "Fix Markdown Rendering - Newlines Double-Encoded"
status: in-review
priority: urgent
risk: normal
deadline: 2026-07-28
executor: "@gpt-5.6-luna-high"
reviewer: "@claude-opus"
result_ref: "0f62f73"
depends_on: []
files:
  - frontend/src/components/chat/ChatPanel.tsx
  - frontend/src/components/chat/MessageContent.tsx
  - backend/app/api/chat.py
  - backend/app/services/coordinator.py
flows: [chat-session]
tests:
  - frontend/src/components/chat/__tests__/ChatMessage.test.tsx
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: high
prediction_factors:
  score: 0.85
  deductions:
    - "debugging task, may need multiple iterations (-0.15)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-068: Fix Markdown Rendering - Newlines Lost

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Context

Screenshot cho thấy markdown output hiển thị như 1 paragraph dài:
- `---###` liền nhau (thay vì `---` rồi xuống dòng `###`)
- `*` bullets hiện raw text
- Tất cả dồn 1 dòng, không xuống dòng

**Root cause giả định:** Newlines (`\n`) bị strip ở đâu đó trong pipeline:
1. LLM response → Backend
2. Backend → DB storage (JSON column)
3. DB → API response
4. API → Frontend state
5. Frontend state → ReactMarkdown

## Tiêu chí nghiệm thu (AC)

- [ ] AC1: Console log tại mỗi điểm trong pipeline để tìm nơi newlines bị mất
- [ ] AC2: Fix điểm gây mất newlines
- [ ] AC3: Markdown với headers (###), lists (*), và line breaks render đúng
- [ ] AC4: Complex output (status report với tables) render đúng
- [ ] AC5: Tests pass

## Verification

```bash
cd /home/lupca/projects/control-tower-v2

# Test 1: Send markdown message và check rendering
# Input: "### Header\n\n* Item 1\n* Item 2"
# Expected: H3 heading, followed by bullet list

# Test 2: Run frontend tests
cd frontend && npm test -- ChatMessage

# Test 3: Visual check với status report query
```

## Debug Steps

### Step 1: Add console logs to trace content

**Backend (chat.py):**
```python
# Before yielding chunk
logger.debug("CHUNK_CONTENT: %r", chunk)  # %r shows raw with \n visible
```

**Frontend (ChatPanel.tsx):**
```tsx
// After JSON.parse
console.log('PARSED_CHUNK:', JSON.stringify(data.content));  // Check if \n present

// Before setting messages
console.log('ACCUMULATED:', JSON.stringify(accumulatedContent));
```

**Frontend (MessageContent.tsx):**
```tsx
// Before ReactMarkdown
console.log('MD_INPUT:', JSON.stringify(content));
```

### Step 2: Check possible culprits

1. **LLM response format** - Some LLMs return `\\n` (escaped) vs `\n` (literal)
2. **JSON serialization** - Double encoding issue
3. **Database JSON column** - PostgreSQL JSON vs JSONB handling
4. **SSE streaming** - Line breaks in SSE data

### Step 3: Fix based on findings

Common fixes:
- `content.replace(/\\n/g, '\n')` if double-escaped
- Ensure proper JSON encoding in backend
- Check SSE format (data lines should preserve content newlines)

## Plan

1. **Quick fix in MessageContent.tsx** - normalize escaped newlines before ReactMarkdown:
   ```tsx
   const normalizedContent = content
     .replace(/\\n/g, '\n')     // Fix double-escaped newlines
     .replace(/\\r/g, '\r');    // Fix carriage returns too
   ```

2. **Find root cause in backend** - check where double-encoding happens:
   - SSE JSON encoding
   - DB JSON storage
   - LLM response processing

3. **Fix root cause** if found, remove frontend workaround

4. **Test** với complex markdown (status report, tables, lists)

## Sub-tasks

- [ ] Add debug logging (backend + frontend)
- [ ] Test và trace newlines
- [ ] Identify và fix root cause
- [ ] Remove debug logging
- [ ] Visual test với complex markdown
