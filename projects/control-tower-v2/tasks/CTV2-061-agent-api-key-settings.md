---
id: CTV2-061
title: "Agent API Key Settings UI"
status: done
priority: high
risk: normal
deadline: 2026-08-03
executor: "@gpt-5.6-luna-high"
reviewer: "@claude-opus"
result_ref: "fc921ed"
depends_on: []
files:
  - backend/app/db/models.py
  - backend/app/schemas/agent.py
  - backend/app/api/agents.py
  - backend/alembic/versions/
  - frontend/src/types/agent.ts
  - frontend/src/components/agents/AgentForm.tsx
  - frontend/src/pages/Agents.tsx
flows: []
tests:
  - backend/tests/test_agents.py
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: high
prediction_factors:
  score: 0.9
  deductions:
    - "no deductions — blast_radius: 7, within limit"
created: 2026-07-27
updated: 2026-07-27
plan_approved: 2026-07-27
---

# CTV2-061: Agent API Key Settings UI

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Context

Coordinator hiện tại có thể sử dụng cả agent CLI (claude, agy) và agent API key (direct SDK calls). Tuy nhiên, trang `/agents` settings chỉ config cho CLI agents — không có UI để config API key cho agents dùng direct API.

**Current architecture:**
- `Agent` model có field `cli` để chỉ định CLI tool (claude/agy/codex)
- API keys chỉ đọc từ env vars (`ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`)
- AgentForm không có input cho API key hay agent type (CLI vs API)

**Gap:**
- Không thể add agent mới với API key riêng (per-agent API key)
- Không phân biệt được agent CLI vs agent API-based
- Không validate API key trước khi save

## Tiêu chí nghiệm thu (AC)

- [x] AC1: Agent model có thêm fields: `agent_type` (enum: cli/api), `api_key` (encrypted), `provider` (anthropic/google/openai)
- [x] AC2: Alembic migration thêm columns mới với backward compatibility (nullable, default cli)
- [x] AC3: API key được encrypt trước khi lưu DB, decrypt khi read (sử dụng Fernet hoặc tương đương)
- [x] AC4: AgentForm có agent type selector (CLI / API) với conditional fields:
  - CLI type: hiện `cli` dropdown (claude/agy/codex)
  - API type: hiện `provider` dropdown + `api_key` input (masked)
- [x] AC5: API key input có password mask, toggle show/hide
- [x] AC6: Validation: API type requires api_key và provider; CLI type requires cli
- [x] AC7: API endpoint PATCH/POST không return api_key trong response (security)
- [x] AC8: Agents page list hiển thị type badge (CLI/API) cho mỗi agent
- [x] AC9: Backend tests cover encryption/decryption và validation

## Verification

```bash
# AC1-2: Check migration
cd /home/lupca/projects/control-tower-v2
alembic upgrade head
psql -c "SELECT column_name, data_type FROM information_schema.columns WHERE table_name='agents' AND column_name IN ('agent_type', 'api_key', 'provider');"

# AC3: Encryption test
pytest backend/tests/test_agents.py -k "encrypt" -v

# AC6-7: API validation test
pytest backend/tests/test_agents.py -k "api_key" -v

# AC9: Full test suite
pytest backend/tests/test_agents.py -v

# AC4-5-8: UI test (manual or E2E)
# Navigate to http://localhost:5173/agents, create API-type agent, verify masked input
```

## Technical Design

### 1. Database Schema Changes

```python
# backend/app/db/models.py
class AgentType(str, Enum):
    CLI = "cli"
    API = "api"

class Agent(Base):
    ...
    agent_type = Column(String(10), nullable=False, default="cli")
    api_key = Column(String(500), nullable=True)  # encrypted
    provider = Column(String(50), nullable=True)  # anthropic/google/openai
```

### 2. Encryption Utility

```python
# backend/app/services/crypto.py
from cryptography.fernet import Fernet

def encrypt_api_key(key: str) -> str: ...
def decrypt_api_key(encrypted: str) -> str: ...
```

