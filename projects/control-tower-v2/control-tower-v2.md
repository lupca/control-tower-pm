---
project: control-tower-v2
full_name: "Control Tower V2 - LangGraph Redesign"
repo_root: /home/lupca/projects/control-tower-v2
repo_url: null
task_prefix: CTV2
next_task_id: 46
created: 2026-07-26
updated: 2026-07-26
---

# Control Tower V2 - LangGraph Redesign

Thiết kế lại hệ thống Control Tower sử dụng LangGraph (Python) để giảm token consumption ~80% trong khi giữ chất lượng output.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      Source of Truth: PostgreSQL                │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   tasks     │  │  sessions   │  │  audit_log  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│         │                │                │                     │
│         └────────────────┴────────────────┘                     │
│                          │                                      │
│         ┌────────────────┼────────────────┐                     │
│         ▼                ▼                ▼                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  LangGraph  │  │  Chainlit   │  │  Streamlit  │              │
│  │  Pipeline   │  │  Chat UI    │  │  Dashboard  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

## Key Design Decisions

1. **Database-first**: PostgreSQL là source of truth, không còn File-Over-API
2. **LangGraph orchestration**: Python state machine, chỉ gọi LLM khi cần judgment
3. **Chainlit chat**: Open-source chat UI với native LangGraph integration
4. **Streamlit dashboard**: View-only task management

## Tiến độ
| Trạng thái | Số task |
|:---|---:|
| done | 9 |
*(Cập nhật bởi `/report`)*

## Tasks
- [[CTV2-001-database-schema]] — Database Schema + Alembic Migrations (dispatched)
- [[CTV2-002-fastapi-crud]] — FastAPI CRUD + Pydantic Schemas (dispatched)
- [[CTV2-003-langgraph-core]] — LangGraph Core - State + Nodes + Builder (dispatched)
- [[CTV2-004-gate-implementations]] — Gate Implementations (dispatched)
- [[CTV2-005-mcp-integration]] — MCP Integration - code-review-graph Client (dispatched)
- [[CTV2-006-chainlit-chat]] — Chainlit Chat UI Integration (dispatched)
- [[CTV2-007-streamlit-dashboard]] — Streamlit Task Dashboard (dispatched)
- [[CTV2-008-docker-deployment]] — Docker Compose + Deployment (dispatched)
- [[CTV2-009-integration-tests]] — Integration Tests - Full Flow (dispatched)

## Tech Stack
- **Backend:** FastAPI + SQLAlchemy + Alembic
- **Orchestration:** LangGraph
- **Database:** PostgreSQL
- **Chat UI:** Chainlit
- **Dashboard:** Streamlit
- **LLM:** Claude API (direct, not through LangChain)
- **Deployment:** Docker Compose

## Quy tắc phê duyệt riêng (Project Gates)
- Mọi DB migration phải có rollback script
- LLM calls phải được wrap trong try/catch với fallback
- State changes phải atomic (transaction)
- Tests phải cover gate transitions

## References
| Tài liệu | Path | Mô tả |
|:---|:---|:---|
| Architecture Design | `docs/architecture.md` | Chi tiết kiến trúc |
| API Spec | `docs/api-spec.md` | OpenAPI endpoints |
