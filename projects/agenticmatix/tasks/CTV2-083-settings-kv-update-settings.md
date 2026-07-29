---
id: CTV2-083
title: "Settings KV table + update_settings tool"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: medium
risk: normal
deadline: null
executor: "@claude-sonnet-medium"
reviewer: "@claude-opus"
result_ref: "45a4bfa"
depends_on:
  - CTV2-082
files:
  - backend/app/db/models.py
  - backend/alembic/versions/
  - backend/app/services/tool_registry.py
flows: []
tests:
  - backend/tests/test_db.py
  - backend/tests/test_command_router.py
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: high
prediction_factors:
  score: 0.85
  deductions:
    - "migration mới cần rollback script theo project gate (-0.1)"
    - "chưa chốt danh sách settings key ban đầu (-0.05)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-083: Settings KV + update_settings (ADR-001 Phase 2d)

> Dự án: [[projects/control-tower-v2/control-tower-v2]]
> Thiết kế: `docs/adr/ADR-001-unified-tool-architecture.md` §D2 — lưu ý: hiện KHÔNG có model Settings trong `db/models.py`.

## Tiêu chí nghiệm thu (AC)

- [x] Model `Setting` (key PK, value JSON, description, updated_at) + Alembic migration KÈM downgrade (quy tắc project: mọi migration phải có rollback)
- [x] Key whitelist khởi tạo (vd: `default_coordinator_model`, `default_mode`, `context_snapshot_top_n`) — `update_settings` từ chối key ngoài whitelist
- [x] Tool `update_settings(key, value)` + `query_db(entity="settings")` cho read; permission=admin, tier=deferred (group admin), qua gate như CTV2-082
- [x] Mutation ghi AuditLog

## Verification

- `alembic upgrade head && alembic downgrade -1 && alembic upgrade head` → sạch
- `pytest backend/tests/test_db.py backend/tests/test_command_router.py -v` → xanh
- `update_settings("bogus_key", ...)` → error rõ ràng, không ghi DB

## Plan

1. Model + migration (up/down).
2. Service handler + whitelist + registry entry.
3. Gate/audit wiring (tái dùng CTV2-082).
4. Tests.

## Sub-tasks

- [x] Model + migration có rollback
- [x] Handler + whitelist
- [x] Registry + gate
- [x] Tests
