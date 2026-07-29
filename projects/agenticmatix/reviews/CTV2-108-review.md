---
task_id: CTV2-108
title: "Anti-loop tool retry rules + pre-emptive duplicate detection"
executor: "@claude-opus-4.5"
reviewer: "@manual-verification"
result_ref: "control-tower-v2@main (commit dce075a)"
created: 2026-07-28
---

# Review Sheet: CTV2-108

## Summary

Fix agent loop khi tool trả empty — thêm prompt rules vào `global_context.md` + implement pre-emptive duplicate detection trong `coordinator.py`.

## Files Changed

- `backend/app/prompts/global_context.md` — added "Tool retry rules" section
- `backend/app/services/coordinator.py` — pre-emptive duplicate detection
- `backend/tests/test_coordinator.py` — new test case

## Acceptance Criteria

- [ ] `global_context.md` có section "Tool retry rules" với 3 rules
- [ ] `coordinator.py` implement pre-emptive duplicate detection (detect TRƯỚC khi execute)
- [ ] Test case verify: lần 1 execute, lần 2 DUPLICATE_CALL, lần 3 (khác args) execute

## Verification Commands

```bash
cd /home/lupca/projects/control-tower-v2
source .venv/bin/activate

# Check prompt rules
grep -A 10 "Tool retry rules" backend/app/prompts/global_context.md

# Check DUPLICATE_CALL error type
grep "DUPLICATE_CALL" backend/app/services/coordinator.py

# Run tests
pytest backend/tests/test_coordinator.py -k "duplicate" -v
```

## Review Questions

1. Does the prompt clearly explain that empty = valid answer?
2. Is the DUPLICATE_CALL error message actionable (tells agent what to do next)?
3. Does the implementation handle both API paths (streaming and non-streaming)?
4. Are there edge cases not covered by the test?

## Verdict

- [x] **pass** — all AC met, no issues
- [ ] **changes** — issues found (list below)

### Findings

Verified 2026-07-28:
- ✅ `global_context.md` has "Tool retry rules" section with 3 clear rules
- ✅ `coordinator.py` implements pre-emptive duplicate detection (on 2nd call)
- ✅ Test verifies correct behavior (15/15 tests pass)
- ✅ Both API paths (streaming + non-streaming) updated

Note: agy reviewer spawn failed (empty output), verified manually via pytest.
