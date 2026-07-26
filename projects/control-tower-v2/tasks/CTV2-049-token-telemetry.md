---
id: CTV2-049
title: "Implement Token Telemetry System"
status: done
priority: high
risk: normal
deadline: 2026-08-02
executor: "@gpt-5.6-sol"
dispatched: 2026-07-26
result_ref: "92b7fbc"
in_review: 2026-07-26
reviewer: "@claude-opus"
files:
  - backend/app/db/models.py
  - backend/app/services/llm_client.py
  - backend/app/api/stats.py
  - frontend/src/pages/Dashboard.tsx
tests:
  - test_token_telemetry.py
  - test_llm_usage.py
created: 2026-07-26
effort: 6h
updated: 2026-07-26
---

# CTV2-049: Implement Token Telemetry System

## Context

Gap analysis CTV2-046 noted:
- Token reduction target (80%) is UNVERIFIED
- V1 baseline: ~3,575 input tokens per cycle
- No current telemetry to measure V2 actual usage
- UI token values are absent or zero

## Objective

Implement token tracking to verify the 80% reduction target. Every LLM call must record usage.

## Deliverables

1. **LLMUsage model** (`backend/app/db/models.py`)
   ```python
   class LLMUsage(Base):
       id: int
       session_id: int (FK)
       task_id: int (FK, nullable)
       agent_run_id: int (FK, nullable)
       model: str
       provider: str  # anthropic, google, openai
       operation: str  # plan, dispatch, review, verdict, chat
       input_tokens: int
       output_tokens: int
       cached_tokens: int
       cost_usd: Decimal
       latency_ms: int
       created_at: datetime
   ```

2. **LLM client wrapper** (`backend/app/services/llm_client.py`)
   - Wrap all SDK calls (Anthropic, Google GenAI)
   - Extract and persist token counts from response
   - Calculate cost based on model pricing

3. **Stats API** (`backend/app/api/stats.py`)
   - `GET /api/stats/tokens` - aggregate by session/task/operation
   - `GET /api/stats/tokens/comparison` - V2 vs V1 baseline

4. **Dashboard widget** (`frontend/src/pages/Dashboard.tsx`)
   - Show total tokens used
   - Show reduction % vs V1 baseline
   - Breakdown by operation type

## AC

- [ ] AC1: LLMUsage model created with all fields
- [ ] AC2: All LLM calls (coordinator, executor, reviewer) record usage
- [ ] AC3: Token counts extracted from SDK responses
- [ ] AC4: Cost calculation based on model pricing
- [ ] AC5: Stats API returns aggregated usage
- [ ] AC6: Dashboard shows token usage and reduction %
- [ ] AC7: Comparison against V1 baseline (3,575 tokens/cycle)
- [ ] AC8: Tests verify telemetry recording
