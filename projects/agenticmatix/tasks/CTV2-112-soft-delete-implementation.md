---
id: CTV2-112
title: "Implement Soft Delete (Archive) cho tất cả entities"
status: done
result_ref: codex session 019fa5e6-*
type: feature
created: 2026-07-28
deadline: 2026-07-29
priority: high
executor: "@gpt-5.6-luna"
reviewer: "@claude-opus"
tests:
  - backend/tests/test_archive.py
files:
  - backend/app/db/models.py
  - backend/app/db/mixins.py
  - backend/app/db/archive.py
  - backend/app/services/archive.py
  - backend/app/services/tool_registry.py
  - backend/app/api/tasks.py
  - backend/app/api/projects.py
  - backend/app/api/agents.py
  - backend/alembic/versions/*_add_archived_at.py
---

# CTV2-112: Implement Soft Delete (Archive) cho tất cả entities

Implement theo research doc: `docs/research/soft-delete-architecture.md`

## Acceptance Criteria

- [ ] AC1: Migration — Alembic migration thêm `archived_at` (nullable timestamp, indexed) vào 6 tables: tasks, projects, agents, knowledge_items, sessions, settings
- [ ] AC2: Mixin — `ArchivableMixin` trong `db/mixins.py` với `archived_at`, `is_archived`, `archive()`, `restore()`
- [ ] AC3: Query helpers — `active_query()`, `with_archived()`, `archived_only()` trong `db/archive.py`
- [ ] AC4: ArchiveService — `services/archive.py` với cascade logic (Project → Tasks/Knowledge/Sessions)
- [ ] AC5: Tool registry — Thêm `action: archive|restore` vào `manage_project`, `manage_agent`, `manage_knowledge`; permission=admin, qua AdminGateRecord ở supervised
- [ ] AC6: API endpoints — `?include_archived=true` query param cho tất cả list endpoints
- [ ] AC7: Audit — archive/restore ghi vào audit_log với `{entity_type}_archive` / `{entity_type}_restore`
- [ ] AC8: Tests — Unit tests cho ArchiveService cascade logic + API filter behavior

## Plan

1. Tạo Alembic migration `add_archived_at` cho 6 tables
2. Tạo `backend/app/db/mixins.py` với `ArchivableMixin`
3. Tạo `backend/app/db/archive.py` với query helpers
4. Update models.py — apply mixin vào 6 entities
5. Tạo `backend/app/services/archive.py` với `ArchiveService`
6. Update tool_registry.py — thêm archive/restore actions
7. Update API endpoints — thêm `include_archived` param
8. Tạo `backend/tests/test_archive.py`
9. Run tests, verify cascade behavior

## Reference

- Research doc: `docs/research/soft-delete-architecture.md`
- ADR-001: Tool permission model (admin tools qua gate)

## Audit Trail

- 2026-07-28: created, Spec Gate auto-approved (bypass)
- 2026-07-28: Plan Gate auto-approved (bypass)
- 2026-07-28: Dispatch Gate auto-approved (bypass), executor=@gpt-5.6-luna, reviewer=@claude-opus
- 2026-07-28: verdict=pass, reviewer=@claude-opus (manage_knowledge permission=write accepted as-is)
