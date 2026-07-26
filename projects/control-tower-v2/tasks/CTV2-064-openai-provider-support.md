---
id: CTV2-064
title: "Add OpenAI Provider Support for Coordinator"
status: completed
priority: high
risk: normal
deadline: 2026-08-03
executor: "@gpt-5.6-luna-high"
reviewer: "@claude-opus"
result_ref: "f741511"
depends_on: []
files:
  - backend/app/services/providers/openai_adapter.py
  - backend/app/services/providers/__init__.py
  - backend/app/services/coordinator.py
  - backend/app/services/llm_client.py
flows: [coordinator-invoke, chat-session]
tests:
  - backend/tests/unit/test_openai_adapter.py
  - backend/tests/integration/test_openai_coordinator.py
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: high
prediction_factors:
  score: 0.85
  deductions:
    - "follows existing adapter pattern (-0.0)"
    - "new dependency (openai SDK) (-0.1)"
    - "needs API key handling (-0.05)"
created: 2026-07-27
updated: 2026-07-27
planned: 2026-07-27
---

# CTV2-064: Add OpenAI Provider Support for Coordinator

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Context

Hiện tại ProviderRouter chỉ support `anthropic` (Claude) và `google` (Gemini). User không thể dùng OpenAI models (GPT-4, GPT-4o, etc.) làm coordinator. Error: `Cannot infer provider for coordinator model 'gpt-*'`.

## Tiêu chí nghiệm thu (AC)

- [x] AC1: Implement `OpenAIAdapter` class theo `CoordinatorProvider` protocol
  - `name = "openai"`
  - `complete()` method với streaming support
  - Proper message format conversion (canonical → OpenAI)
  - Usage extraction (prompt_tokens, completion_tokens)
- [x] AC2: Update `ProviderRouter.provider_name()` để detect OpenAI models
  - `gpt-*` → `openai`
  - `o1-*` → `openai` (reasoning models)
  - `chatgpt-*` → `openai`
- [x] AC3: Register `OpenAIAdapter` trong `ProviderRouter.__init__`
- [x] AC4: Add `OPENAI_API_KEY` env var handling trong `llm_client.py`
- [x] AC5: Unit tests cho OpenAIAdapter
  - Test message conversion
  - Test streaming
  - Test usage extraction
  - Test error handling (rate limit, invalid key)
- [x] AC6: Integration test với mock OpenAI API
- [x] AC7: Update `__init__.py` exports

## Verification

```bash
# Unit tests
docker compose exec backend pytest tests/unit/test_openai_adapter.py -v

# Integration tests  
docker compose exec backend pytest tests/integration/test_openai_coordinator.py -v

# Manual test (requires OPENAI_API_KEY)
# 1. Add agent với model "gpt-4o" trong Agents page
# 2. Select model trong chat
# 3. Send message, verify response
```

## Technical Reference

### Existing Pattern (AnthropicAdapter)

```python
class AnthropicAdapter:
    name = "anthropic"
    
    def __init__(self, client=None, *, api_key=None):
        self._client = client
        self._api_key = api_key or ANTHROPIC_API_KEY
    
    async def complete(self, messages, model, stream=False, **kwargs) -> ProviderResponse:
        # Convert messages to provider format
        # Call SDK
        # Return normalized ProviderResponse
```

### OpenAI Message Format

```python
# Canonical format
{"role": "system", "content": "..."}
{"role": "user", "content": "..."}
{"role": "assistant", "content": "..."}

# OpenAI format (same, but tools differ)
{"role": "system", "content": "..."}
{"role": "user", "content": "..."}
{"role": "assistant", "content": "..."}
```

### OpenAI SDK Usage

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=api_key)
response = await client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    max_tokens=max_tokens,
    temperature=temperature,
    stream=stream,
)

# Usage extraction
response.usage.prompt_tokens
response.usage.completion_tokens
```

## Plan

### Phase 1: Dependencies & Config (AC4)
1. Add `openai>=1.0.0` to `requirements.txt`
2. Add `OPENAI_API_KEY` to `llm_client.py`:
   ```python
   OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
   ```
3. Add to `.env.example`

### Phase 2: OpenAIAdapter Implementation (AC1)
1. Create `backend/app/services/providers/openai_adapter.py`:
   - Class `OpenAIAdapter` implementing `CoordinatorProvider`
   - `name = "openai"`
   - `__init__(self, client=None, *, api_key=None)`
   - `_get_client()` - lazy init AsyncOpenAI
   - `render_messages()` - convert canonical to OpenAI format
   - `complete()` - call OpenAI API, return ProviderResponse
   - Handle streaming via async generator

### Phase 3: Router Integration (AC2, AC3, AC7)
1. Update `coordinator.py` `ProviderRouter.provider_name()`:
   ```python
   if any(x in normalized for x in ("gpt", "o1-", "chatgpt")):
       return "openai"
   ```
2. Register in `ProviderRouter.__init__`:
   ```python
   "openai": OpenAIAdapter(),
   ```
3. Update `providers/__init__.py` exports

### Phase 4: Testing (AC5, AC6)
1. Unit tests (`test_openai_adapter.py`):
   - `test_render_messages_basic`
   - `test_render_messages_with_system`
   - `test_complete_non_streaming`
   - `test_complete_streaming`
   - `test_usage_extraction`
   - `test_error_handling_rate_limit`
   - `test_error_handling_invalid_key`
2. Integration tests (`test_openai_coordinator.py`):
   - Mock OpenAI API responses
   - Test full coordinator flow with OpenAI model

## Sub-tasks

- [x] Add `openai` to requirements.txt
- [x] Create `openai_adapter.py` với `OpenAIAdapter` class
- [x] Update `ProviderRouter.provider_name()` cho GPT detection
- [x] Register OpenAIAdapter trong ProviderRouter
- [x] Add `OPENAI_API_KEY` env var
- [x] Write unit tests
- [x] Write integration tests
- [x] Update `__init__.py` exports
