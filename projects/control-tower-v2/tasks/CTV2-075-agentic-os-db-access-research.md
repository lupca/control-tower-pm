---
id: CTV2-075
title: "Research: Agentic OS Full DB Access Architecture"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: high
risk: normal
deadline: null
executor: "@claude-fable"
reviewer: null
result_ref: "docs/adr/ADR-001-unified-tool-architecture.md"
depends_on: []
files:
  - backend/app/services/tool_definitions.py
  - backend/app/services/command_router.py
  - backend/app/services/context_hierarchy.py
  - backend/app/graph/context.py
  - backend/app/db/models.py
flows: []
tests: []
dispatched: null
in_review: null
predicted_success: high
prediction_factors:
  score: 0.95
  deductions: []
created: 2026-07-27
updated: 2026-07-27
completed: 2026-07-27
confidence_interval: [0.85, 0.98]
---

> **Closed 2026-07-27 theo research-no-review**: deliverable tồn tại tại `control-tower-v2/docs/adr/ADR-001-unified-tool-architecture.md`, phủ đủ 7 AC. Executor thực tế là phiên coordinator @claude-fable (không phải @antigravity như dispatch ban đầu — reconciled). Implementation plan đã phân rã thành CTV2-077..CTV2-085.

# CTV2-075: Research: Agentic OS Full DB Access Architecture

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Tiêu chí nghiệm thu (AC)

- [x] Gap analysis document: liệt kê tất cả DB entities chưa có tools (Project, Agent, Knowledge, Settings, etc.) — ADR §3 P6
- [x] Pattern evaluation: so sánh MCP resources vs LLM tools vs hybrid với token metrics — ADR §7 + D2
- [x] LangGraph patterns: multi-step DB operations, transaction handling, rollback — ADR §2.3, §7 (giữ separation graph = task FSM)
- [x] Token optimization strategies: deferred tools, batch ops, context snapshot expansion — ADR D3, D4, §5
- [x] Security model: permission levels, audit trail, rate limiting — ADR D2 guardrails + registry `permission`
- [x] ADR document: recommended architecture với rationale — `docs/adr/ADR-001-unified-tool-architecture.md`
- [x] Implementation plan: ordered task list với dependencies — ADR §6, triển khai thành CTV2-077..085

## Verification

- ADR document exists at `docs/adr/ADR-XXX-agentic-os-db-access.md`
- Document covers all 6 research areas in scope
- Implementation plan has concrete task definitions

## Plan

1. **Gap Analysis** (backend/app/services/tool_definitions.py, command_router.py):
   - Audit existing tools vs DB models
   - Categorize: have-tool, read-only, no-access
   - Estimate token cost per operation type

2. **Pattern Evaluation**:
   - MCP resources: pros (cacheable, browsable), cons (extra hop)
   - LLM tools: pros (direct), cons (token cost per definition)
   - Hybrid (current): pros (read via snapshot, write via tools)
   - Compare with CTV2-059 findings (74% token savings)

3. **LangGraph Patterns**:
   - Review builder.py, state.py for existing patterns
   - Research: subgraphs for DB transactions
   - Research: conditional edges for permission checks

4. **Token Optimization**:
   - Deferred tool loading (already implemented, assess expansion)
   - Batch operation tools (e.g., `bulk_update_tasks`)
   - Context snapshot expansion for more entities

5. **Security Model**:
   - Define permission levels: read-only, write-own, write-all, admin
   - Audit trail: leverage existing GateRecord/AuditLog
   - Rate limiting: per-session, per-agent

6. **Write ADR + Implementation Plan**:
   - Synthesize findings
   - Recommend architecture
   - Break into implementation tasks

## Sub-tasks

- [ ] Audit existing tools vs DB models, create gap matrix
- [ ] Evaluate MCP vs tools vs hybrid with token metrics
- [ ] Research LangGraph subgraph patterns for transactions
- [ ] Design expanded context snapshot schema
- [ ] Define permission model with levels
- [ ] Write ADR document
- [ ] Create implementation task list
