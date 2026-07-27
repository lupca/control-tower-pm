---
id: CTV2-107
task_path: projects/control-tower-v2/tasks/CTV2-107-unified-llm-service.md
project: control-tower-v2
result_ref: c4da02cb
executor: @gpt-5.6-luna-high
reviewer: @claude-opus
status: completed
issued: 2026-07-28
verdict: pass
verdict_date: 2026-07-28
---

# Phiếu Review: CTV2-107 — Unified LLMService - Consolidate LLMClient, ProviderRouter, OpenAIAdapter

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-107-unified-llm-service.md`
- Result-ref: c4da02cb
- Executor: @gpt-5.6-luna-high
- Reviewer: @claude-opus
- Ngày phát phiếu: 2026-07-28

## Acceptance Criteria cần verify
## Tiêu chí nghiệm thu (AC)

- [x] Tạo `services/llm_service.py` với class `LLMService` là single entry point cho ALL model calls
- [x] `LLMService.complete(agent: Agent, messages, tools?)` route dựa trên `agent.agent_type`:
  - `api` → `APIProvider` (refactor từ OpenAIAdapter)
  - `cli` → `CLIProvider` (refactor từ CLIDispatcher)
- [x] **Không fallback:** nếu không có agent → raise `ConfigurationError`, không dùng env var
- [x] Xóa `LLMClient` class — tất cả callers chuyển sang `LLMService`
- [x] Xóa `ProviderRouter` từ `coordinator.py` — logic chuyển vào `LLMService`
- [x] Refactor callers:
  - `spec_plan_generator.py` → dùng `LLMService`
  - `context_hierarchy.py` (compaction) → dùng `LLMService`
  - `coordinator.py` → dùng `LLMService`
- [x] **Test coverage TRƯỚC refactor:** đảm bảo tests hiện tại cover đủ behavior
- [x] **Test pass SAU refactor:** tất cả tests trong `tests:` vẫn pass
- [x] Giữ lại `UsageCounts`, `calculate_cost`, `extract_usage` từ `llm_client.py` (telemetry utils, không duplicate)

## Definition of Done (AGENTS.md mục 3)
- [x] Toàn bộ AC pass
- [x] Test liên quan xanh 100%: backend/tests/test_llm_usage.py, backend/tests/test_coordinator.py, backend/tests/test_cli_coordinator.py, backend/tests/unit/test_openai_adapter.py, backend/tests/test_spec_plan_generator.py
- [x] Không regression (test khác trong module vẫn xanh) — 440/441 passed, 1 failure pre-existing (test_db transaction state)
- [x] Reviewer khác executor (xác nhận reviewer @claude-opus ≠ executor @gpt-5.6-luna-high)

## Test gợi ý chạy trong repo code
- `backend/tests/test_llm_usage.py`
- `backend/tests/test_coordinator.py`
- `backend/tests/test_cli_coordinator.py`
- `backend/tests/unit/test_openai_adapter.py`
- `backend/tests/test_spec_plan_generator.py`

## Câu hỏi rủi ro (từ code-review-graph, tĩnh — không thay thế việc tự đọc diff)
- *(LLM/coordinator bổ sung từ graph nếu có; script không đọc diff và không gọi graph.)*

## Review Toolchain
Chạy theo toolchain của repo đích; preflight các tool đã đăng ký trước khi review.

## Trả kết quả
`/verdict CTV2-107 <pass|changes> --reviewer @claude-opus [--commit <hash>] [--notes "..."]`
