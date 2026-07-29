---
id: CTV2-210
title: "Enforce reviewer isolation and schema versioning"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: medium
risk: normal
deadline: null
executor: "@gpt-5.6-luna"
reviewer: "@claude-sonnet-medium"
result_ref: "23cb9be..49123ec"
depends_on: [CTV2-201]
files:
  - backend/app/services/command_builder.py
  - backend/app/workers/agent_runner.py
flows: []
tests:
  - backend/tests/unit/test_agent_runner.py
dispatched: 2026-07-29
in_review: null
predicted_success: high
prediction_factors:
  score: 0.7
  deductions:
    - "depends_on: CTV2-201 (-0.2)"
    - "worktree: git isolation (-0.1)"
confidence_interval: [0.6, 0.8]
created: 2026-07-29
updated: 2026-07-29
---

# CTV2-210: Enforce reviewer isolation and schema versioning

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Context

Reviewer should run read-only in separate worktree. Review JSON needs schema version for forward compatibility.

## Tiêu chí nghiệm thu (AC)

- [ ] Create separate worktree for reviewer that checks out executor's head_sha
- [ ] Run reviewer CLI with read-only git config (or verify no commits allowed)
- [ ] Add schema_version field to ReviewResult (start at "1.0")
- [ ] Extend ReviewResult to require: criterion_id, status, evidence[], finding_ids[] per AC
- [ ] Validate ReviewResult.findings have: id, severity, category, file, line, description
- [ ] Reject reviews missing required fields instead of defaulting to pass

## Verification

- `pytest backend/tests/unit/test_agent_runner.py -v` → 100% pass

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] Update build_review_command for worktree isolation
- [ ] Add read-only git config for reviewer
- [ ] Define ReviewResult schema v1.0
- [ ] Add validation for ReviewResult
- [ ] Add tests
