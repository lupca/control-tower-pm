---
id: CTV2-067
title: "Fix Markdown Line Breaks + Whitespace Handling"
status: done
priority: high
risk: normal
deadline: 2026-07-28
executor: "@gpt-5.6-luna-high"
reviewer: "@claude-opus"
result_ref: "ca8e182"
depends_on: []
files:
  - frontend/src/components/chat/MessageContent.tsx
  - frontend/package.json
flows: [chat-session]
tests:
  - frontend/src/components/chat/__tests__/ChatMessage.test.tsx
dispatched: 2026-07-27
in_review: 2026-07-27
reviewed: 2026-07-27
verdict: pass
predicted_success: high
prediction_factors:
  score: 0.9
  deductions:
    - "simple fix — add plugin (-0.0)"
    - "blast_radius: 2 files (-0.0)"
created: 2026-07-27
updated: 2026-07-27
plan_approved: 2026-07-27
---

# CTV2-067: Fix Markdown Line Breaks + Whitespace Handling

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Context

CTV2-062 added markdown rendering nhưng output AI vẫn còn hiển thị raw:
- `###` headers không render đúng
- `*` bullets hiển thị thay vì list
- Không xuống dòng đúng — đặc biệt với output phức tạp như status report

**Root cause (từ code analysis):**
1. **Missing `remark-breaks` plugin** — single `\n` bị collapse thay vì tạo `<br>`, nên list items và paragraphs dính nhau
2. **Default `rehype-sanitize` schema** — có thể strip elements unexpectedly
3. **No `whitespace-pre-wrap`** — raw text với line breaks ngoài markdown syntax bị collapse

## Tiêu chí nghiệm thu (AC)

- [x] AC1: Single line break (`\n`) renders as `<br>` — không collapse
- [x] AC2: Headers (###) render correctly trong complex output
- [x] AC3: Bullet lists (*) render as `<ul><li>` không hiện raw `*`
- [x] AC4: Status report output (nhiều sections, lists) renders correctly
- [x] AC5: Container có `whitespace-pre-wrap` hoặc tương đương

## Verification

```bash
cd /home/lupca/projects/control-tower-v2
# Check remark-breaks installed
grep "remark-breaks" frontend/package.json

# Run tests
cd frontend && npm test -- ChatMessage

# Visual test: paste this vào chat và verify rendered:
# ### Task Status
# - PMI-001: done
# - PMI-002: in-review
#
# **Summary**: 2 tasks total
```

## Plan

1. **Install remark-breaks**
   ```bash
   cd frontend && npm install remark-breaks
   ```

2. **Update MessageContent.tsx**
   ```tsx
   import remarkBreaks from 'remark-breaks';
   
   // In ReactMarkdown:
   remarkPlugins={[remarkGfm, remarkBreaks]}
   ```

3. **Add whitespace handling to container**
   ```tsx
   <div className="markdown-content leading-relaxed whitespace-pre-wrap">
   ```

4. **Test với complex output**
   - Send status report query
   - Verify headers, lists, line breaks render correctly

## Sub-tasks

- [x] Install `remark-breaks` package
- [x] Add `remarkBreaks` to remarkPlugins array
- [x] Add `whitespace-pre-wrap` to container class
- [x] Visual test với complex markdown output
