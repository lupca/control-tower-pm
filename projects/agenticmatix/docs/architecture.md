# Control Tower V2 - Architecture Design

## 1. Overview

Control Tower V2 là phiên bản redesign của hệ thống task coordination, sử dụng LangGraph (Python) thay vì Claude Code để giảm token consumption.

### Goals
- Giảm token ~80% so với hiện tại
- Giữ nguyên chất lượng output
- Database-first (PostgreSQL) thay vì File-Over-API
- Web chat interface + Dashboard

### Non-Goals
- Backward compatibility với Markdown files
- Multi-tenant support (phase 1)

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Users                                   │
│                                                                 │
│  ┌─────────────┐                        ┌─────────────┐         │
│  │  Chat UI    │                        │  Dashboard  │         │
│  │  (Chainlit) │                        │ (Streamlit) │         │
│  │  :8080      │                        │  :8501      │         │
│  └──────┬──────┘                        └──────┬──────┘         │
└─────────┼──────────────────────────────────────┼────────────────┘
          │                                      │
          ▼                                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend (:8000)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Message Router                       │    │
│  │  /command → LangGraph Pipeline (0 tokens)               │    │
│  │  question? → Claude API (tokens)                        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           │                                     │
│           ┌───────────────┴───────────────┐                     │
│           ▼                               ▼                     │
│  ┌─────────────────┐             ┌─────────────────┐            │
│  │   LangGraph     │             │   Claude API    │            │
│  │   StateGraph    │             │   (Haiku/Sonnet)│            │
│  │                 │             │                 │            │
│  │  ┌───────────┐  │             └─────────────────┘            │
│  │  │Spec Gate  │  │                                            │
│  │  │Plan Gate  │  │                                            │
│  │  │Dispatch   │  │                                            │
│  │  │Review     │  │                                            │
│  │  │Verdict    │  │                                            │
│  │  └───────────┘  │                                            │
│  └────────┬────────┘                                            │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    PostgreSQL                           │    │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌───────────┐   │    │
│  │  │ tasks   │  │sessions │  │audit_log│  │checkpoints│   │    │
│  │  └─────────┘  └─────────┘  └─────────┘  └───────────┘   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External Services                            │
│                                                                 │
│  ┌─────────────────┐             ┌─────────────────┐            │
│  │ code-review-    │             │  Target Repos   │            │
│  │ graph (MCP)     │             │  (execution)    │            │
│  └─────────────────┘             └─────────────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 3. Data Model

### tasks table
```sql
CREATE TABLE tasks (
    id VARCHAR(20) PRIMARY KEY,      -- "CTV2-001"
    project VARCHAR(50) NOT NULL,
    title TEXT NOT NULL,
    status VARCHAR(20) NOT NULL,     -- todo|dispatched|in-review|done|changes-requested
    priority VARCHAR(10),
    risk VARCHAR(10),
    executor VARCHAR(50),
    reviewer VARCHAR(50),
    acceptance_criteria JSONB,
    files JSONB,
    tests JSONB,
    flows JSONB,
    plan TEXT,
    result_ref VARCHAR(100),
    findings JSONB,
    verdict VARCHAR(10),
    predicted_success VARCHAR(10),
    prediction_factors JSONB,
    deadline DATE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    dispatched_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

### sessions table
```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY,
    task_id VARCHAR(20) REFERENCES tasks(id),
    thread_id VARCHAR(100),          -- LangGraph checkpoint
    current_gate VARCHAR(20),
    messages JSONB,                  -- Chat history
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### audit_log table
```sql
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(20),
    action VARCHAR(50) NOT NULL,
    actor VARCHAR(50),
    details JSONB,
    created_at TIMESTAMP
);
```

## 4. LangGraph State Machine

### TaskState
```python
class TaskState(BaseModel):
    # Input
    raw_input: str
    
    # Identity
    task_id: str | None
    project: str | None
    title: str | None
    
    # Workflow
    current_gate: GateType
    status: str
    mode: Mode
    
    # Gate outputs
    acceptance_criteria: list[str]
    files: list[str]
    tests: list[str]
    plan: str | None
    
    # Actors
    executor: str | None
    reviewer: str | None
    
    # Review
    result_ref: str | None
    findings: list[str]
    verdict: str | None
    
    # Human-in-loop
    awaiting_approval: bool
```

### Gate Flow
```
START → parse_input → query_graph → spec_gate → [approval] →
        plan_gate → [approval] → dispatch_gate → END (dispatched)

... executor works externally ...

resume → review_order_gate → END (in-review)

... reviewer works externally ...

resume → verdict_gate → END (done | changes-requested)
```

## 5. Token Optimization Strategy

### What needs LLM (tokens)
| Operation | Model | Est. tokens |
|-----------|-------|-------------|
| Validate spec + generate AC | Haiku | ~500 |
| Write implementation plan | Sonnet | ~2000 |
| Answer user questions | Sonnet | ~1000 |

### What doesn't need LLM (0 tokens)
- Parse command input
- Query code-review-graph (MCP)
- Route messages
- Gate transitions
- Update database
- Generate dispatch command
- Create review sheet
- Apply verdict

### Estimated savings
- Current (Claude Code): ~25K tokens/task
- LangGraph: ~4K tokens/task
- Savings: **84%**

## 6. Human-in-the-Loop

### Modes
- **bypass**: Auto-approve all gates
- **supervised**: Pause at each gate for approval
- **plan-only**: Stop at Dispatch Gate

### Implementation
```python
from langgraph.types import interrupt

def approval_gate(state: TaskState) -> dict:
    if state.mode == Mode.BYPASS:
        return {"awaiting_approval": False}
    
    decision = interrupt({
        "gate": state.current_gate,
        "summary": f"Approve {state.task_id}?"
    })
    
    return {"awaiting_approval": decision != "approve"}
```

## 7. Four-Eyes Enforcement

Critical invariant: `reviewer != executor`

```python
def verdict_gate(state: TaskState) -> dict:
    if state.reviewer == state.executor:
        raise FourEyesViolation(
            f"reviewer={state.reviewer} cannot be same as executor"
        )
    # ... proceed with verdict
```

This is enforced at:
1. Verdict Gate (primary)
2. Database constraint (secondary)
3. API validation (tertiary)

## 8. MCP Integration

```python
async def query_graph(repo_root: str, query: str) -> dict:
    async with MCPClient("code-review-graph") as client:
        return await client.call("semantic_search_nodes_tool", {
            "repo_root": repo_root,
            "query": query
        })
```

Used by:
- Spec Gate: find affected files, existing tests
- Plan Gate: get context for planning

## 9. Deployment

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:16-alpine
    
  backend:
    build: ./backend
    depends_on: [db]
    
  chat:
    build: ./frontend/chat
    depends_on: [backend]
    
  dashboard:
    build: ./frontend/dashboard
    depends_on: [backend]
```

Ports:
- 5432: PostgreSQL
- 8000: FastAPI
- 8080: Chainlit Chat
- 8501: Streamlit Dashboard