### 3. Pydantic Schema Updates

```python
# backend/app/schemas/agent.py
class AgentCreate(BaseModel):
    agent_type: Literal["cli", "api"] = "cli"
    api_key: str | None = None  # input only, never returned
    provider: str | None = None
    
    @model_validator
    def validate_type_fields(self): ...

class Agent(BaseModel):
    agent_type: str
    provider: str | None
    has_api_key: bool  # indicator only, not actual key
```

### 4. Frontend AgentForm

```tsx
// AgentType selector
<RadioGroup value={agentType} onChange={setAgentType}>
  <Radio value="cli">CLI Tool</Radio>
  <Radio value="api">API Key</Radio>
</RadioGroup>

// Conditional fields
{agentType === "cli" && <CliSelect />}
{agentType === "api" && (
  <>
    <ProviderSelect />
    <ApiKeyInput type="password" />
  </>
)}
```

## Sub-tasks

- [ ] Add AgentType enum và update Agent model
- [ ] Create Alembic migration
- [ ] Implement crypto utility (encrypt/decrypt)
- [ ] Update Pydantic schemas với validation
- [ ] Update agents API endpoints (mask api_key in response)
- [ ] Add agent.ts TypeScript types
- [ ] Update AgentForm with type selector + conditional fields
- [ ] Add type badge to agent list/card
- [ ] Write backend tests for encryption và validation

## Plan

### Phase 1: Backend Schema + Migration (AC1-3, AC7, AC9)

1. **Create crypto utility** (`backend/app/services/crypto.py`)
   - Use `cryptography.fernet` với key from `ENCRYPTION_KEY` env var
   - `encrypt_api_key(key: str) -> str`
   - `decrypt_api_key(encrypted: str) -> str`
   - Unit tests in `backend/tests/test_crypto.py`

2. **Update Agent model** (`backend/app/db/models.py`)
   - Add `agent_type: String(10)` (default "cli")
   - Add `api_key: String(500)` (nullable, encrypted)
   - Add `provider: String(50)` (nullable)

3. **Create Alembic migration** (`backend/alembic/versions/xxx_add_agent_api_key_fields.py`)
   - `agent_type` default "cli" for existing rows
   - All new columns nullable for backward compatibility

4. **Update Pydantic schemas** (`backend/app/schemas/agent.py`)
   - `AgentCreate`: add `agent_type`, `api_key`, `provider` with validator
   - `Agent` response: replace `api_key` with `has_api_key: bool`
   - Validator: api type requires api_key + provider; cli type requires cli

5. **Update agents API** (`backend/app/api/agents.py`)
   - POST: encrypt api_key before save
   - PATCH: encrypt if api_key provided
   - GET: never return api_key, only has_api_key indicator
   - Add tests to `backend/tests/test_agents.py`

### Phase 2: Frontend UI (AC4-6, AC8)

6. **Update TypeScript types** (`frontend/src/types/agent.ts`)
   - Add `agent_type: "cli" | "api"`
   - Add `provider?: string`
   - Add `has_api_key?: boolean`
   - `api_key` only in create/update forms, never in read

7. **Update AgentForm** (`frontend/src/components/agents/AgentForm.tsx`)
   - Add RadioGroup for agent type (CLI / API)
   - Conditional rendering:
     - CLI: show existing `cli` dropdown
     - API: show `provider` dropdown + `api_key` password input
   - Toggle show/hide for password field
   - Form validation matching backend rules

8. **Update Agents page** (`frontend/src/pages/Agents.tsx`)
   - Add type badge to AgentCard (CLI/API với icon)
   - Filter/tab by agent_type (optional enhancement)

### Order of execution:

```
crypto.py → migration → models.py → schemas.py → agents.py (test)
         → agent.ts → AgentForm.tsx → Agents.tsx (test)
```
