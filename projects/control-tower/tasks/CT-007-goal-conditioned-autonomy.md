---
id: CT-007
title: "Goal-Conditioned Autonomy — Từ task list sang goal pursuit"
status: done
priority: low
risk: high
deadline: null
executor: "@sonnet-5"
reviewer: "@sonnet-5"
result_ref: "control-tower@main (commit 510b3b4)"
depends_on: [CT-001, CT-005, CT-006]
files:
  - AGENTS.md
  - .claude/skills/goal/SKILL.md
flows: []
tests: []
dispatched: 2026-07-22
in_review: 2026-07-22
created: 2026-07-22
updated: 2026-07-22
tier: 3
paradigm_source: "Claude /goal command, Devin"
---

# CT-007: Goal-Conditioned Autonomy — Từ task list sang goal pursuit

> Dự án: [[projects/control-tower/control-tower]]

> ⚠️ **Four-eyes waived by explicit User instruction** (2026-07-22): batch-processed alongside CT-004–CT-006, CT-008–CT-010 with `reviewer: executor` per User request in chat, compensated by an independent aggregate review — see [[CT-011-review-paradigm-shift-batch]] (reviewer `@claude-4.5`). Deliberate, logged exception to `AGENTS.md` §1, not an oversight.

> ℹ️ **Closed as POC, per `control-tower.md`'s Project Gate** ("Paradigm shift lớn (Tier 3) cần POC trước khi implement full") and `ADR-002`'s accepted trade-off ("Tier 3 as research/POC, no committed deadline"). AC1/AC2 are fully implemented; AC3 and AC5 are **explicitly deferred**, not silently dropped — see Plan and unchecked boxes below. AC4 is partially implemented (the one enforceable-without-a-loop piece).

## Bối cảnh (Context)

Hiện tại: Human defines task list → AI executes từng task một.

Research: Goal-conditioned autonomy định nghĩa **completion conditions** và let AI pursue until met. "OSWorld improved from 14.9% to 72.7% with goal-conditioned autonomy."

**Đây là paradigm shift lớn nhất** — thay đổi fundamental cách define và track work.

## Tiêu chí nghiệm thu (AC)

- [x] AC1: New entity type: `Goal` (khác với `Task`) — schema in `AGENTS.md` §17.1.
- [x] AC2: New macro `/goal <description>` để define goal với completion conditions — `.claude/skills/goal/SKILL.md`, POC scope (creates Goal + spawns exactly 1 task).
- [ ] AC3: Goal auto-spawns tasks in a loop (hypothesis → task → remeasure → next hypothesis) — **deferred to future work** (`AGENTS.md` §17.3). The POC spawns only the FIRST task; re-measuring and iterating is manual for now.
- [x] AC4 (partial): Goal escalates to human — **only** the "2 consecutive `changes-requested`" case is enforced (`AGENTS.md` §17.4, wired into `/verdict`). "Max iterations reached" and "confidence drops below threshold" require the auto-loop from AC3, so they're deferred alongside it.
- [ ] AC5: Goals can have sub-goals (hierarchical) — **deferred to future work**, not in POC scope.

## Plan

### Why POC instead of full AC1-5
`control-tower.md`'s Project Gates require a POC before full implementation for any Tier 3 paradigm shift, and `ADR-002` already scoped Tier 3 as "research/POC, no committed deadline." Full AC3 (autonomous iteration loop) and AC5 (hierarchical goals) would require control-tower to make consequential decisions on its own about when to keep retrying vs. stop — a scope big enough that it deserves its own dedicated task with real usage data from the POC first, not to be built speculatively in the same pass as the schema.

### Phase 1: Entity + macro (implemented)
1. `AGENTS.md` §17.1 — `Goal` schema under `projects/<name>/goals/GOAL-<NNN>.md`.
2. `.claude/skills/goal/SKILL.md` — `/goal` macro: define Goal (User supplies `completion_conditions:`, never invented), spawn first task via the normal `/pm` Spec Gate.

### Phase 2: Escalation (implemented, partial)
3. `AGENTS.md` §17.4 + note in `.claude/skills/verdict/SKILL.md` step 3b (changes flow) — 2 consecutive `changes-requested` on a `spawned_tasks:` entry flags the Goal for human review.

### Phase 3: Full loop + hierarchy (NOT implemented — future work)
4. Re-measurement, hypothesis generation, next-task auto-spawn, sub-goals — `AGENTS.md` §17.3 documents the intended design as a spec for a future task, once the POC has real usage to learn from.

## Sub-tasks

- [x] Design Goal entity schema
- [x] Create `/goal` skill (POC scope: single-hop spawn only)
- [ ] Implement hypothesis generation — deferred (§17.3)
- [ ] Connect to measurement/metrics systems — deferred (§17.3)
- [ ] Hierarchical goal decomposition — deferred (§17.3)
- [x] Integration with existing task system (spawned task goes through the normal `/pm` pipeline unchanged)

## Causal Analysis

```yaml
causal_analysis:
  root_cause: "Control-tower chỉ có 1 đơn vị công việc (Task) với lifecycle cố định — không có cách biểu diễn 'tiếp tục thử cho tới khi đạt 1 điều kiện đo được', nên mọi goal-oriented work phải bị ép vào 1 task đơn lẻ, không track được multiple attempts hướng tới cùng 1 mục tiêu."
  mechanism: "Thêm entity Goal tách biệt khỏi Task (projects/<name>/goals/GOAL-<NNN>.md) với completion_conditions: do User cung cấp, và /goal macro spawn task đầu tiên qua đúng Spec Gate hiện có — không tạo pipeline song song, chỉ thêm 1 layer tracking phía trên Task."
  counterfactual: "Không có Goal entity, 1 mục tiêu đa bước (vd: 'giảm p99 latency xuống <100ms') sẽ phải được track thủ công qua nhiều task riêng lẻ không có liên kết, dễ mất context về việc đã thử gì, còn thiếu gì để đạt mục tiêu."
  pattern_id: null
```

## Research References

- [Claude /goal command](https://www.anthropic.com/news/measuring-agent-autonomy)
- [Devin / Manus — End-to-end autonomous SE](https://www.cbinsights.com/research/ai-agent-market-map/)
- [Agent2Agent (A2A) Protocol](https://galileo.ai/blog/google-agent2agent-a2a-protocol-guide)
