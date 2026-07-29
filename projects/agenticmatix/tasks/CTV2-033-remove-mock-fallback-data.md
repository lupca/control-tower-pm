---
id: CTV2-033
title: "Remove mock/fallback data from frontend"
status: done
priority: medium
risk: low
deadline: 2026-07-28
executor:
reviewer:
depends_on: [CTV2-032]
files:
  - frontend/src/pages/Dashboard.tsx
  - frontend/src/pages/Agents.tsx
  - frontend/src/pages/Projects.tsx
  - frontend/src/pages/AgentDetail.tsx
  - frontend/src/pages/ProjectDetail.tsx
tests:
  - Frontend shows error state when API fails (not mock data)
  - No "fallback" or "mock" data patterns in code
created: 2026-07-26
updated: 2026-07-26
---

# CTV2-033: Remove Mock/Fallback Data

## Context

Frontend files contain fallback/mock data that displays when API fails. Now that API is working, remove these fallbacks and show proper error states instead.

## AC

- [ ] AC1: Dashboard.tsx - remove fallback stats, show error UI
- [ ] AC2: Agents.tsx - remove getFallbackAgents(), getFallbackStats()
- [ ] AC3: Projects.tsx - remove fallback project list
- [ ] AC4: AgentDetail.tsx - remove fallback tasks for demo
- [ ] AC5: ProjectDetail.tsx - remove fallback if no tasks

## Verification

```bash
# No fallback/mock patterns in production code
grep -rn "fallback\|mock" frontend/src --include="*.tsx" | grep -v "test\|spec"
# Should return empty or only error message strings
```
