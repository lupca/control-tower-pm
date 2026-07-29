---
id: CTV2-021
title: "Run migration: MD → PostgreSQL"
status: done
priority: high
risk: low
executor: "@gemini-3.6-flash"
reviewer: "@gpt-5.6-sol"
deadline: 2026-07-28
created: 2026-07-26
files:
  - scripts/migrate_md_to_db.py
tests:
  - All projects imported from index.md
  - All tasks imported from projects/*/tasks/*.md
  - All agents imported from knowledge/agents/@*.md
  - Verify data in dashboard after migration
---

# CTV2-021: Run migration MD → PostgreSQL

## Context
Migration script đã có (`scripts/migrate_md_to_db.py`) nhưng chưa chạy do SSHFS mount issue với Docker.

## Acceptance Criteria
- [ ] AC1: Chạy migration script thành công
- [ ] AC2: Verify projects imported (check /api/projects)
- [ ] AC3: Verify tasks imported (check /api/tasks)
- [ ] AC4: Verify agents imported (check /api/agents)
- [ ] AC5: Dashboard hiển thị data đúng

## Workaround
Chạy trực tiếp trên máy host với venv:
```bash
cd control-tower-v2
python -m venv .venv
source .venv/bin/activate
pip install sqlalchemy pyyaml psycopg2-binary
python scripts/migrate_md_to_db.py
```
