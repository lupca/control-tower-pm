---
pattern_id: race-condition
category: reliability
severity: high
created: 2026-07-22
updated: 2026-07-22
---

# race-condition

## Problem Signature
Two or more concurrent operations read-modify-write shared state (a DB row, an in-memory counter, a cache entry) without synchronization, producing lost updates or inconsistent state under concurrent load. Symptoms are intermittent and load-dependent — the bug rarely reproduces when tested serially.

## Detection
- Code smell: a read-then-write sequence on shared state with no transaction/lock in between — e.g. `obj.count += 1; obj.save()` outside `select_for_update()`/an atomic transaction.
- Symptom: intermittent test failures under concurrency/load tests, or production data inconsistencies (double-decrements, lost writes) that never reproduce in single-threaded manual testing.
- `code-review-graph`: a hotspot write path reachable from multiple concurrent entry points (e.g. more than one API handler writing the same model/row).

## Solution Template
Replace read-modify-write application code with either DB-level locking (`select_for_update()`, optimistic locking via a version column) or atomic operations (`F()` expressions, `UPDATE ... SET x = x + 1` at the DB layer). Add a concurrency test that fires the operation from multiple threads/tasks and asserts the final state is correct, not just that each individual call succeeds.

## Past Instances
*(none yet)*
