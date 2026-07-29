---
id: CTV2-054
title: "Coordinator Model Settings (via Agents)"
status: done
dispatched: 2026-07-26
result_ref: e9f1fb6
in_review: 2026-07-26
priority: high
risk: normal
deadline: 2026-08-02
executor: "@gpt-5.6-luna-high"
reviewer: "@claude-opus"
files:
  - backend/app/api/agents.py
  - backend/app/db/models.py
  - frontend/src/pages/Agents.tsx
  - frontend/src/components/agents/AgentForm.tsx
  - frontend/src/components/chat/ModelSelector.tsx
tests:
  - backend/tests/test_agents.py
created: 2026-07-26
effort: 3h
updated: 2026-07-26
plan_approved: 2026-07-26
---

# CTV2-054: Coordinator Model Settings (via Agents)

## Context

CTV2-052 added ModelSelector with hardcoded models. User pointed out: coordinator models ARE agents — should use existing `agents` table with `role: "coordinator"` instead of creating new table.

## Objective

Use existing Agents infrastructure for coordinator model management. Add `is_default` field, filter by role, update ModelSelector to fetch from API.

## Changes Required

### 1. Add `is_default` to Agent model

```python
# backend/app/db/models.py
class Agent(Base):
    ...
    is_default = Column(Boolean, default=False)  # NEW: for coordinator default
```

### 2. Seed coordinator agents

Add to migration or seed script:
```python
agents = [
    Agent(id="claude-sonnet", name="Claude Sonnet", role="coordinator", 
          model="claude-sonnet-4-20250514", cli="claude", is_default=True),
    Agent(id="claude-opus", name="Claude Opus", role="coordinator",
          model="claude-opus-4-5-20251101", cli="claude"),
    Agent(id="gemini-pro", name="Gemini Pro", role="coordinator",
          model="gemini-2.5-pro", cli="agy"),
    Agent(id="gemini-flash", name="Gemini Flash", role="coordinator",
          model="gemini-2.5-flash", cli="agy"),
]
```

### 3. API endpoint for coordinator agents

```python
# GET /api/agents?role=coordinator
# Already exists, just need to filter by role
```

### 4. Update Agents page UI

- Filter tabs: All | Executors | Reviewers | Coordinators
- Add/Edit form includes `is_default` toggle for coordinators
- Set default action (unset others first)

### 5. Update ModelSelector

- Fetch `GET /api/agents?role=coordinator&status=idle` (or enabled)
- Map agent fields to dropdown options
- Pre-select `is_default=true` agent

## AC

- [x] AC1: Agent model has `is_default` field with migration
- [x] AC2: 4 coordinator agents seeded in DB
- [x] AC3: GET /api/agents?role=coordinator returns only coordinators
- [x] AC4: Agents page shows Coordinator tab/filter
- [x] AC5: Can add/edit coordinator agent via existing form
- [x] AC6: Can set default coordinator (unsets others)
- [x] AC7: ModelSelector fetches coordinators from API
- [x] AC8: Default coordinator pre-selected for new sessions
- [x] AC9: Tests cover coordinator filtering

## Plan

1. **Add `is_default` to Agent model** + migration

2. **Add coordinator filter to agents API**
   - `GET /api/agents?role=coordinator`
   - `POST /api/agents/{id}/set-default`

3. **Seed 4 coordinator agents**

4. **Update Agents page**
   - Role filter/tabs
   - is_default toggle in form

5. **Update ModelSelector**
   - useQuery for `/api/agents?role=coordinator`
   - Map to dropdown options
