---
id: CTV2-107
title: "Unified LLMService - Consolidate LLMClient, ProviderRouter, OpenAIAdapter"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: high
risk: high
deadline: null
executor: "@gpt-5.6-luna-high"
reviewer: "@claude-opus"
result_ref: "c4da02cb"
depends_on: []
files:
  - backend/app/services/llm_client.py
  - backend/app/services/coordinator.py
  - backend/app/services/cli_dispatcher.py
  - backend/app/services/providers/openai_adapter.py
  - backend/app/services/providers/__init__.py
  - backend/app/services/spec_plan_generator.py
  - backend/app/services/context_hierarchy.py
  - backend/app/db/models.py
flows: []
tests:
  - backend/tests/test_llm_usage.py
  - backend/tests/test_coordinator.py
  - backend/tests/test_cli_coordinator.py
  - backend/tests/unit/test_openai_adapter.py
  - backend/tests/test_spec_plan_generator.py
dispatched: 2026-07-28
in_review: 2026-07-28
predicted_success: medium
prediction_factors:
  score: 0.55
  deductions:
    - "blast_radius: 8 files (-0.1)"
    - "hub node: CoordinatorService (51 degree) (-0.2)"
    - "refactor risk: consolidating 3 components (-0.15)"
created: 2026-07-28
updated: 2026-07-28
---

# CTV2-107: Unified LLMService

> Dự án: [[projects/control-tower-v2/control-tower-v2]]
> Supersedes: CTV2-106 (thiết kế không đạt yêu cầu)

Consolidate 3 duplicate LLM invocation paths (`LLMClient`, `ProviderRouter + OpenAIAdapter`, `CLIDispatcher`) thành một unified `LLMService`.

## Tiêu chí nghiệm thu (AC)

- [ ] Tạo `services/llm_service.py` với class `LLMService` là single entry point cho ALL model calls
- [ ] `LLMService.complete(agent: Agent, messages, tools?)` route dựa trên `agent.agent_type`:
  - `api` → `APIProvider` (refactor từ OpenAIAdapter)
  - `cli` → `CLIProvider` (refactor từ CLIDispatcher)
- [ ] **Không fallback:** nếu không có agent → raise `ConfigurationError`, không dùng env var
- [ ] Xóa `LLMClient` class — tất cả callers chuyển sang `LLMService`
- [ ] Xóa `ProviderRouter` từ `coordinator.py` — logic chuyển vào `LLMService`
- [ ] Refactor callers:
  - `spec_plan_generator.py` → dùng `LLMService`
  - `context_hierarchy.py` (compaction) → dùng `LLMService`
  - `coordinator.py` → dùng `LLMService`
- [ ] **Test coverage TRƯỚC refactor:** đảm bảo tests hiện tại cover đủ behavior
- [ ] **Test pass SAU refactor:** tất cả tests trong `tests:` vẫn pass
- [ ] Giữ lại `UsageCounts`, `calculate_cost`, `extract_usage` từ `llm_client.py` (telemetry utils, không duplicate)

## Verification

- `pytest backend/tests/ -v --tb=short` → tất cả tests pass
- `grep -r "LLMClient" backend/app/` → chỉ còn trong `llm_client.py` (nếu giữ telemetry utils) hoặc 0 matches
- `grep -r "ProviderRouter" backend/app/` → 0 matches (đã move vào LLMService)

## Plan

1. **Audit test coverage:** chạy `pytest --cov=backend/app/services` để biết coverage hiện tại của `llm_client.py`, `coordinator.py`, `cli_dispatcher.py`, `providers/`
2. **Thêm tests nếu thiếu:** đảm bảo các paths chính đều có test trước khi refactor
3. **Tạo `services/llm_service.py`:**
   - `LLMService` class với `complete()` và `stream()` methods
   - Route dựa trên `Agent.agent_type`
   - Raise `ConfigurationError` nếu không có agent
4. **Refactor `providers/api_provider.py`:** rename/refactor `OpenAIAdapter` thành `APIProvider`
5. **Refactor `providers/cli_provider.py`:** extract CLI logic từ `CLIDispatcher`
6. **Migrate callers một-một:**
   - `spec_plan_generator.py` (đơn giản nhất)
   - `context_hierarchy.py` (compaction)
   - `coordinator.py` (phức tạp nhất, có streaming)
7. **Xóa dead code:** `LLMClient` class, `ProviderRouter`
8. **Run full test suite:** đảm bảo không regression

## Sub-tasks

- [ ] Audit + document current test coverage
- [ ] Add missing tests for uncovered paths
- [ ] Create `LLMService` skeleton với routing logic
- [ ] Implement `APIProvider` (refactor OpenAIAdapter)
- [ ] Implement `CLIProvider` (refactor CLIDispatcher)
- [ ] Migrate `spec_plan_generator.py`
- [ ] Migrate `context_hierarchy.py`
- [ ] Migrate `coordinator.py`
- [ ] Remove `LLMClient`, `ProviderRouter`
- [ ] Final test run + cleanup

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        LLMService                                │
│  (single entry point for ALL model calls)                        │
├─────────────────────────────────────────────────────────────────┤
│  complete(agent: Agent, messages, tools?) -> LLMResponse        │
│  stream(agent: Agent, messages, tools?) -> AsyncIterator        │
├─────────────────────────────────────────────────────────────────┤
│                            │                                     │
│         ┌──────────────────┴──────────────────┐                 │
│         ▼                                      ▼                 │
│  ┌─────────────────┐                   ┌─────────────────┐      │
│  │ APIProvider     │                   │ CLIProvider     │      │
│  │ (agent_type=api)│                   │ (agent_type=cli)│      │
│  ├─────────────────┤                   ├─────────────────┤      │
│  │ OpenAI-compat   │                   │ claude, agy,    │      │
│  │ API calls       │                   │ codex CLI spawn │      │
│  └─────────────────┘                   └─────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

## Safety Notes

- **Test-first:** Không refactor trước khi có đủ test coverage
- **Migrate từng caller:** Không big-bang, migrate một file rồi test
- **Keep telemetry:** `UsageCounts`, `calculate_cost` giữ nguyên (có thể move sang `llm_service.py` hoặc `llm_telemetry.py`)
