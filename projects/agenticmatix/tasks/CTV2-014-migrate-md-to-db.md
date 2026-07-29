---
id: CTV2-014
title: "Migration script: Markdown → PostgreSQL"
status: done
priority: critical
risk: high
executor: "@antigravity"
reviewer: "@gpt-5.6-sol"
deadline: 2026-07-28
created: 2026-07-26
updated: 2026-07-26
completed_at: 2026-07-26
depends_on: [CTV2-011]
files:
  - scripts/migrate_md_to_db.py
  - scripts/parse_frontmatter.py
  - scripts/test_migrate_md_to_db.py
tests:
  - All projects imported correctly
  - All tasks imported with full data
  - All agents imported with stats
  - All knowledge items imported
  - No data loss
---

# CTV2-014: Migration script Markdown → PostgreSQL

## Context
Import toàn bộ data từ control-tower markdown vào database.

## Source Data
```
control-tower/
├── index.md                    → projects table (parse PROJECT REGISTRY)
├── projects/*/tasks/*.md       → tasks table
├── knowledge/agents/@*.md      → agents table
├── knowledge/**/*.md           → knowledge table
└── log.md                      → audit_log table
```

## Acceptance Criteria
- [x] AC1: Parse `index.md` PROJECT REGISTRY → projects
- [x] AC2: Parse all `projects/*/tasks/*.md` → tasks với đầy đủ frontmatter
- [x] AC3: Parse all `knowledge/agents/@*.md` → agents
- [x] AC4: Parse all `knowledge/**/*.md` (non-agents) → knowledge
- [x] AC5: Parse `log.md` → audit_log (optional, complex)
- [x] AC6: Handle edge cases: missing fields, invalid status, etc.
- [x] AC7: Dry-run mode để verify trước khi commit
- [x] AC8: Report: số records imported, errors

## Technical Notes
- Dùng Python script, chạy một lần
- Parse YAML frontmatter với `yaml` library
- Idempotent: chạy lại không duplicate
- Log chi tiết để debug
