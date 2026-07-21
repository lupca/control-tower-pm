---
pattern_id: missing-db-index
category: performance
severity: medium
created: 2026-07-22
updated: 2026-07-22
---

# missing-db-index

## Problem Signature
A query filters, sorts, or joins on a column with no supporting index, forcing a full table scan. Latency is fine on a small/empty table and degrades as the table grows — often invisible in dev/staging and only surfaces in production.

## Detection
- `EXPLAIN`/`EXPLAIN ANALYZE` on the query shows `Seq Scan` (Postgres) or an equivalent full-scan plan on a table beyond trivial size.
- Slow-query log entries whose latency correlates with `WHERE`/`ORDER BY`/`JOIN` on a specific column, with no index covering it.
- `code-review-graph`: a model/migration defines a foreign key or a column used in frequent filters/sorts without a corresponding index in the schema.

## Solution Template
Add a migration creating an index on the column(s) actually used in the filter/sort/join — single-column for a simple equality filter, composite (matching column order to the query) for multi-column filters. Verify with `EXPLAIN` before/after showing an index scan replacing the sequential scan, and add a migration test so the index isn't silently dropped later.

## Past Instances
*(none yet)*
