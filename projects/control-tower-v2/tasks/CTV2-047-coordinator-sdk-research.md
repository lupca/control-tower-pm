---
id: CTV2-047
title: "Research: Coordinator SDK Options (Claude/Antigravity)"
status: dispatched
priority: high
risk: low
deadline: 2026-07-30
executor: "@gpt-5.6-sol"
dispatched: 2026-07-26
reviewer:
files:
  - docs/coordinator-sdk-architecture.md
tests:
  - SDK comparison complete
  - Architecture recommendation provided
  - Token caching analysis included
created: 2026-07-26
effort: 4h
---

# CTV2-047: Coordinator SDK Options Research

## Objective

Research using closed-model SDKs (Claude SDK, Antigravity SDK) for the coordinator instead of CLI spawning. Enable model switching while preserving context.

## Current State

Coordinator uses CLI tools:
- `claude` CLI - Claude models
- `agy` CLI - Gemini models (Antigravity)
- `codex` CLI - GPT models

Each spawn is a new process with no shared context.

## Research Areas

### 1. SDK Options

**Claude SDK (Anthropic)**
```python
from anthropic import Anthropic
client = Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    messages=[...],
    # Token caching with prompt_caching
)
```

**Antigravity SDK (Gemini)**
```python
# Research: What's the Antigravity SDK API?
# How does it handle context/caching?
```

### 2. Requirements

1. **Context Preservation**: Store conversation history in DB, load on model switch
2. **Token Caching**: 
   - Same model throughout = SDK prompt caching works
   - Model switch = accept cache miss, reload from DB
3. **Model Selection**: User chooses coordinator model per-session or per-task

### 3. Architecture Options

**Option A: SDK Direct**
```
User → FastAPI → SDK Client → Model
                    ↓
              PostgreSQL (history)
```
- Pro: Token caching, lower latency
- Con: Need SDK for each provider

**Option B: CLI Spawn (current)**
```
User → FastAPI → subprocess(claude/agy/codex) → Model
```
- Pro: Simple, works with any CLI
- Con: No token caching, process overhead

**Option C: Hybrid**
- Use SDK for primary coordinator (cached)
- Fall back to CLI for model switch (uncached)

### 4. Token Caching Analysis

| Scenario | CLI | SDK |
|----------|-----|-----|
| Same model, long conversation | No cache | Cached (~90% savings) |
| Model switch mid-session | N/A | Cache miss, reload |
| New session | No cache | Cache miss |

## Deliverable

`docs/coordinator-sdk-architecture.md` with:
- SDK API comparison (Claude vs Antigravity)
- Token caching deep dive
- Recommended architecture
- Implementation plan

## AC

- [ ] AC1: Claude SDK capabilities documented
- [ ] AC2: Antigravity SDK capabilities documented
- [ ] AC3: Token caching comparison (CLI vs SDK)
- [ ] AC4: Architecture recommendation with diagram
- [ ] AC5: Context preservation strategy for model switching
