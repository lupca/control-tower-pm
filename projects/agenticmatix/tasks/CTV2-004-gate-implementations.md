---
id: CTV2-004
title: "Gate Implementations - Spec, Plan, Dispatch, Review, Verdict"
status: done
priority: high
risk: medium
deadline: 2026-08-12
executor: "@antigravity-3.6-high"
reviewer: "@antigravity"
result_ref: "f41e472"
depends_on:
  - CTV2-003
files:
  - backend/app/graph/gates/spec.py
  - backend/app/graph/gates/plan.py
  - backend/app/graph/gates/dispatch.py
  - backend/app/graph/gates/review.py
  - backend/app/graph/gates/verdict.py
  - backend/app/graph/gates/__init__.py
flows: []
tests:
  - backend/tests/test_gates.py
dispatched: 2026-07-26
in_review: 2026-07-26
predicted_success: medium
prediction_factors:
  score: 0.65
  deductions:
    - "Core business logic (-0.15)"
    - "LLM integration needed for some gates (-0.1)"
    - "Four-eyes enforcement critical (-0.1)"
created: 2026-07-26
updated: 2026-07-26
---

# CTV2-004: Gate Implementations

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Tiêu chí nghiệm thu (AC)

### Spec Gate
- [x] Parse raw input để extract project, title
- [x] Gọi Claude API (Haiku) để validate spec + generate AC
- [x] Minimal prompt: chỉ gửi title + verifier rules
- [x] Return: acceptance_criteria, risk assessment

### Plan Gate
- [x] Gọi Claude API (Sonnet) để generate implementation plan
- [x] Input: title, AC, files, tests
- [x] Return: plan text

### Dispatch Gate
- [x] Assign executor từ input hoặc default
- [x] Generate dispatch command (reuse logic từ ct-dispatch.py)
- [x] Update status → "dispatched"
- [x] Return: executor, dispatched_at

### Review-Order Gate
- [x] Validate result_ref exists
- [x] Generate review sheet
- [x] Assign reviewer (≠ executor)
- [x] Update status → "in-review"

### Verdict Gate
- [x] Enforce four-eyes: reviewer ≠ executor (HARD FAIL if violated)
- [x] "pass" → status = "done", completed_at
- [x] "changes" → status = "changes-requested", findings populated
- [x] Update prediction metrics

### All Gates
- [x] Support `interrupt()` for supervised mode
- [x] Auto-approve in bypass mode
- [x] Audit log entry on each gate pass

## Gate Decision Matrix

| Gate | Needs LLM? | Can fail? | Four-eyes? |
|------|------------|-----------|------------|
| Spec | ✅ Yes (AC generation) | ✅ Invalid input | ❌ |
| Plan | ✅ Yes (plan writing) | ❌ | ❌ |
| Dispatch | ❌ No | ✅ No executor | ❌ |
| Review | ❌ No | ✅ No result_ref | ❌ |
| Verdict | ❌ No | ✅ Four-eyes violation | ✅ CRITICAL |

## Plan

1. Tạo base `Gate` class với common logic (interrupt, audit)
2. Implement từng gate trong file riêng
3. LLM calls dùng anthropic SDK trực tiếp (không qua LangChain)
4. Test từng gate isolated với mock state
5. Integration test: full flow spec→verdict

## Verification

```python
# Test Spec Gate
state = TaskState(raw_input="/pm add dark mode --project web")
result = spec_gate(state)
assert len(result["acceptance_criteria"]) > 0

# Test Four-eyes (must fail)
state = TaskState(executor="@alice", reviewer="@alice", verdict="pass")
with pytest.raises(FourEyesViolation):
    verdict_gate(state)
```
