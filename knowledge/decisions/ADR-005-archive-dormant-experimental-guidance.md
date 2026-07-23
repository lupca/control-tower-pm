---
type: decision
scope: general
created: 2026-07-23
updated: 2026-07-23
tags: [control-tower, documentation, skills, experimental]
related: [[ADR-002-paradigm-shifts-roadmap]]
---

# ADR-005: Archive dormant experimental guidance outside the agent instruction set

## Context

`AGENTS-EXPERIMENTAL.md` mixed active operating guidance with dormant POC
designs. Skills still cited that root instruction file, causing agents to load a
large archive while running otherwise routine workflows. The control-tower
project also requires an ADR whenever `AGENTS.md` or a skill changes.

## Decision

Delete `AGENTS-EXPERIMENTAL.md`. Preserve the dormant §14 and §17–§20 designs
verbatim in `docs/experimental-archive.md`, clearly marked as reference-only.
Remove all `AGENTS-EXPERIMENTAL.md` citations from skills while retaining their
already-inlined active instructions, and point the `AGENTS.md` detail-file note
to the archive without making it operational guidance.

Re-enabling an archived feature requires a later explicit decision and new
operational instructions; the archive itself does not activate anything.

## Consequences

- Routine skill execution no longer directs agents to load the former
  experimental instruction bundle.
- Dormant designs remain available for future reconsideration.
- Active skill behavior remains in the skills themselves, so removing the
  citations does not remove currently used workflows.
- The active §12, §13, §15, and §16 source material is no longer consolidated in
  one root archive; its maintained form is the relevant skill guidance.

## Status

Accepted
