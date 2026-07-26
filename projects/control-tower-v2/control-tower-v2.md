---
project: control-tower-v2
full_name: "Control Tower V2 - LangGraph Redesign"
repo_root: /home/lupca/projects/control-tower-v2
repo_url: null
task_prefix: CTV2
next_task_id: 73
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
3. **Streamlit dashboard**: View-only task management

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
- [[CTV2-053-hierarchical-context-chat]] — Hierarchical Context Chat System (done, round 2)
- [[CTV2-055-chat-ui-research]] — Research: Chat UI với Hierarchical Context + Multi-Session (done)
- [[CTV2-056-chat-backend-schema]] — Chat UI Phase 1: Backend Schema + API (done)
- [[CTV2-057-chat-frontend-components]] — Chat UI Phase 2: Frontend Components (done)
- [[CTV2-058-chat-integration]] — Chat UI Phase 3: Integration + Global Chat (todo, unblocked)
- [[CTV2-059-chat-data-architecture-research]] — Research: Kiến trúc Data Manipulation cho User Chat (done)
- [[CTV2-060-hybrid-context-snapshot]] — Implement Hybrid Context Snapshot for User Chat (done)
- [[CTV2-061-agent-api-key-settings]] — Agent API Key Settings UI (done)
- [[CTV2-062-chat-markdown-rendering]] — Fix Chat UI Markdown Rendering (done)
- [[CTV2-063-headroom-library-research]] — Research: Headroom Library - Token Reduction & Task Quality (done)
- [[CTV2-064-openai-provider-support]] — Add OpenAI Provider Support for Coordinator (done)
- [[CTV2-065-headroom-mcp-compression]] — Implement Headroom Compression for MCP Responses (dispatched)
- [[CTV2-066-openai-adapter-db-keys]] — Fix OpenAI Adapter: Use DB API Keys + OpenAI-Compatible APIs (done)
- [[CTV2-067-markdown-linebreak-fix]] — Fix Markdown Line Breaks + Whitespace Handling (dispatched)
- [[CTV2-069-markdown-newlines-fix]] — Fix Markdown Rendering - Newlines Double-Encoded (dispatched)
- [[CTV2-070-openai-adapter-tool-calls]] — Fix OpenAI Adapter: Parse Tool Calls from API Response (dispatched)
- [[CTV2-071-default-model-from-db]] — Fix Chat Page: Load Default Model from DB (dispatched)
- [[CTV2-072-prompt-tool-refactor]] — Refactor Prompt System + Tool Execution Loop for API Mode (dispatched)

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
