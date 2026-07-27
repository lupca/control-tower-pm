---
id: CTV2-110
title: "Hotfix: Token Telemetry & Dynamic Pricing"
status: done
priority: high
risk: low
executor: "@claude-opus"
reviewer: "@lupca"
result_ref: "fa3577c"
depends_on: []
files:
  - backend/app/services/coordinator.py
  - backend/app/services/llm_client.py
  - backend/app/services/llm.py
  - backend/app/core/config.py
  - backend/app/api/stats.py
  - backend/app/db/models.py
flows: []
tests: []
dispatched: 2026-07-28
in_review: 2026-07-28
predicted_success: high
created: 2026-07-28
updated: 2026-07-28
---

# CTV2-110: Hotfix: Token Telemetry & Dynamic Pricing

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Tiêu chí nghiệm thu (AC)

- [x] Track đúng operation type (chat/tool/plan) thay vì hardcode "chat"
- [x] Tool call responses được track riêng (không chỉ final response)
- [x] Pricing đọc từ DB (`model_pricing` table) thay vì hardcode
- [x] Xóa unused env var constants (SILICONFLOW_*, ANTHROPIC_*, GOOGLE_*, etc.)
- [x] API endpoint GET /api/stats/pricing trả về bảng giá từ DB

## Changes

### 1. Operation Type Detection (e4275f9)
```python
# coordinator.py - _record_usage()
operation = "chat"
if response.tool_calls:
    operation = "tool"
elif db_session.current_gate == "plan":
    operation = "plan"
```

### 2. Track Tool Calls Separately (53ef861)
- Mỗi LLM call có `tool_calls` → tracked ngay trong loop
- Final response (không có tool_calls) → tracked trong `_persist_success`

### 3. Dynamic Pricing from DB (e46a597)
- `get_model_pricing()` query `model_pricing` table
- Cache results, fallback to provider defaults
- `refresh_pricing_cache()` để force refresh

### 4. Cleanup Unused Constants (fa3577c)
- Removed: LLM_PROVIDER, SILICONFLOW_*, ANTHROPIC_*, GOOGLE_*, OPENAI_*
- All config now from DB (agents + model_pricing tables)

## Commits
- e4275f9: fix: track LLM operation type
- 53ef861: fix: track tool call LLM responses separately
- e46a597: refactor: load model pricing from DB
- fa3577c: chore: remove unused LLM env var constants
