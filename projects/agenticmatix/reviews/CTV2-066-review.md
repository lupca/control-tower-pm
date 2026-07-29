---
id: CTV2-066
task_path: projects/control-tower-v2/tasks/CTV2-066-openai-adapter-db-keys.md
project: control-tower-v2
result_ref: "5e46299"
executor: "@gpt-5.6-luna-high"
reviewer: "@claude-opus"
status: complete
issued: 2026-07-27
verdict: pass
verdict_date: 2026-07-27
---

# Phiếu Review: CTV2-066 — Fix OpenAI Adapter: Use DB API Keys + OpenAI-Compatible APIs

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-066-openai-adapter-db-keys.md`
- Result-ref: `5e46299`
- Executor: @gpt-5.6-luna-high
- Reviewer: @claude-opus
- Ngày phát phiếu: 2026-07-27

## Acceptance Criteria cần verify

- [x] AC1: Add `base_url` column to Agent model + migration
- [x] AC2: Update `OpenAIAdapter` để nhận `api_key` và `base_url` từ caller
- [x] AC3: Update `ProviderRouter`/`CoordinatorService` để pass agent credentials
- [x] AC4: Frontend UI cho base_url trong Agent settings (if applicable)
- [x] AC5: Test với OpenAI-compatible API pattern
- [x] AC6: Remove `OPENAI_API_KEY` env var dependency

## Definition of Done

- [x] Toàn bộ AC pass
- [x] Tests pass (258 passed, 0 failed)
- [x] No regression
- [x] Reviewer ≠ executor (@claude-opus ≠ @gpt-5.6-luna-high)

## Review Notes

### Verified Implementation

1. **Migration 014**: `base_url` VARCHAR(500), nullable column added to agents table
2. **OpenAIAdapter**: Constructor accepts `api_key` (required) and `base_url` (optional), passes both to AsyncOpenAI client, validates api_key not empty
3. **ProviderRouter.get()**: Accepts `agent` parameter, instantiates OpenAIAdapter with `decrypt_api_key(agent.api_key)` and `agent.base_url`
4. **Frontend**: AgentForm.tsx includes base_url input field, agent.ts type includes base_url
5. **Env cleanup**: OPENAI_API_KEY removed from config.py and .env.example

### Test Results

```
258 passed, 5 warnings in 17.33s
```

Key passing tests:
- `test_client_uses_explicit_credentials_and_base_url`
- `test_coordinator_resolves_openai_agent_credentials_from_db`

## Files changed (11 files, +117/-32)

- `backend/alembic/versions/014_agent_base_url.py` (new migration)
- `backend/app/db/models.py`
- `backend/app/schemas/agent.py`
- `backend/app/api/agents.py`
- `backend/app/api/sessions.py`
- `backend/app/services/coordinator.py`
- `backend/app/services/providers/openai_adapter.py`
- `backend/app/services/llm.py`
- `backend/app/services/llm_client.py`
- `backend/app/core/config.py`
- `.env.example`

## Trả kết quả

```
/verdict CTV2-066 <pass|changes> --reviewer @claude-opus --commit 5e46299 [--notes "..."]
```
