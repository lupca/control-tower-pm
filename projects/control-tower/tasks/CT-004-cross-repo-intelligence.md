---
id: CT-004
title: "Cross-Repository Intelligence — Learn patterns across repos"
status: todo
priority: medium
risk: normal
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: []
files:
  - .claude/skills/pm/SKILL.md
  - index.md
  - AGENTS.md
flows: [pm-create]
tests: []
dispatched: null
in_review: null
created: 2026-07-22
updated: 2026-07-22
tier: 2
paradigm_source: "RepoGraph (2024), BLAZE (2024)"
---

# CT-004: Cross-Repository Intelligence — Learn patterns across repos

> Dự án: [[projects/control-tower/control-tower]]

## Bối cảnh (Context)

Hiện tại: code-review-graph chỉ query 1 repo (topvnsport) per task.

Research: Transfer learning across codebases gives significant boost. "BLAZE achieves cross-project bug detection via dynamic chunking."

## Tiêu chí nghiệm thu (AC)

- [ ] AC1: Mở rộng PROJECT REGISTRY với field `patterns_exportable: true|false`
- [ ] AC2: Khi `/pm` tạo task, search tương tự across ALL registered repos:
  - "Similar implementation exists in topvnsport-oms/OrderService (85% match)"
  - "Open source pattern: FastAPI pagination best practice"
- [ ] AC3: `code-review-graph cross_repo_search_tool` được sử dụng đúng cách:
  - Query với patterns từ multiple repos
  - Aggregate kết quả với similarity scores
- [ ] AC4: Tạo `knowledge/patterns/cross-repo/` để cache discovered patterns
- [ ] AC5: Pattern learning: khi task done, extract pattern và check applicability to other repos

## Plan

*(Điền khi Plan Gate)*

## Sub-tasks

- [ ] Research `cross_repo_search_tool` capabilities và params
- [ ] Update index.md PROJECT REGISTRY schema
- [ ] Implement cross-repo search in `/pm` skill
- [ ] Pattern extraction từ completed tasks
- [ ] Similarity scoring và ranking

## Research References

- [RepoGraph (2024)](https://arxiv.org/pdf/2410.14684)
- [BLAZE: Cross-Language Bug Localization (2024)](https://arxiv.org/pdf/2407.17631)
- [TransCoder: Unified Transferable Code Representation (2023-2025)](https://arxiv.org/pdf/2306.07285)
