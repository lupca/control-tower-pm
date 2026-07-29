---
id: CTV2-111
title: "Research: Soft Delete (Archive) Architecture"
status: done
executor: "@claude-opus"
type: research
created: 2026-07-28
deadline: 2026-07-29
priority: high
tests: []
files: []
---

# CTV2-111: Research: Soft Delete (Archive) Architecture

## Mục tiêu

Thiết kế kiến trúc soft delete (archive) cho tất cả data types trong CTV2, đảm bảo:
- Dữ liệu không bị xoá vĩnh viễn, có thể restore
- Cascade archive khi archive parent entity
- API/tool mặc định không trả về rows đã archive

## Acceptance Criteria

- [ ] AC1: Schema design — cột `archived_at` (nullable timestamp) cho: Task, Project, Agent, KnowledgeItem, Session, Settings
- [ ] AC2: Cascade rules — archive Project → archive tất cả Tasks, KnowledgeItems liên quan (cùng transaction)
- [ ] AC3: Query filtering — SQLAlchemy mixin/base query filter `WHERE archived_at IS NULL` mặc định, option để include archived
- [ ] AC4: Tool design — `archive_<entity>` và `restore_<entity>` actions trong existing manage tools, permission=admin
- [ ] AC5: API design — query param `?include_archived=true` cho list endpoints
- [ ] AC6: Audit — archive/restore actions ghi vào audit_log với actor, entity_type, entity_id, timestamp
- [ ] AC7: Migration strategy — Alembic migration thêm cột, không break existing data

## Deliverable

Research doc: `projects/control-tower-v2/docs/research/soft-delete-architecture.md`

## Plan

1. Audit existing models (`backend/app/db/models.py`) — list entities cần thêm `archived_at`
2. Design SQLAlchemy mixin `ArchivableMixin` với:
   - `archived_at: DateTime | None`
   - `archive()` / `restore()` methods
   - Class-level `query` property override hoặc event listener
3. Design cascade logic — có thể dùng SQLAlchemy `relationship` cascade hoặc explicit service layer
4. Design tool/API changes — extend `manage_project`, `manage_agent`, etc. với `action: archive|restore`
5. Write migration strategy — add column với `nullable=True`, no default
6. Document trong research doc

## Audit Trail

- 2026-07-28: created, Spec Gate auto-approved (bypass)
- 2026-07-28: Plan Gate auto-approved (bypass)
- 2026-07-28: Dispatch Gate auto-approved (bypass), executor=@claude-opus
- 2026-07-28: done — deliverable exists (research, no review cycle)
