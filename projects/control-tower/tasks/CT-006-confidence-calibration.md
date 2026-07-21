---
id: CT-006
title: "Confidence Calibration — Know WHEN to escalate"
status: todo
priority: medium
risk: normal
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: [CT-001]
files:
  - .claude/skills/pm/SKILL.md
  - AGENTS.md
flows: [pm-create, plan, dispatch]
tests: []
dispatched: null
in_review: null
created: 2026-07-22
updated: 2026-07-22
tier: 2
paradigm_source: "MIT Conformal Prediction for NLP (2025)"
---

# CT-006: Confidence Calibration — Know WHEN to escalate

> Dự án: [[projects/control-tower/control-tower]]

## Bối cảnh (Context)

Hiện tại: Fixed gates — Spec Gate ALWAYS, Plan Gate ALWAYS, Verdict ALWAYS needs human.

Research: Conformal prediction provides "distribution-free uncertainty quantification — know WHEN to defer to humans" với formal guarantees.

## Tiêu chí nghiệm thu (AC)

- [ ] AC1: Thêm `confidence_interval: [lower, upper]` vào task metadata
- [ ] AC2: Confidence được tính từ:
  - Model's own uncertainty (logprobs nếu có)
  - Historical accuracy on similar tasks (từ CT-001)
  - Verifier results (từ CT-005)
  - Risk level (hub/bridge nodes)
- [ ] AC3: Dynamic gate rules:
  ```
  If confidence_interval narrow AND lower > 0.85:
    → Auto-proceed (log only, no human gate)
  If confidence_interval wide OR lower < 0.60:
    → REQUIRE explicit human approval
  Else:
    → Standard gate (human can quick-approve)
  ```
- [ ] AC4: Human can always override to require gates ("I want to review all tasks this week")
- [ ] AC5: Calibration tracking: so sánh predicted confidence vs actual outcomes
- [ ] AC6: `/lint` warning nếu calibration drift quá lớn

## Plan

*(Điền khi Plan Gate)*

## Sub-tasks

- [ ] Research conformal prediction implementation
- [ ] Define confidence computation formula
- [ ] Implement dynamic gate logic
- [ ] User preference override ("always ask me")
- [ ] Calibration drift detection

## Research References

- [MIT Conformal Prediction for NLP (2025)](https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00715/125278/Conformal-Prediction-for-Natural-Language)
- [Human-AI Joint Cognitive Systems Framework (ACM 2024)](https://interactions.acm.org/archive/view/january-february-2024/applying-hcai-in-developing-effective-human-ai-teaming)
