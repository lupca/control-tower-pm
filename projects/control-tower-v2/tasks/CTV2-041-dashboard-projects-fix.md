---
id: CTV2-041
title: "Fix Dashboard Project Progress section"
status: in-review
priority: medium
risk: low
deadline: 2026-07-29
executor: "@gpt-5.6-luna-high"
reviewer: "@gpt-5.6-sol"
result_ref: 1b0209a
in_review: 2026-07-26
files:
  - frontend/src/pages/Dashboard.tsx
  - frontend/src/components/dashboard/ProjectCards.tsx
  - backend/app/api/stats.py
tests:
  - Dashboard Project Progress shows real projects
  - API returns projectProgress array
created: 2026-07-26
effort: 2h
---

# CTV2-041: Fix Dashboard Project Progress

## Problem

Dashboard "Project Progress & Status" section shows "No projects found" despite /api/projects returning 17 projects.

## Root Cause

Dashboard fetches from `/api/stats/overview` which doesn't include `projectProgress` field.
ProjectCards component expects `projectProgress: ProjectProgress[]` in the response.

## Fix

Option 1: Add `projectProgress` to stats overview API
Option 2: Dashboard fetches projects separately from `/api/projects`

## AC

- [ ] AC1: Dashboard shows project cards with completion rates
- [ ] AC2: At least top 5 projects displayed
- [ ] AC3: Clicking project card navigates to project detail
