---
pattern_id: n-plus-one-query
category: performance
severity: medium
created: 2026-07-22
updated: 2026-07-22
---

# n-plus-one-query

## Problem Signature
A loop issues one database query per iteration instead of a single batched query — most commonly, iterating over a queryset/result set and accessing a related object or foreign key inside the loop body, where each access triggers a fresh `SELECT`. Query count scales linearly with the number of rows (N rows → N+1 queries: 1 for the initial list, N for the related lookups).

## Detection
- Code smell: `for x in queryset: x.related_field.attr` (Django) or the equivalent in another ORM, with no eager-loading directive on the initial query.
- `code-review-graph`: `query_graph_tool`/`get_impact_radius_tool` on a hotspot function shows high fan-out to DB-access nodes from inside a loop body.
- Runtime: query count in APM/query logs scales with result-set size; slow endpoints whose query count grows with pagination/list size are a strong signal.

## Solution Template
Use the ORM's eager-loading mechanism to batch related lookups into 1-2 queries instead of N+1:
- `select_related()` for foreign-key / one-to-one relations (SQL JOIN).
- `prefetch_related()` for many-to-many / reverse-FK relations (separate batched query).
Verify the fix with a query-count assertion in a test (e.g. `assertNumQueries(2)`), not just a passing functional test — the regression is about query count, not correctness.

## Past Instances
*(none yet)*
