---
id: CT-010
title: "Vericoding — Formal proofs thay vì testing"
status: todo
priority: low
risk: high
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: []
files:
  - AGENTS.md
  - .claude/skills/pm/SKILL.md
  - .claude/skills/verdict/SKILL.md
flows: [pm-create, verdict]
tests: []
dispatched: null
in_review: null
created: 2026-07-22
updated: 2026-07-22
tier: 3
paradigm_source: "Vericoding (Tegmark 2025), AlphaProof"
---

# CT-010: Vericoding — Formal proofs thay vì testing

> Dự án: [[projects/control-tower/control-tower]]

## Bối cảnh (Context)

Hiện tại: AC là natural language → executor viết code → test pass = done.

Research: "Vericoding" = LLM generates code WITH formal proofs. "82% success generating formally verified Dafny code." AlphaProof achieved IMO silver medal with machine-verified Lean proofs.

**Impact:** Reviewer không cần chạy test để verify correctness — proof kernel đã verify mathematically. Human chỉ verify INTENT (spec đúng chưa), machine verify IMPLEMENTATION (code matches spec).

## Tiêu chí nghiệm thu (AC)

- [ ] AC1: New field `formal_spec:` trong task frontmatter (optional):
  ```yaml
  formal_spec:
    language: dafny  # hoặc lean4, verus
    spec: |
      ensures result >= 0
      ensures forall i :: 0 <= i < items.Length ==> items[i].price > 0
  ```
- [ ] AC2: `/pm` có thể generate formal spec từ natural language AC:
  - "Total price = sum of (price * quantity)" → Dafny `ensures`
  - "No negative values allowed" → `ensures x >= 0`
- [ ] AC3: Executor workflow khi có `formal_spec:`:
  - Generate code + proof annotations
  - Run Dafny/Lean verifier
  - If proof passes → code is mathematically correct
- [ ] AC4: `/verdict` với formal proof:
  - Reviewer chỉ verify: "Spec đúng intent của AC không?"
  - Không cần chạy test suite — proof đã verify correctness
  - `verdict: pass` nếu spec matches intent (faster review)
- [ ] AC5: Gradual adoption:
  - Start với critical paths only (payment, auth)
  - Non-critical paths vẫn dùng traditional testing

## Plan

*(Điền khi Plan Gate)*

## Sub-tasks

- [ ] Research Dafny/Lean4 integration options
- [ ] NL-to-formal-spec generation (prompt engineering or fine-tuned)
- [ ] Proof verification toolchain setup
- [ ] Modified review process for verified code
- [ ] Identify critical paths for pilot

## Research References

- [Vericoding (Tegmark, Sept 2025)](https://arxiv.org/pdf/2509.22908)
- [AlphaProof / AlphaProof Nexus (DeepMind)](https://www.nature.com/articles/s41586-025-09833-y)
- [DeepSeek-Prover V2 (April 2025)](https://arxiv.org/pdf/2504.21801)
- [Proof-Carrying Code Completions (ASE 2024)](https://dl.acm.org/doi/10.1145/3691621.3694932)
