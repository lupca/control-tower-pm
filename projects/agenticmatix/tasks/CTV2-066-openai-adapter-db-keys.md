---
id: CTV2-066
title: "Fix OpenAI Adapter: Use DB API Keys + Support OpenAI-Compatible APIs"
status: done
priority: urgent
risk: normal
deadline: 2026-07-28
executor: "@gpt-5.6-luna-high"
reviewer: "@claude-opus"
result_ref: "5e46299"
depends_on: [CTV2-064]
files:
  - backend/app/db/models.py
  - backend/app/services/providers/openai_adapter.py
  - backend/app/services/coordinator.py
  - backend/alembic/versions/
flows: [coordinator-invoke, chat-session]
tests:
  - backend/tests/unit/test_openai_adapter.py
  - backend/tests/integration/test_openai_coordinator.py
dispatched: 2026-07-27
in_review: 2026-07-27
verdict: pass
verdict_date: 2026-07-27
predicted_success: high
prediction_factors:
  score: 0.85
  deductions:
    - "requires migration (-0.1)"
    - "touches coordinator flow (-0.05)"
created: 2026-07-27
updated: 2026-07-27
planned: 2026-07-27
completed: 2026-07-27
---

# CTV2-066: Fix OpenAI Adapter: Use DB API Keys + Support OpenAI-Compatible APIs

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Context

CTV2-064 sai plan: dùng `OPENAI_API_KEY` env var thay vì lấy từ DB per-agent. CTV2-061 đã implement API key storage trong DB. Cần fix để:
1. Adapter lấy API key từ agent record trong DB
2. Support custom `base_url` cho OpenAI-compatible APIs (SiliconFlow, Together, Groq, etc.)

## Tiêu chí nghiệm thu (AC)

- [x] AC1: Add `base_url` column to Agent model
  - Migration: `ALTER TABLE agents ADD COLUMN base_url VARCHAR(500)`
  - Nullable, default NULL (uses OpenAI default)
- [x] AC2: Update `OpenAIAdapter` để nhận `api_key` và `base_url` từ caller
  - Remove dependency on `OPENAI_API_KEY` env var
  - Constructor: `__init__(self, *, api_key: str, base_url: str | None = None)`
  - Pass to `AsyncOpenAI(api_key=api_key, base_url=base_url)`
- [x] AC3: Update `ProviderRouter` và `CoordinatorService` để pass agent's api_key/base_url
  - Lookup agent record khi resolving provider
  - Pass credentials to adapter
- [x] AC4: Frontend UI cho base_url trong Agent settings
  - Add field trong Agent form
  - Placeholder: "https://api.siliconflow.cn/v1" hoặc để trống cho OpenAI
- [x] AC5: Test với OpenAI-compatible API (SiliconFlow, etc.)
- [x] AC6: Remove `OPENAI_API_KEY` từ env nếu không còn dùng

## Verification

```bash
# Run tests
docker compose exec backend pytest tests/unit/test_openai_adapter.py -v
docker compose exec backend pytest tests/integration/test_openai_coordinator.py -v

# Manual test
# 1. Add agent với model "Qwen/Qwen2.5-72B-Instruct"
# 2. Set base_url: "https://api.siliconflow.cn/v1"
# 3. Set api_key: <siliconflow key>
# 4. Select model, send message
```

## Technical Design

### Migration

```python
def upgrade():
    op.add_column('agents', sa.Column('base_url', sa.String(500), nullable=True))

def downgrade():
    op.drop_column('agents', 'base_url')
```

### Adapter Change

```python
class OpenAIAdapter:
    def __init__(self, *, api_key: str, base_url: str | None = None):
        self._api_key = api_key
        self._base_url = base_url
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(
                api_key=self._api_key,
                base_url=self._base_url,  # None = use OpenAI default
                max_retries=0,
            )
        return self._client
```

### Coordinator Change

```python
def _get_adapter(self, agent: Agent) -> CoordinatorProvider:
    provider = self.provider_name(agent.model)
    if provider == "openai":
        return OpenAIAdapter(api_key=agent.api_key, base_url=agent.base_url)
    # ... similar for other providers
```

## Plan

### Phase 1: Migration (AC1)
1. Create Alembic migration:
   - Add `base_url` column to `agents` table
   - VARCHAR(500), nullable, default NULL

### Phase 2: Backend Adapter Fix (AC2, AC3)
1. Update `OpenAIAdapter`:
   - Change constructor to require `api_key`, optional `base_url`
   - Remove env var fallback
   - Pass `base_url` to `AsyncOpenAI()`
2. Update `ProviderRouter`:
   - Accept agent record or credentials
   - Instantiate adapter with agent's api_key/base_url
3. Update `CoordinatorService`:
   - Lookup agent when handling chat
   - Pass credentials to provider

### Phase 3: Frontend (AC4)
1. Update Agent form:
   - Add `base_url` input field
   - Label: "API Base URL (optional)"
   - Placeholder: "https://api.siliconflow.cn/v1"
   - Help text: "Leave empty for OpenAI, or enter URL for compatible APIs"

### Phase 4: Testing (AC5, AC6)
1. Update unit tests for new adapter signature
2. Test with mock OpenAI-compatible API
3. Remove `OPENAI_API_KEY` from env if no longer needed

## Sub-tasks

- [x] Create migration cho `base_url` column
- [x] Update `OpenAIAdapter` constructor
- [x] Update `ProviderRouter`/`CoordinatorService` để pass credentials
- [x] Update frontend Agent form
- [x] Update/add tests
- [x] Remove env var fallback
