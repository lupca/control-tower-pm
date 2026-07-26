---
id: CTV2-011
title: "Database Schema V2 - Full data model migration"
status: done
priority: critical
risk: medium
executor: "@antigravity-teamwork"
reviewer: "@gpt-5.6-sol"
dispatched: 2026-07-26
in_review: 2026-07-26
done: 2026-07-26
deadline: 2026-07-28
created: 2026-07-26
updated: 2026-07-26
files:
  - backend/alembic/versions/002_schema_v2.py
  - backend/app/db/models.py
tests:
  - All tables created successfully
  - Foreign keys work correctly
  - Indexes created
---

# CTV2-011: Database Schema V2

## Context
Mở rộng database schema để chứa toàn bộ data từ markdown (projects, agents, knowledge).

## Acceptance Criteria
- [ ] AC1: Tạo table `projects` với đầy đủ fields (repo_root, graph_status, etc.)
- [ ] AC2: Mở rộng table `tasks` thêm fields (body, project_id FK, dispatched_at, in_review_at, done_at)
- [ ] AC3: Tạo table `agents` với performance stats
- [ ] AC4: Tạo table `knowledge` với type categorization
- [ ] AC5: Update `sessions` thêm mode, state fields
- [ ] AC6: Tạo Alembic migration file
- [ ] AC7: Tất cả indexes được tạo đúng

## Technical Notes
- Xem design: `docs/database-design-v2.md`
- Dùng Alembic cho migration
- JSONB cho arrays (acceptance_criteria, files, strengths, etc.)
