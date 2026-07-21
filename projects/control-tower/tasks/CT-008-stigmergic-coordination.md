---
id: CT-008
title: "Stigmergic Coordination — Agents coordinate qua shared artifacts"
status: todo
priority: low
risk: high
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: [CT-002]
files:
  - AGENTS.md
  - .claude/skills/ingest/SKILL.md
flows: []
tests: []
dispatched: null
in_review: null
created: 2026-07-22
updated: 2026-07-22
tier: 3
paradigm_source: "Ledger-State Stigmergy (2025)"
---

# CT-008: Stigmergic Coordination — Agents coordinate qua shared artifacts

> Dự án: [[projects/control-tower/control-tower]]

## Bối cảnh (Context)

Hiện tại: Control-tower explicitly dispatch → executor làm → executor báo done.

Research: Stigmergy là coordination mechanism từ sinh học (ants, bees) — agents communicate through changes in shared environment, không cần direct messaging. "Agents read/write to shared state; no direct communication needed."

## Tiêu chí nghiệm thu (AC)

- [ ] AC1: `code-review-graph` trở thành **shared ledger**:
  - Agents poll graph changes định kỳ
  - New "knowledge gap" detected → auto-create task candidate
  - Test failure → auto-create fix task candidate
- [ ] AC2: Task auto-claiming:
  - Agent sees unassigned task matching its strengths (từ CT-002)
  - Agent "claims" task bằng cách set `executor: @self`
  - First-claim wins (với conflict resolution)
- [ ] AC3: Emergent prioritization:
  - Tasks with more "watchers" (agents interested) get higher implicit priority
  - Blocked tasks (has unfulfilled depends_on) stay unclaimed
- [ ] AC4: Event stream (lightweight):
  - `events.jsonl` log mọi state changes
  - Agents subscribe to events thay vì poll full state
- [ ] AC5: No central dispatcher — coordination emerges from shared state

## Plan

*(Điền khi Plan Gate)*

## Sub-tasks

- [ ] Design event stream format
- [ ] Implement graph-change watcher
- [ ] Task auto-generation from knowledge gaps
- [ ] Claiming mechanism với conflict resolution
- [ ] Remove explicit dispatch requirement (optional path)

## Research References

- [Ledger-State Stigmergy (2025)](https://arxiv.org/html/2604.03997v1)
- [Spontaneous Social Conventions Study (2025)](https://zylos.ai/research/2026-03-18-emergent-behavior-large-scale-multi-agent-systems/)
- [Behavioral Differentiation Without Role Assignment (2025)](https://arxiv.org/pdf/2604.00026)
