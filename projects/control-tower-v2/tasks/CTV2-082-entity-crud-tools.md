---
id: CTV2-082
title: "Entity CRUD tools: manage_project / manage_agent / manage_knowledge / update_task + gate wiring"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: high
risk: high
deadline: null
executor: "@claude-sonnet-medium"
reviewer: "@claude-opus"
result_ref: "74bad94"
depends_on:
  - CTV2-080
  - CTV2-081
files:
  - backend/app/services/tool_registry.py
  - backend/app/services/command_router.py
  - backend/app/services/task_orchestration.py
  - backend/app/api/projects.py
  - backend/app/api/agents.py
flows: []
tests:
  - backend/tests/test_command_router.py
  - backend/tests/test_api_projects.py
  - backend/tests/test_api_agents.py
  - backend/tests/test_gates.py
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: medium
prediction_factors:
  score: 0.7
  deductions:
    - "risk cao: LLM có quyền ghi lên projects/agents (-0.15)"
    - "gate wiring cho admin permission là logic mới (-0.15)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-082: Entity CRUD Tools + Gate Wiring (ADR-001 Phase 2c)

> Dự án: [[projects/control-tower-v2/control-tower-v2]]
> Thiết kế: `docs/adr/ADR-001-unified-tool-architecture.md` §D2

## Tiêu chí nghiệm thu (AC)

- [x] `manage_project(action: create|update|archive, ...)` — KHÔNG có hard delete; archive = status change
- [x] `manage_agent(action: create|update|disable, ...)` — không bao giờ nhận/trả giá trị `api_key` (chỉ `has_api_key`)
- [x] `manage_knowledge(action: create|update|archive, ...)` cho KnowledgeItem
- [x] `update_task(task_id, patch)` — sửa plan/AC/priority/tags qua service layer, không đổi status ngoài gate flow
- [x] Tools permission=admin (`manage_project`, `manage_agent`): ở mode `supervised` tạo GateRecord pending → cần `/approve`; ở `bypass` tự approve + audit log
- [x] Mọi mutation ghi AuditLog (actor = session id); đi qua service layer để DB constraints (four-eyes, append-only) giữ nguyên
- [x] Tất cả đăng ký registry, tier=deferred, group đúng (task_lifecycle / admin)

## Verification

- `pytest backend/tests/ -v` → xanh
- Test: `manage_agent` với payload chứa api_key → rejected; `manage_project(action=archive)` ở supervised → gate pending, chưa mutate; sau approve → mutate + audit row

## Plan

1. Handlers trong service layer (tái dùng logic từ api/projects.py, api/agents.py — không duplicate).
2. Gate wiring: mở rộng TaskOrchestrationService hoặc service gate riêng cho non-task mutations (GateRecord.task_id nullable? — nếu cần migration, tách nhỏ và kèm rollback).
3. Registry entries + schema chặt (action enum, required fields per action).
4. Tests per AC.

## Sub-tasks

- [ ] manage_project + manage_knowledge
- [ ] manage_agent (api_key guard)
- [ ] update_task
- [ ] Admin gate wiring + audit
- [ ] Tests
