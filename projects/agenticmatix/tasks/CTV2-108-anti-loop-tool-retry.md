---
id: CTV2-108
title: "Anti-loop tool retry rules + pre-emptive duplicate detection"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: high
risk: normal
deadline: null
executor: "@claude-opus-4.5"
reviewer: "@manual-verification"
result_ref: "control-tower-v2@main (commit dce075a)"
depends_on: []
files:
  - backend/app/prompts/global_context.md
  - backend/app/services/coordinator.py
flows: []
tests:
  - backend/tests/test_coordinator.py
dispatched: 2026-07-28
in_review: 2026-07-28
predicted_success: high
prediction_factors:
  score: 0.85
  deductions:
    - "blast_radius: 2 files (-0.0)"
    - "clear requirements from research (-0.0)"
created: 2026-07-28
updated: 2026-07-28
---

# CTV2-108: Anti-loop tool retry rules + pre-emptive duplicate detection

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Context

Agent bị stuck loop gọi `query_db` 3 lần với cùng arguments. Harness detect và stop, nhưng agent không có instructions để recover. Claude Code tránh được vì system prompt có explicit anti-loop rules.

## Tiêu chí nghiệm thu (AC)

- [ ] `global_context.md` có section "Tool retry rules" với:
  - Rule: không gọi cùng tool với cùng arguments 2 lần liên tiếp
  - Hướng dẫn: nếu empty → thử query khác hoặc report not found
  - Clarify: empty = valid answer, không phải error cần retry
- [ ] `coordinator.py` implement pre-emptive duplicate detection:
  - Detect duplicate call TRƯỚC khi execute (không phải sau)
  - Trả về tool result với `{"error": "DUPLICATE_CALL", "message": "..."}` thay vì execute
  - Message hướng dẫn agent thử approach khác
- [ ] Test case verify:
  - Gọi tool lần 1 → execute bình thường
  - Gọi tool lần 2 với cùng args → KHÔNG execute, trả DUPLICATE_CALL error
  - Gọi tool lần 3 với args KHÁC → execute bình thường

## Verification

- `grep -A 10 "Tool retry rules" backend/app/prompts/global_context.md` → có section với 3 rules
- `grep "DUPLICATE_CALL" backend/app/services/coordinator.py` → có error type
- `pytest backend/tests/test_coordinator.py -k "duplicate" -v` → pass

## Plan

1. **global_context.md**: Thêm section "Tool retry rules" sau section "Tool usage" với 3 rules:
   - Never call same tool with identical args consecutively
   - If empty: try different query or report not found
   - Empty = valid answer, not retry signal

2. **coordinator.py**: Modify `_execute_tools()` method:
   - Track `last_tool_sig` (tool_name, args_hash)
   - Before executing, check if current sig == last_tool_sig
   - If duplicate: return fake tool result with DUPLICATE_CALL error instead of executing
   - If not duplicate: execute normally, update last_tool_sig

3. **test_coordinator.py**: Add test case:
   - Mock a tool that returns empty
   - Call it twice with same args
   - Assert second call returns DUPLICATE_CALL error without executing
   - Call with different args → executes normally

## Sub-tasks

- [x] Add "Tool retry rules" section to `global_context.md`
- [x] Implement pre-emptive duplicate detection in `coordinator.py`
- [x] Add test case for duplicate detection
