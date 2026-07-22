---
id: CT-008
title: "Stigmergic Coordination — Agents coordinate qua shared artifacts"
status: done
priority: low
risk: high
deadline: null
executor: "@sonnet-5"
reviewer: "@sonnet-5"
result_ref: "control-tower@main (commit 510b3b4)"
depends_on: [CT-002]
files:
  - AGENTS.md
  - .claude/skills/ingest/SKILL.md
flows: []
tests: []
dispatched: 2026-07-22
in_review: 2026-07-22
created: 2026-07-22
updated: 2026-07-22
tier: 3
paradigm_source: "Ledger-State Stigmergy (2025)"
---

# CT-008: Stigmergic Coordination — Agents coordinate qua shared artifacts

> Dự án: [[projects/control-tower/control-tower]]

> ⚠️ **Four-eyes waived by explicit User instruction** (2026-07-22): batch-processed alongside CT-004–CT-007, CT-009, CT-010 with `reviewer: executor` per User request in chat, compensated by an independent aggregate review — see [[CT-011-review-paradigm-shift-batch]] (reviewer `@claude-4.5`). Deliberate, logged exception to `AGENTS.md` §1, not an oversight.

> ℹ️ **Closed as POC**, per `control-tower.md`'s Project Gate + `ADR-002`. AC4 (event format) and AC2 (opt-in claiming rule) are implemented; AC1 (graph-change watcher auto-creating tasks), AC3 (emergent prioritization as an enforced mechanism), and AC5 (removing the central dispatcher) are **explicitly deferred**, not silently dropped.

## Bối cảnh (Context)

Hiện tại: Control-tower explicitly dispatch → executor làm → executor báo done.

Research: Stigmergy là coordination mechanism từ sinh học (ants, bees) — agents communicate through changes in shared environment, không cần direct messaging. "Agents read/write to shared state; no direct communication needed."

## Tiêu chí nghiệm thu (AC)

- [ ] AC1: `code-review-graph` trở thành **shared ledger** với auto-created task candidates từ knowledge gaps/test failures — **deferred**. Control-tower has no polling daemon/scheduler to run this; would need to live outside this Markdown-only system (see `AGENTS.md` §18.4).
- [x] AC2: Task auto-claiming (POC, opt-in per agent) — `AGENTS.md` §18.2: an agent may self-claim a matching unassigned task, first-commit-wins conflict resolution. Opt-in, not the default flow.
- [ ] AC3: Emergent prioritization as an enforced mechanism — **deferred**; implemented only as a *documented hint* `/lint` may surface (`AGENTS.md` §18.3), never an auto-written priority field (would fight the human-set `priority:`).
- [x] AC4: Event stream (lightweight) — `events.jsonl` format defined (`AGENTS.md` §18.1), written alongside existing `log.md` entries by the same skills.
- [ ] AC5: No central dispatcher — **deferred**. The default remains explicit User-assigned `executor:` at the Plan Gate; AC2's opt-in claiming is an additional path, not a replacement.

## Plan

### Why POC instead of full AC1-5
Full stigmergic coordination (AC1's watcher, AC5's dispatcher removal) needs a live polling process — control-tower is a Markdown-only, session-driven system with no background daemon of its own (`code-review-graph`'s daemon watches code, not control-tower's own task backlog). Building that is a much bigger infra decision than this task's blast radius suggests; per the Project Gate, ship the POC (event format + opt-in claiming) and let a future task decide on the watcher/dispatcher-removal separately, informed by how the POC gets used.

### Phase 1: Event format (implemented)
1. `AGENTS.md` §18.1 — `events.jsonl` line shape, written by the same skills that already write `log.md`.

### Phase 2: Opt-in claiming (implemented)
2. `AGENTS.md` §18.2 — self-claim rule + first-commit-wins conflict resolution, opt-in per agent.
3. `AGENTS.md` §18.3 — emergent prioritization documented as a `/lint` hint, not an enforced field.

### Phase 3: Watcher + dispatcher removal (NOT implemented — future work)
4. `AGENTS.md` §18.4 explicitly scopes this out and states why.

## Sub-tasks

- [x] Design event stream format
- [ ] Implement graph-change watcher — deferred (§18.4)
- [ ] Task auto-generation from knowledge gaps — deferred (§18.4)
- [x] Claiming mechanism với conflict resolution (opt-in, first-commit-wins)
- [ ] Remove explicit dispatch requirement (optional path) — deferred (§18.4)

## Causal Analysis

```yaml
causal_analysis:
  root_cause: "Mọi coordination hiện tại đi qua 1 điểm duy nhất — User assign executor: tại Plan Gate. Không có cách nào cho 1 agent tự nhận task phù hợp với strengths của nó (CT-002) mà không cần User can thiệp thủ công từng lần."
  mechanism: "Thêm events.jsonl (ghi song song với log.md, không thay thế) làm shared signal machine-readable, và 1 rule opt-in cho phép agent tự set executor: trên task ready/unassigned phù hợp strengths — first-commit-wins nếu 2 agent claim gần như đồng thời."
  counterfactual: "Không có cơ chế này, mọi task dù rõ ràng phù hợp với 1 agent cụ thể vẫn phải chờ User rảnh để gõ lệnh assign — tạo bottleneck không cần thiết cho các task đơn giản, rõ domain."
  pattern_id: null
```

## Research References

- [Ledger-State Stigmergy (2025)](https://arxiv.org/html/2604.03997v1)
- [Spontaneous Social Conventions Study (2025)](https://zylos.ai/research/2026-03-18-emergent-behavior-large-scale-multi-agent-systems/)
- [Behavioral Differentiation Without Role Assignment (2025)](https://arxiv.org/pdf/2604.00026)
