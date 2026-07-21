---
pattern_id: memory-leak
category: reliability
severity: high
created: 2026-07-22
updated: 2026-07-22
---

# memory-leak

## Problem Signature
Process memory usage grows monotonically over the process's lifetime instead of stabilizing, eventually causing OOM kills or forced restarts. Typically invisible in short-lived dev/test runs and only surfaces after hours/days of production uptime.

## Detection
- Symptom: RSS/heap graphs trend upward over time with no sawtooth pattern (GC isn't reclaiming); `OOMKilled` events in orchestrator/container logs.
- Code smell: an unbounded cache/dict/list that's appended to but never evicted; event listeners/subscriptions/callbacks registered but never unregistered on teardown; reference cycles in a runtime without a cycle collector.
- Profiling: a heap snapshot diff between two points in time shows one object type growing without bound.

## Solution Template
Bound caches with an explicit eviction policy (LRU/TTL/max-size), ensure every listener/subscription registered on setup is unregistered on teardown, and break needless reference cycles. Add a soak test that exercises the suspect code path repeatedly (well beyond normal usage) and asserts memory stays within a bound, rather than relying on a single-run functional test.

## Past Instances
*(none yet)*
