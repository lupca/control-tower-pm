---
id: CTV2-046
title: "Research: V1 vs V2 Feature Gap Analysis"
status: dispatched
priority: high
risk: low
deadline: 2026-07-30
executor: "@gpt-5.6-sol"
dispatched: 2026-07-26
reviewer:
files:
  - docs/v1-v2-gap-analysis.md
tests:
  - Gap analysis document complete
  - All v1 features cataloged
  - Migration recommendations provided
created: 2026-07-26
effort: 4h
---

# CTV2-046: V1/V2 Feature Gap Analysis

## Objective

Analyze control-tower v1 (File-Over-API) vs v2 (LangGraph/PostgreSQL) to identify feature gaps. Goal: ensure v2 achieves token reduction + task accuracy improvement.

## V1 Components to Analyze

### Scripts (`scripts/`)
- `ct-dispatch.py` - mechanical dispatch with state updates
- `ct-verdict-apply.py` - verdict processing with prediction tracking
- `ct-review-order.py` - review sheet generation
- `update-agent-stats.sh` - agent performance tracking

### Skills (`.claude/skills/`)
- `pm` - project manager workflow (Spec→Plan→Dispatch gates)
- `dispatch` - executor/reviewer spawning
- `verdict` - four-eyes enforcement, causal analysis
- `review-order` - review sheet generation with graph enrichment
- `ingest` - inbox classification into tasks/knowledge
- `report` - progress tracking, index updates
- `lint` - backlog health checks

### Knowledge System
- `knowledge/agents/` - agent profiles with performance metrics
- `knowledge/tools/` - tool registry with preflight checks
- `knowledge/guides/` - spawn patterns, setup guides
- `knowledge/decisions/` - ADRs
- `knowledge/metrics/` - prediction accuracy tracking

### Workflows
- Gate-based approval (supervised/bypass/plan-only modes)
- Four-eyes enforcement (reviewer ≠ executor)
- Rejection rotation (2+ rejections → new reviewer)
- Causal analysis for high-risk tasks
- Agent performance tracking (success rate, trend)

## V2 Current State

- LangGraph StateGraph orchestration
- PostgreSQL source of truth
- FastAPI REST API
- React frontend with chat UI
- Dramatiq + Redis background workers
- SSE streaming for agent output

## Analysis Questions

1. **Gate System**: Does v2 have equivalent spec/plan/dispatch gates?
2. **Four-Eyes**: Is reviewer ≠ executor enforced?
3. **Agent Stats**: Is performance tracking implemented?
4. **Prediction Accuracy**: Is task outcome tracking in place?
5. **Knowledge System**: How are agent profiles/guides stored?
6. **Mode Switching**: supervised/bypass/plan-only support?
7. **Audit Trail**: Equivalent to log.md?

## Deliverable

`docs/v1-v2-gap-analysis.md` with:
- Feature comparison table
- Gap list with severity (critical/medium/low)
- Migration recommendations
- Token reduction opportunities identified

## AC

- [ ] AC1: All v1 scripts functionality cataloged
- [ ] AC2: All v1 skills functionality cataloged  
- [ ] AC3: Gap table with severity ratings
- [ ] AC4: Recommendations for closing critical gaps
- [ ] AC5: Token reduction analysis (v1 token usage vs v2 potential)
