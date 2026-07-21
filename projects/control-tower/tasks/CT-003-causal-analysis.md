---
id: CT-003
title: "Causal Analysis — Hiểu WHY fix works, không chỉ THAT it works"
status: dispatched
priority: medium
risk: normal
deadline: null
executor: "@sonnet-5"
reviewer: null
result_ref: null
depends_on: []
files:
  - .claude/skills/verdict/SKILL.md
  - AGENTS.md
flows: [verdict]
tests: []
dispatched: 2026-07-22
in_review: null
created: 2026-07-22
updated: 2026-07-22
tier: 2
paradigm_source: "Causal Software Engineering Vision (2025)"
---

# CT-003: Causal Analysis — Hiểu WHY fix works, không chỉ THAT it works

> Dự án: [[projects/control-tower/control-tower]]

## Bối cảnh (Context)

Hiện tại: Task done = tests pass. Không track TẠI SAO fix đó work, không học được pattern.

Research: "Re-frames SE as intervention-centric decision-making. Treats changes as interventions. Enables counterfactual testing."

## Tiêu chí nghiệm thu (AC)

- [ ] AC1: Thêm `## Causal Analysis` section vào task template (sau verdict pass)
- [ ] AC2: Format:
  ```yaml
  causal_analysis:
    root_cause: "N+1 query in ProductService.get_all()"
    mechanism: "Added .select_related('category') reduces DB calls from N+1 to 2"
    counterfactual: "Without fix, latency would remain 450ms under 100 concurrent users"
    pattern_id: "n-plus-one-query"  # reusable pattern identifier
  ```
- [ ] AC3: `/verdict pass` prompts reviewer để fill causal analysis (required for high-risk tasks)
- [ ] AC4: Tạo `knowledge/patterns/` directory — mỗi pattern_id có file mô tả:
  - Problem signature (how to detect)
  - Solution template
  - Past instances (links to tasks)
- [ ] AC5: `/pm` auto-suggests "This looks like pattern X, see how PMI-003 was fixed"
- [ ] AC6: `/lint` detects "same pattern exists elsewhere" — flags preventive tasks

## Plan

### Phase 1: Schema Update
1. AGENTS.md §2.1 — thêm `## Causal Analysis` section template (required for risk: high)

### Phase 2: Pattern Library
2. Tạo `knowledge/patterns/` với initial patterns:
   - `_index.md` — pattern registry
   - `n-plus-one-query.md`
   - `missing-db-index.md`
   - `race-condition.md`
   - `memory-leak.md`

3. Pattern file format: pattern_id, category, severity, Problem Signature, Detection, Solution Template, Past Instances

### Phase 3: Verdict Integration
4. verdict/SKILL.md — prompt causal analysis on pass (required for high-risk):
   - Root cause, mechanism, counterfactual, pattern_id
   - Update pattern's Past Instances list

### Phase 4: PM Pattern Matching
5. pm/SKILL.md — scan task description for pattern signatures, suggest past fixes

### Phase 5: Lint Cross-Reference
6. lint/SKILL.md — detect patterns in codebase without existing tasks, flag preventive fixes

## Sub-tasks

- [ ] Add `## Causal Analysis` to task template in AGENTS.md §2.1
- [ ] Update verdict skill to collect causal info
- [ ] Create `knowledge/patterns/` with initial patterns (n-plus-one, missing-index, etc.)
- [ ] Pattern matching logic in `/pm` for suggestions
- [ ] Cross-reference detection in `/lint`

## Research References

- [Causal Software Engineering Vision (2025)](https://arxiv.org/pdf/2605.02454)
- [CauSE 2025 Workshop](https://causality-software-engineering.github.io/cause-workshop-2025/)
- [KRCA: Root Cause Analysis via Agentic AI (2025)](https://arxiv.org/pdf/2607.01788)
