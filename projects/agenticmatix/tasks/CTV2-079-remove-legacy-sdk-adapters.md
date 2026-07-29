---
id: CTV2-079
title: "Xoá legacy SDK adapters (Anthropic/Google) + compatibility seam"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: medium
risk: normal
deadline: null
executor: "@claude-sonnet-medium"
reviewer: "@claude-opus"
result_ref: "3e1936a"
depends_on:
  - CTV2-077
files:
  - backend/app/services/providers/anthropic_adapter.py
  - backend/app/services/providers/google_adapter.py
  - backend/app/services/coordinator.py
  - backend/app/services/llm_client.py
flows: []
tests:
  - backend/tests/test_providers.py
  - backend/tests/test_coordinator.py
  - backend/tests/test_cli_coordinator.py
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: high
prediction_factors:
  score: 0.85
  deductions:
    - "tests hiện có có thể đang mock 2 adapter này (-0.15)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-079: Remove Legacy SDK Adapters (ADR-001 Phase 1c)

> Dự án: [[projects/control-tower-v2/control-tower-v2]]
> Thiết kế: `docs/adr/ADR-001-unified-tool-architecture.md` §D6, fix P3

## Bối cảnh

Quyết định 2026-07: bỏ SDK Claude/Antigravity. Coordinator chỉ còn: OpenAI-compatible API (OpenAIAdapter) + CLI dispatch (claude/agy/codex). `ProviderRouter` vẫn default AnthropicAdapter/GoogleAdapter, kèm seam `_explicit_provider_compatibility` — dead code.

## Tiêu chí nghiệm thu (AC)

- [x] Xoá `providers/anthropic_adapter.py`, `providers/google_adapter.py`
- [x] `ProviderRouter` chỉ resolve OpenAIAdapter (từ Agent DB record); anthropic/google model → luôn đi đường CLI qua `route_model`
- [x] Xoá seam `_explicit_provider_compatibility` và nhánh legacy trong `_resolve_selection`
- [x] `DEFAULT_CONTEXT_WINDOWS` bổ sung entry mặc định cho OpenAI-compatible models (không rơi về min ngầm định)
- [x] Không còn import `anthropic`/`google.genai` SDK trong backend (trừ requirements nếu CLI cần — kiểm tra và dọn requirements.txt)

## Verification

- `grep -r "AnthropicAdapter\|GoogleAdapter" backend/app/` → rỗng
- `pytest backend/tests/ -v` → xanh (tests mock adapter cũ được viết lại theo OpenAI/CLI path)

## Plan

1. Inventory usage 2 adapter trong app + tests.
2. Xoá adapter, đơn giản hoá ProviderRouter/_resolve_selection.
3. Viết lại tests bị ảnh hưởng theo 2 đường còn lại.
4. Dọn requirements + docs (README "LLM: Claude API" → cập nhật).

## Sub-tasks

- [ ] Inventory + xoá adapters
- [ ] Đơn giản hoá router/selection
- [ ] Sửa tests
- [ ] Dọn requirements/README
