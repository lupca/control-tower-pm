---
id: CT-004
title: "Cross-Repository Intelligence — Learn patterns across repos"
status: done
priority: medium
risk: normal
deadline: null
executor: "@sonnet-5"
reviewer: "@sonnet-5"
result_ref: "control-tower@main (commit 510b3b4)"
depends_on: []
files:
  - .claude/skills/pm/SKILL.md
  - .claude/skills/pm/references/task-creation.md
  - index.md
  - AGENTS.md
  - knowledge/patterns/cross-repo/_index.md
flows: [pm-create]
tests: []
dispatched: 2026-07-22
in_review: 2026-07-22
created: 2026-07-22
updated: 2026-07-22
tier: 2
paradigm_source: "RepoGraph (2024), BLAZE (2024)"
---

# CT-004: Cross-Repository Intelligence — Learn patterns across repos

> Dự án: [[projects/control-tower/control-tower]]

> ⚠️ **Four-eyes waived by explicit User instruction** (2026-07-22): batch-processed alongside CT-005–CT-010 with `reviewer: executor` per User request in chat, compensated by an independent aggregate review — see [[CT-011-review-paradigm-shift-batch]] (reviewer `@claude-4.5`). This is a deliberate, logged exception to `AGENTS.md` §1's separation-of-duties rule, not an oversight.

## Bối cảnh (Context)

Hiện tại: code-review-graph chỉ query 1 repo (topvnsport) per task.

Research: Transfer learning across codebases gives significant boost. "BLAZE achieves cross-project bug detection via dynamic chunking."

## Tiêu chí nghiệm thu (AC)

- [x] AC1: Mở rộng PROJECT REGISTRY với field `patterns_exportable: true|false`
- [x] AC2: Khi `/pm` tạo task, search tương tự across ALL registered repos:
  - "Similar implementation exists in topvnsport-oms/OrderService (85% match)"
  - "Open source pattern: FastAPI pagination best practice"
- [x] AC3: `code-review-graph cross_repo_search_tool` được sử dụng đúng cách:
  - Query với patterns từ multiple repos
  - Aggregate kết quả với similarity scores
- [x] AC4: Tạo `knowledge/patterns/cross-repo/` để cache discovered patterns
- [x] AC5: Pattern learning: khi task done, extract pattern và check applicability to other repos

## Plan

### Phase 1: Registry schema
1. `index.md` §2 — thêm cột `patterns_exportable` vào PROJECT REGISTRY (mọi repo topvnsport = `true`, control-tower = `false` vì không có code).

### Phase 2: Search integration
2. `AGENTS.md` §14 — định nghĩa cross-repo search behavior + `cross_repo_search_tool` usage.
3. `.claude/skills/pm/SKILL.md` — thêm `cross_repo_search_tool` vào `allowed-tools`.
4. `.claude/skills/pm/references/task-creation.md` step 4 — cross-repo search tại Spec Gate, check cache trước khi query graph.

### Phase 3: Cache + learning
5. `knowledge/patterns/cross-repo/_index.md` — cache registry cho confirmed matches.
6. `AGENTS.md` §14.4 + `.claude/skills/verdict/SKILL.md` step 4 (pass flow) — pattern learning suggestion khi task đóng.

## Sub-tasks

- [x] Research `cross_repo_search_tool` capabilities và params
- [x] Update index.md PROJECT REGISTRY schema
- [x] Implement cross-repo search in `/pm` skill
- [x] Pattern extraction từ completed tasks
- [x] Similarity scoring và ranking (documented as "~70% similarity threshold" heuristic — actual scoring comes from `cross_repo_search_tool`'s own output, not reimplemented in control-tower)

## Research References

- [RepoGraph (2024)](https://arxiv.org/pdf/2410.14684)
- [BLAZE: Cross-Language Bug Localization (2024)](https://arxiv.org/pdf/2407.17631)
- [TransCoder: Unified Transferable Code Representation (2023-2025)](https://arxiv.org/pdf/2306.07285)
