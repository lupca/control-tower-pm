---
project: control-tower-v2
full_name: "Control Tower V2 - LangGraph Redesign"
repo_root: /home/lupca/projects/control-tower-v2
repo_url: null
task_prefix: CTV2
next_task_id: 109
created: 2026-07-26
updated: 2026-07-27
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
│         ┌────────────────┴────────────────┐                     │
│         ▼                                 ▼                     │
│  ┌─────────────┐                   ┌─────────────┐              │
│  │  LangGraph  │                   │   React     │              │
│  │  Pipeline   │◄──── FastAPI ────►│  Frontend   │              │
│  └─────────────┘                   └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

## Key Design Decisions

1. **Database-first**: PostgreSQL là source of truth, không còn File-Over-API
2. **LangGraph orchestration**: Python state machine, chỉ gọi LLM khi cần judgment
3. **React SPA**: Full-featured dashboard + chat UI với hierarchical context

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
- [[CTV2-073-think-tag-parser-tool-display]] — Parse <think> tags + Collapsible Thought Process UI + Tool Usage Display (done, round 2)
- [[CTV2-074-shared-pagination-component]] — Create Shared Pagination Component (done)
- [[CTV2-075-agentic-os-db-access-research]] — Research: Agentic OS Full DB Access Architecture (done, ADR-001)
- [[CTV2-076-tool-system-audit-research]] — Research: Tool System Audit & Unified Design Strategy (done)
- [[CTV2-077-tool-registry-ssot]] — Tool Registry: Single Source of Truth (todo, ADR-001 P1a)
- [[CTV2-078-cache-aware-context-layout]] — Cache-aware Context Layout (todo, ADR-001 P1b)
- [[CTV2-079-remove-legacy-sdk-adapters]] — Xoá legacy SDK adapters Anthropic/Google (todo, ADR-001 P1c)
- [[CTV2-080-system-state-snapshot-querydb]] — System State Snapshot + query_db (todo, ADR-001 P2a)
- [[CTV2-081-load-tools-meta-tool]] — load_tools Meta-tool cho OpenAI (todo, ADR-001 P2b)
- [[CTV2-082-entity-crud-tools]] — Entity CRUD Tools + Gate Wiring (todo, ADR-001 P2c)
- [[CTV2-083-settings-kv-update-settings]] — Settings KV + update_settings (todo, ADR-001 P2d)
- [[CTV2-084-fastmcp-cli-projection]] — FastMCP Projection cho Coordinator Chat CLI (todo, ADR-001 P3)
- [[CTV2-085-ui-tool-palette]] — UI Tool Palette (todo, ADR-001 P4)
- [[CTV2-086-agentrun-kind-review-role]] — AgentRun.kind/agent_role + nới expected_status (todo, autonomy #1b)
- [[CTV2-087-request-review-tool-review-run]] — request_review tool + Review Run thật (todo, autonomy #1)
- [[CTV2-088-idempotency-key-attempt-nonce]] — Sửa idempotency, chặn kẹt im lặng (todo, autonomy #2b)
- [[CTV2-089-orchestration-driver-advance-task]] — Orchestration Driver advance_task (todo, autonomy #2)
- [[CTV2-090-research-tools-graph-mcp-wiring]] — Research tools: nối GraphClient/MCPClient (todo, autonomy #3b)
- [[CTV2-091-spec-plan-step-real-gate]] — Spec/Plan step thật + siết verdict theo AC (todo, autonomy #3)
- [[CTV2-092-create-task-project-scope-id]] — create_task project scope + ID an toàn (todo, autonomy #4)
- [[CTV2-093-autonomy-policy]] — Autonomy policy Settings + project override (todo, autonomy #5)
- [[CTV2-094-task-dependencies-dag]] — task_dependencies + dependency check (todo, autonomy #5b)
- [[CTV2-095-snapshot-last-tool-result-pruning]] — Snapshot cuối prefix + prune tool result (todo, autonomy #6)
- [[CTV2-096-llm-compaction-token-threshold]] — Compaction LLM theo ngưỡng token (todo, autonomy #6)
- [[CTV2-097-sub-session-per-task]] — Sub-session per task (todo, autonomy #6)
- [[CTV2-098-gate-notification-global-inbox]] — Thông báo gate vào global chat (todo, autonomy #7)
- [[CTV2-099-result-ref-accuracy]] — result_ref chính xác (todo, autonomy #9)
- [[CTV2-100-remove-langgraph-runtime]] — Bỏ LangGraph khỏi runtime (todo, autonomy #8)
- [[CTV2-101-tool-iteration-budget]] — Ngân sách tool-iteration coordinator (todo, autonomy)
- [[CTV2-102-review-result-schema]] — Review result schema JSON (todo, tách từ CTV2-087)
- [[CTV2-104-compact-context-orphan-tool-calls]] — compact_context orphan tool_calls, bug tiền tồn (todo, tách từ NB-4 của CTV2-095)
- [[CTV2-105-git-worktree-per-dispatch]] — Git worktree riêng mỗi dispatch (todo, user duyệt 2026-07-27)
- [[CTV2-103-kill-switch-cost-budget]] — Kill switch + trần chi phí + trần run đồng thời (todo, an toàn cho 089)
- [[CTV2-106-spec-plan-model-selection]] — Spec/Plan Generation Model Selection giống Dispatch Gate (done, superseded by CTV2-107)
- [[CTV2-107-unified-llm-service]] — Unified LLMService - Consolidate LLMClient, ProviderRouter, OpenAIAdapter (done)

## Tech Stack
- **Backend:** FastAPI + SQLAlchemy + Alembic
- **Orchestration:** LangGraph
- **Database:** PostgreSQL
- **Frontend:** React + Vite + TailwindCSS + React Query
- **LLM:** Claude API, OpenAI-compatible APIs (direct SDK calls)
- **Deployment:** Docker Compose

## Quy tắc phê duyệt riêng (Project Gates)
- Mọi DB migration phải có rollback script
- LLM calls phải được wrap trong try/catch với fallback
- State changes phải atomic (transaction)
- Tests phải cover gate transitions

## References
| Tài liệu | Path | Mô tả |
|:---|:---|:---|
| Research Archive | `docs/archive/` | Task research docs (implemented) |
| OCR Design | `docs/design/ocr-integration.md` | OCR integration design |
| ADR-001 | `docs/adr/ADR-001-unified-tool-architecture.md` | Unified tool architecture + full DB access (nguồn của CTV2-077..085) |
