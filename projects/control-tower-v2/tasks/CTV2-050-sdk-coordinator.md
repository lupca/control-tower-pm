---
id: CTV2-050
title: "Implement SDK-Direct Coordinator"
status: done
priority: high
risk: normal
deadline: 2026-08-02
executor: "@gpt-5.6-sol"
dispatched: 2026-07-26
reviewer: null
files:
  - backend/app/services/coordinator.py
  - backend/app/services/providers/__init__.py
  - backend/app/services/providers/anthropic_adapter.py
  - backend/app/services/providers/google_adapter.py
  - backend/app/api/chat.py
  - backend/app/api/sessions.py
tests:
  - test_coordinator.py
  - test_providers.py
created: 2026-07-26
effort: 6h
updated: 2026-07-26
---

# CTV2-050: Implement SDK-Direct Coordinator

## Context

Research CTV2-047 recommends SDK-direct for coordinator (not CLI spawn):
- `anthropic` SDK for Claude
- `google-genai` SDK for Gemini
- PostgreSQL as canonical conversation store
- Keep CLI for executor/reviewer (different workload)

Current state: `backend/app/services/llm.py` already close to SDK-direct but needs refactoring.

## Objective

Implement hybrid architecture from CTV2-047:
- Coordinator: SDK-direct with provider adapters
- Executor/Reviewer: CLI spawn (unchanged)

## Deliverables

1. **CoordinatorService** (`backend/app/services/coordinator.py`)
   - Session/model selection
   - Canonical message persistence to PostgreSQL
   - Context-window budgeting
   - Turn-level retry/idempotency
   - Streaming normalization

2. **Provider adapters** (`backend/app/services/providers/`)
   - `anthropic_adapter.py` — Claude Messages API
   - `google_adapter.py` — Gemini API via google-genai
   - Common interface: `complete(messages, model, stream) -> Response`

3. **Provider router**
   - Model switch loads history from DB (cache miss but context preserved)
   - Same model = SDK prompt caching (~90% savings)

4. **Update chat endpoint** (`backend/app/api/chat.py`)
   - Use CoordinatorService instead of raw llm.py
   - Support model switching mid-session

## Architecture (from CTV2-047)

```
User → FastAPI → CoordinatorService → Provider Router
                      ↓                    ↓
                 PostgreSQL         Anthropic/Google SDK
                 (history)              (model call)
```

## AC

- [ ] AC1: CoordinatorService created with session management
- [ ] AC2: Anthropic adapter wraps claude Messages API
- [ ] AC3: Google adapter wraps google-genai API
- [ ] AC4: Provider router selects adapter by model name
- [ ] AC5: Model switch preserves context from PostgreSQL
- [ ] AC6: Streaming works for both providers
- [ ] AC7: Token usage recorded to LLMUsage table (integrate with CTV2-049)
- [ ] AC8: Tests verify both providers and model switching
