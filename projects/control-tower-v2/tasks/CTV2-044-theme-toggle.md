---
id: CTV2-044
title: "Fix Dark/Light Mode Toggle - Full App Coverage"
status: dispatched
priority: high
risk: low
deadline: 2026-07-30
executor: "@gpt-5.6-luna-high"
reviewer: "@gpt-5.6-sol"
dispatched: 2026-07-26
result_ref: de226c2
in_review: 2026-07-26
reviewer:
files:
  - frontend/src/contexts/ThemeContext.tsx
  - frontend/src/components/layout/Navbar.tsx
  - frontend/src/index.css
  - frontend/src/App.tsx
tests:
  - Toggle button switches theme
  - Theme persists on refresh (localStorage)
  - All components respect theme
  - No hardcoded colors outside theme
created: 2026-07-26
effort: 3h
rejections: 1
updated: 2026-07-26
---

# CTV2-044: Fix Dark/Light Mode Toggle

## Problem

Nút toggle theme có nhưng không hoạt động. Một số components có thể hardcode colors.

## Scope

1. **ThemeContext** - Create/fix context với:
   - `theme: 'light' | 'dark'`
   - `toggleTheme()`
   - Persist to localStorage
   - Apply `data-theme` attribute to `<html>`

2. **Navbar Toggle** - Wire button to context

3. **CSS Variables** - Ensure all colors use CSS variables:
   ```css
   :root { --bg-primary: #fff; --text-primary: #000; }
   [data-theme="dark"] { --bg-primary: #1a1a2e; --text-primary: #fff; }
   ```

4. **Audit Components** - Check for hardcoded colors:
   - Dashboard
   - TaskDetail
   - ChatPanel
   - All cards/badges

## AC

- [ ] AC1: Toggle button switches between light/dark
- [ ] AC2: Theme persists on page refresh
- [ ] AC3: All pages render correctly in both themes
- [ ] AC4: No hardcoded bg/text colors outside CSS variables
- [ ] AC5: System preference respected on first visit

## Findings từ reviewer
- [ ] AC4 fails: indigo-200, indigo-300, emerald-600 compile to fixed Tailwind colors - missing CSS variable palette
