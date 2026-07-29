---
id: CTV2-131
title: "Fix dispatch: prioritize explicit RESULT_REF over HEAD check"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: high
risk: normal
deadline: null
executor: "@claude-opus-4.5"
reviewer: "@claude-opus-4.5"
result_ref: c2ee899
verdict: pass
verdict_by: "@claude-opus-4.5"
verdict_note: "bypass mode - all tests pass including new regression test"
depends_on: []
files:
  - backend/app/workers/agent_runner.py
  - backend/tests/unit/test_agent_runner.py
flows: []
tests:
  - backend/tests/unit/test_agent_runner.py::test_build_execution_result_ref_uses_explicit_ref_when_head_unchanged
predicted_success: high
prediction_factors:
  score: 1.0
  deductions: []
created: 2026-07-28
updated: 2026-07-28
completed: 2026-07-28
---

# CTV2-131: Fix dispatch: prioritize explicit RESULT_REF over HEAD check

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Problem

Tasks MARK-001, MARK-003, MARK-005 trong `marketing-video-agent` project đều fail với lỗi:
```
Agent completed without committed changes; escalating for review
```

Mặc dù agent đã hoàn thành work và output `RESULT_REF: <sha>`.

## Root Cause

Trong `_build_execution_result_ref()`, logic check theo thứ tự sai:

```python
# BUG: Check này chạy TRƯỚC khi xem xét explicit_result_ref
if base == head or not _has_committed_diff(repo_root, base, head):
    return None, "Agent completed without committed changes"

# explicit_ref chỉ được check SAU khi base..HEAD đã pass
if explicit_ref:
    ...
```

Khi agent work trong **worktree**:
1. Worktree checkout tại `base_ref`
2. Agent tạo commits trên branch riêng → output `RESULT_REF: <sha>`
3. Nhưng `HEAD` trong worktree vẫn = `base_ref` (commit trên branch khác)
4. Check `base == head` fails trước khi xem xét `explicit_result_ref`

## Fix

Restructure logic để check `explicit_result_ref` TRƯỚC:

1. Nếu agent emit valid `RESULT_REF` (descendant of base + has diff) → use it
2. Chỉ fallback to `base..HEAD` nếu không có explicit ref
3. Fail only if neither has changes

## Verification

- 4/4 tests pass including new regression test
- `test_build_execution_result_ref_uses_explicit_ref_when_head_unchanged` - verifies explicit ref is used when HEAD hasn't moved
