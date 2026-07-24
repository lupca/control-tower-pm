# ADR-010: Mechanical Dispatch and Review-order Scripts

**Status:** Accepted  
**Date:** 2026-07-25  
**Related:** CT-028, ADR-008

## Context

`/dispatch` and `/review-order` repeatedly perform deterministic file and
command-building work. Doing it manually costs tokens and makes status,
registry, model, and four-eyes handling easy to drift.

## Decision

1. `scripts/ct-dispatch.py` resolves the task, project `repo_root`, agent
   profile, and CLI spawn pattern, then prints the command. It never spawns a
   process. `--print-only` is a strict no-write preview; the normal execution
   path records the executor dispatch transition.
2. `scripts/ct-review-order.py` performs the mechanical `dispatched` →
   `in-review` transition and creates the review sheet. It re-checks
   reviewer ≠ executor before any write and supports an all-no-write
   `--dry-run` preview.
3. Both scripts reuse `ct_common.py` for task lookup and frontmatter handling.
   LLM-only work remains in the skills: agent selection, coordination Gates,
   graph risk questions, and audit narrative. A manual fallback remains
   documented if a script cannot run.

## Consequences

Deterministic transitions and spawn commands become testable in `/tmp`
sandboxes, while process spawning and judgment stay explicit coordinator or
User actions. The scripts intentionally do not call code-review-graph or read
executor diffs.
