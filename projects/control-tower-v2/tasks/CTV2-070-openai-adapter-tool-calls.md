---
id: CTV2-070
title: "Fix OpenAI Adapter: Parse Tool Calls from API Response"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: high
risk: normal
deadline: null
executor: "@gpt-5.6-luna"
reviewer: "@claude-opus"
result_ref: "bf047f0"
depends_on: []
files:
  - backend/app/services/providers/openai_adapter.py
flows: []
tests:
  - backend/tests/unit/test_openai_adapter.py
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: high
prediction_factors:
  score: 0.9
  deductions:
    - "blast_radius: 1 (-0.0)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-070: Fix OpenAI Adapter: Parse Tool Calls from API Response

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Tiêu chí nghiệm thu (AC)
- [x] OpenAI adapter extracts `tool_calls` from API response (non-streaming)
- [x] OpenAI adapter extracts `tool_calls` from streaming response
- [x] `ProviderResponse` includes tool_calls field populated from response
- [x] Kimi model tool calls are parsed and returned correctly

## Verification
- `cd /home/lupca/projects/control-tower-v2 && pytest backend/tests/unit/test_openai_adapter.py -v` → 100% pass
- Test với Kimi model: gửi prompt với tool definitions, verify tool_calls được parse

## Plan

**Root cause**: `_text()` method only extracts `content` from response, ignores `tool_calls`. `complete()` method doesn't include tool_calls in `ProviderResponse`.

1. **Add tool_calls extraction method** in `openai_adapter.py`:
   - Add `_tool_calls(response)` static method to extract `choices[0].message.tool_calls`
   - Handle both dict and object response formats

2. **Update ProviderResponse** (if needed):
   - Check if `ProviderResponse` has `tool_calls` field
   - Add if missing: `tool_calls: list[dict[str, Any]] | None = None`

3. **Update complete() for non-streaming**:
   - After `normalized.text = self._text(response)`, add:
   - `normalized.tool_calls = self._tool_calls(response)`

4. **Update iter_chunks() for streaming**:
   - Accumulate `tool_calls` deltas across chunks
   - Set `normalized.tool_calls` after stream completes

5. **Update tests**:
   - Add test case for response with tool_calls
   - Add test case for streaming with tool_calls

## Sub-tasks
- [ ] Add `_tool_calls()` extraction method
- [ ] Update `ProviderResponse` dataclass if needed
- [ ] Update `complete()` non-streaming path
- [ ] Update `iter_chunks()` streaming path
- [ ] Add unit tests for tool_calls extraction
