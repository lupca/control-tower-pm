---
id: CTV2-106
title: "Spec/Plan Generation Model Selection (giống Dispatch Gate)"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: high
risk: high
deadline: null
executor: "@claude-sonnet-medium"
reviewer: null
result_ref: "53c79bf"
depends_on: []
files:
  - backend/app/services/spec_plan_generator.py
  - backend/app/services/llm_client.py
  - backend/app/services/task_orchestration.py
  - backend/app/db/models.py
  - backend/app/services/command_router.py
flows: []
tests:
  - backend/tests/test_llm_usage.py
  - backend/tests/test_task_orchestration.py
  - backend/tests/test_gates.py
dispatched: 2026-07-28
in_review: null
predicted_success: low
prediction_factors:
  score: 0.2
  deductions:
    - "blast_radius: 70 files (-0.5)"
    - "hub node: TaskOrchestrationService (88 degree) (-0.2)"
    - "no direct tests for spec_plan_generator.py (-0.1)"
created: 2026-07-28
updated: 2026-07-28T01:38
---

# CTV2-106: Spec/Plan Generation Model Selection (giống Dispatch Gate)

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

Hiện tại `generate_spec_plan` hardcode dùng `LLM_PROVIDER` env var (mặc định SiliconFlow). Cần refactor để model selection hoạt động giống Dispatch Gate: supervised mode hỏi human, bypass mode tự chọn.

## Tiêu chí nghiệm thu (AC)

- [ ] `generate_spec_plan` đọc model từ Settings table (key: `spec_plan_model`) hoặc Project config, fallback về env var
- [ ] supervised mode: tạo gate record `pending`, trả về prompt hỏi human chọn model/agent nào để sinh spec/plan
- [ ] bypass mode: tự động chọn model từ config, log `auto-approved: spec_plan_model` vào audit
- [ ] Có thể chọn agent từ `agents` table (filter by capability `coordinator` hoặc `spec_plan`) thay vì chỉ model string
- [ ] Fallback chain: Project.autonomy_policy["spec_plan_model"] > Settings["spec_plan_model"] > env `LLM_PROVIDER`
- [ ] Test: supervised mode với spec_plan_model chưa set → pending gate, human phải approve
- [ ] Test: bypass mode với spec_plan_model set → auto-select, no pending

## Verification

- `pytest backend/tests/test_gates.py backend/tests/test_task_orchestration.py -v -k spec_plan` → xanh
- `grep -r "spec_plan_model" backend/app/` → có trong task_orchestration.py hoặc coordinator
- Manual: set `mode: supervised`, call `generate_spec_plan` → phải pending chờ approve

## Plan

1. **db/models.py** — Thêm `Setting` entity nếu chưa có (đã có → skip), đảm bảo có key `spec_plan_model` type string
2. **task_orchestration.py** — Thêm method `resolve_spec_plan_model(project)` theo pattern của `resolve_autonomy()`:
   - Project.autonomy_policy["spec_plan_model"] > Settings["spec_plan_model"] > env LLM_PROVIDER
   - Return tuple (provider, model) hoặc agent_id
3. **spec_plan_generator.py** — Refactor `generate_spec_plan`:
   - Nhận thêm param `model_config: dict | None` (provider, model, hoặc agent_id)
   - Nếu None → gọi `resolve_spec_plan_model()` để lấy default
   - Truyền provider/model vào `LLMClient(provider=...)` thay vì dùng default
4. **command_router.py** — `_handle_generate_spec_plan`:
   - Đọc mode từ `resolve_autonomy()`
   - supervised: tạo pending GateRecord với payload chứa suggested model, return early
   - bypass: gọi `generate_spec_plan(model_config=auto_selected)`, log auto-approved
5. **agents table** — Thêm capability filter: agent có `capabilities` chứa `coordinator` hoặc `spec_plan` mới được suggest
6. **Tests**:
   - test_gates.py: supervised mode → pending gate record
   - test_gates.py: bypass mode → auto-approve, task có AC/plan sau call

## Sub-tasks

- [ ] Thêm `spec_plan_model` vào Settings schema / Project.autonomy_policy
- [ ] Refactor `generate_spec_plan` để nhận model/agent_id từ caller thay vì hardcode
- [ ] Tích hợp với gate system: supervised → pending, bypass → auto-approve
- [ ] Thêm agent capability filter cho spec/plan generation
- [ ] Viết tests cho cả hai modes

## Notes

**Low prediction (0.2)** do blast radius lớn và chạm hub node.

## Closure Note (2026-07-28)

**Thiết kế của Opus 4.5 chưa đạt yêu cầu.** Human đã chỉnh lại thiết kế tốt hơn:

1. **Vấn đề với implementation hiện tại:**
   - Vẫn dùng fallback chain (Project → Setting → env) — nên error nếu không config
   - Vẫn dùng `LLMClient` riêng — nên reuse infrastructure của coordinator chat
   - Không support cả CLI và API agents

2. **Thiết kế mới (CTV2-107):**
   - Unified `LLMService` thay thế cả `LLMClient`, `ProviderRouter`, `OpenAIAdapter`
   - Route dựa trên `Agent.agent_type` (API hoặc CLI)
   - Không fallback, thiếu config → error rõ ràng
   - Đảm bảo test coverage trước khi refactor

Commit 53c79bf được giữ lại nhưng sẽ bị supersede bởi CTV2-107.
