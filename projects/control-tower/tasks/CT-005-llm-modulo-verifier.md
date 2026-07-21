---
id: CT-005
title: "LLM-Modulo — Symbolic verifier cho LLM-generated plans"
status: todo
priority: medium
risk: high
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: []
files:
  - .claude/skills/pm/SKILL.md
  - .claude/skills/pm/references/task-creation.md
  - AGENTS.md
flows: [pm-create, plan]
tests: []
dispatched: null
in_review: null
created: 2026-07-22
updated: 2026-07-22
tier: 2
paradigm_source: "LLM-Modulo Framework (ICML 2024)"
---

# CT-005: LLM-Modulo — Symbolic verifier cho LLM-generated plans

> Dự án: [[projects/control-tower/control-tower]]

## Bối cảnh (Context)

Hiện tại: `/pm` dùng LLM generate AC + Plan → human approve.

Research (ICML 2024): "LLMs fundamentally cannot plan autonomously. They should be treated as universal approximate knowledge sources within a neuro-symbolic architecture where external verifiers check generated candidates."

## Tiêu chí nghiệm thu (AC)

- [ ] AC1: Tạo verifier rules set (có thể mở rộng):
  ```yaml
  # .claude/verifier-rules.yaml
  rules:
    - id: no-circular-deps
      check: "depends_on không tạo cycle"
    - id: files-exist
      check: "mọi file trong files: phải tồn tại trong repo"
    - id: reasonable-scope
      check: "blast radius <= 8 files hoặc đã split"
    - id: tests-for-changes
      check: "mỗi file thay đổi phải có test tương ứng trong tests:"
    - id: no-conflicting-tasks
      check: "không có task khác đang modify same files với status dispatched/in-review"
  ```
- [ ] AC2: `/pm` runs verifier BEFORE showing plan to human:
  - Nếu fail → auto-fix hoặc flag specific issues
  - Chỉ plans PASS mới đến Spec Gate
- [ ] AC3: Verifier output:
  ```
  ✅ no-circular-deps: passed
  ✅ files-exist: passed
  ⚠️ reasonable-scope: 12 files, suggest splitting
  ❌ tests-for-changes: missing test for services/payment.py
  ```
- [ ] AC4: Human có thể override verifier warnings (với explicit acknowledgment)

## Plan

*(Điền khi Plan Gate)*

## Sub-tasks

- [ ] Design verifier rules schema
- [ ] Implement each rule checker
- [ ] Integrate verifier into `/pm` flow (before Spec Gate)
- [ ] Auto-fix logic cho simple violations
- [ ] Override mechanism với audit

## Research References

- [LLM-Modulo Framework (ICML 2024)](https://proceedings.mlr.press/v235/kambhampati24a.html)
- [LaMMA-P: LLM-Driven PDDL Planning (2024)](https://arxiv.org/pdf/2409.20560)
- [Plan-and-Act Framework (2025)](https://arxiv.org/html/2503.09572v3)
