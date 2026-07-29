---
id: CTV2-049
task_path: projects/control-tower-v2/tasks/CTV2-049-token-telemetry.md
project: control-tower-v2
result_ref: 92b7fbc
executor: "@gpt-5.6-sol"
reviewer: "@claude-opus"
status: passed
issued: 2026-07-26
verdict: pass
verdict_date: 2026-07-26
---

# Phiếu Review: CTV2-049 — Token Telemetry System

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-049-token-telemetry.md`
- Result-ref: 92b7fbc
- Executor: @gpt-5.6-sol
- Reviewer: @claude-opus
- Ngày phát phiếu: 2026-07-26

## Acceptance Criteria cần verify

- [ ] AC1: LLMUsage model created with all fields
- [ ] AC2: All LLM calls (coordinator, executor, reviewer) record usage
- [ ] AC3: Token counts extracted from SDK responses
- [ ] AC4: Cost calculation based on model pricing
- [ ] AC5: Stats API returns aggregated usage
- [ ] AC6: Dashboard shows token usage and reduction %
- [ ] AC7: Comparison against V1 baseline (3,575 tokens/cycle)
- [ ] AC8: Tests verify telemetry recording

## Definition of Done (AGENTS.md mục 3)

- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: test_llm_usage.py, test_token_telemetry.py
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (bạn đang review, hãy xác nhận bạn ≠ @gpt-5.6-sol)

## Test gợi ý chạy trong repo code

```bash
cd /home/lupca/projects/control-tower-v2
pytest backend/tests/test_llm_usage.py -v
pytest backend/tests/test_token_telemetry.py -v
pytest backend/tests/ -v --tb=short
```

## Files to Review

| File | Changes |
|------|---------|
| `backend/app/services/llm_client.py` | NEW - LLM wrapper with token extraction |
| `backend/app/db/models.py` | LLMUsage model |
| `backend/app/api/stats.py` | Token aggregation endpoints |
| `frontend/src/pages/Dashboard.tsx` | Token usage widget |
| `backend/alembic/versions/006_llm_usage.py` | Migration |

## Trả kết quả

`/verdict CTV2-049 <pass|changes> --reviewer @claude-opus [--commit 92b7fbc] [--notes "..."]`
