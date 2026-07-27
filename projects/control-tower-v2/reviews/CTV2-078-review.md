---
id: CTV2-078
task_path: projects/control-tower-v2/tasks/CTV2-078-cache-aware-context-layout.md
project: control-tower-v2
result_ref: 46e2aee
executor: @claude-sonnet-medium
reviewer: "@claude-opus"
status: passed
issued: 2026-07-27
verdict: pass
verdict_date: 2026-07-27
---

# Phiếu Review: CTV2-078 — Cache-aware context layout: tách snapshot khỏi prefix, bỏ cache_control Anthropic

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-078-cache-aware-context-layout.md`
- Result-ref: 46e2aee
- Executor: @claude-sonnet-medium
- Reviewer: @claude-opus
- Ngày phát phiếu: 2026-07-27

## Acceptance Criteria cần verify

- [x] Snapshot không còn append vào message Global; phát thành message riêng đặt SAU Project tier, TRƯỚC Task tier
- [x] Thứ tự volatility tăng dần: global (static) → project (semi-stable) → snapshot (dynamic) → task/session (dynamic)
- [x] Bỏ phát `cache_control` trong `build_messages`; prefix pinning trong `budget_messages` chuyển sang flag tường minh `pinned: True` trên message
- [x] Messages gửi tới OpenAI adapter không chứa key `cache_control`/`pinned` (adapter strip hoặc build strip)
- [x] Hành vi compact/budget giữ nguyên với test hiện có

## Definition of Done (AGENTS.md mục 3)
- [x] Toàn bộ AC pass
- [x] Test liên quan xanh 100%: backend/tests/test_context_hierarchy.py, backend/tests/test_coordinator.py
- [x] Không regression (test khác trong module vẫn xanh)
- [x] Reviewer khác executor (xác nhận reviewer @claude-opus ≠ executor @claude-sonnet-medium)

## Review Toolchain Results

### 1. OCR Review
```
ocr review --from main --to 46e2aee --format json
```
**Result**: `{"status": "skipped", "message": "No supported files changed."}`

### 2. Ruff Linter
```
ruff check backend/app/services/context_hierarchy.py backend/app/services/coordinator.py
```
**Result**: 6 findings (style-only, non-blocking):
- I001: Import sorting (auto-fixable)
- BLE001: Broad exception catches (existing defensive patterns for file reads)
- RUF012: Mutable class attribute (existing pattern)

None of these are correctness issues or related to the AC items.

## AC Verification Details

| AC | Verification |
|----|--------------|
| **AC1** | `build_messages` (context_hierarchy.py:232-235) creates snapshot as separate system message at Tier 2.5. Test `test_build_messages_tiered_ordering_and_pinned_flag` verifies messages[2] is the snapshot, positioned after global[0] and project[1], before task[3]. |
| **AC2** | Comment on lines 205-211 documents ordering. Verified by test assertions on message indices and `pinned` flags. |
| **AC3** | `build_messages` sets `pinned: True` on global (line 224) and project (line 230) messages. No `cache_control` in build_messages. `budget_messages` (coordinator.py:398) checks `message.get("pinned")`. Tests assert `"cache_control" not in` each message. |
| **AC4** | `OpenAIAdapter.render_messages` (openai_adapter.py:48-82) builds new dicts with only API-relevant keys (role, content, tool_call_id, name, tool_calls). Test `test_render_messages_and_tools_converts_canonical_shapes` explicitly verifies input with `cache_control`/`pinned` produces output without them. |
| **AC5** | All 19 tests in test_context_hierarchy.py and test_coordinator.py pass. `test_context_compaction` and `test_context_budget_keeps_newest_turns_and_system_prefix` verify unchanged behavior. |

## Test Results

```
pytest backend/tests/test_context_hierarchy.py backend/tests/test_coordinator.py -v
19 passed in 0.42s

pytest backend/tests/ -v
277 passed in 16.56s
```

Key tests validating CTV2-078:
- `test_build_messages_tiered_ordering_and_pinned_flag`: Verifies tier ordering and pinned flags
- `test_build_messages_prefix_stable_across_task_mutation`: Verifies Global/Project bytes unchanged when task mutates; only snapshot changes
- `test_render_messages_and_tools_converts_canonical_shapes`: Verifies OpenAI adapter strips metadata keys

## Verdict

**PASS**

All acceptance criteria verified. Implementation correctly separates snapshot into its own message at Tier 2.5, uses `pinned: True` instead of `cache_control` for prefix stability, and ensures OpenAI adapter receives clean messages. 277 tests pass with no regressions.

---

Reviewed by: @claude-opus
Date: 2026-07-27
Commit: 46e2aee
