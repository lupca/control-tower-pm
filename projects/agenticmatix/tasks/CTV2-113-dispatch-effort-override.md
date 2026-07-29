---
id: CTV2-113
title: "Dispatch với effort override"
status: done
dispatched: 2026-07-28
priority: normal
risk: normal
created: 2026-07-28
deadline: null
executor: "@claude-sonnet-medium"
reviewer: "@claude-opus"
result_ref: "b094b1d"
depends_on: []
files:
  - backend/app/db/models.py
  - backend/app/services/tool_registry.py
  - backend/app/services/command_builder.py
  - backend/app/services/task_orchestration.py
  - backend/app/services/command_router.py
tests: []
flows: []
predicted_success: high
prediction_factors:
  score: 0.8
  deductions:
    - "blast_radius: 5 files (-0.0)"
    - "migration required (-0.1)"
    - "touches command_builder (already familiar from CTV2-110) (-0.1)"
confidence_interval: [0.7, 0.9]
in_review: 2026-07-28
updated: 2026-07-28
---

# CTV2-113: Dispatch với effort override

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Context

Hiện tại effort chỉ lấy từ `Agent.effort`, không có cách override per-dispatch. User muốn:
- `/dispatch PMI-029 @gemini-3.6-flash --effort high`
- Chat: "dispatch task với effort cao"

Effort hierarchy: `dispatch_effort > agent.effort > 'medium'`

## Tiêu chí nghiệm thu (AC)

- [x] **AC1**: Migration thêm `AgentRun.effort` column (nullable string)
- [x] **AC2**: `dispatch_task` tool có param `effort` (enum: low|medium|high|extra-high|max)
- [x] **AC3**: `command_builder.build_dispatch_command()` nhận `effort` param và truyền:
  - claude: `--effort <effort>`
  - agy: `--effort <effort>` (nếu hỗ trợ)
  - codex: đã có, giữ nguyên
- [x] **AC4**: `task_orchestration.request_dispatch()` nhận `effort`, lưu vào `AgentRun.effort`, truyền cho command_builder
- [x] **AC5**: `command_router._handle_dispatch_task()` parse `--effort` từ args, truyền vào service
- [x] **AC6**: Unit test cho effort resolution logic

## Plan

1. Migration: `alembic revision --autogenerate -m "add AgentRun.effort"`
2. Update `AgentRun` model: thêm `effort = Column(String(20), nullable=True)`
3. Update `tool_registry.py`: thêm `effort` param vào `dispatch_task` schema
4. Update `command_builder.py`:
   - `build_dispatch_command(task, agent, project, effort=None)`
   - claude/agy: thêm `--effort` flag
5. Update `task_orchestration.py`:
   - `request_dispatch(..., effort=None)`
   - Resolve effort: `effort or agent.effort or 'medium'`
   - Lưu vào `AgentRun.effort`
6. Update `command_router.py`:
   - Parse `--effort` từ args
   - Truyền vào `service.request_dispatch()`
7. Tests

