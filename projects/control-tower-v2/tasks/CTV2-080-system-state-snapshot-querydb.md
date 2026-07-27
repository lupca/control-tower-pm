---
id: CTV2-080
title: "System State snapshot block + generic query_db tool"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: high
risk: normal
deadline: null
executor: "@claude-sonnet-medium"
reviewer: "@claude-opus"
result_ref: "3e1936a"
depends_on:
  - CTV2-077
files:
  - backend/app/graph/context.py
  - backend/app/services/tool_registry.py
  - backend/app/services/command_router.py
flows: []
tests:
  - backend/tests/test_context_hierarchy.py
  - backend/tests/test_command_router.py
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: high
prediction_factors:
  score: 0.85
  deductions:
    - "cần whitelist filter cẩn thận cho query_db (-0.1)"
    - "cap token snapshot cần đo thực tế (-0.05)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-080: System State Snapshot + query_db (ADR-001 Phase 2a)

> Dự án: [[projects/control-tower-v2/control-tower-v2]]
> Thiết kế: `docs/adr/ADR-001-unified-tool-architecture.md` §D2

## Tiêu chí nghiệm thu (AC)

- [ ] `build_context_snapshot` thêm block `## System State`: Projects (đếm + tên), Agents (đếm, api/cli, default model), Sessions active, Tasks mở theo trạng thái (dispatched/in-review/awaiting approval)
- [ ] Snapshot cap cứng ~30 dòng / ~600 token; enumeration top-N, còn lại chỉ đếm
- [ ] Tool mới `query_db(entity, filters, limit<=50, offset)` — read-only, entity whitelist: tasks|projects|agents|sessions|knowledge|usage; filter fields whitelist per entity
- [ ] `query_db` trả cột compact (id/title/status/…), không dump full row; agents KHÔNG trả `api_key`
- [ ] `query_db` đăng ký trong registry với tier=eager, permission=read
- [ ] `invalidate_context_snapshot` vẫn phủ đúng các mutation mới ảnh hưởng System State (agent/session changes)

## Verification

- `pytest backend/tests/test_context_hierarchy.py backend/tests/test_command_router.py -v` → xanh
- Test: snapshot với 20 projects/50 agents vẫn ≤ cap; `query_db(entity="agents")` không chứa api_key; entity ngoài whitelist → error rõ ràng

## Plan

1. Mở rộng `build_context_snapshot` với các count query (1 query/entity, gộp khi được).
2. Implement handler `query_db` trong service layer + serializer compact per entity.
3. Đăng ký registry + test whitelist/cap.

## Sub-tasks

- [ ] System State block + cap
- [ ] query_db handler + whitelists
- [ ] Registry entry + tests
