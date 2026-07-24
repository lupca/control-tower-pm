---
type: decision
scope: general
created: 2026-07-25
updated: 2026-07-25
tags: [control-tower, skills, lint, validation]
related:
  - "[[ADR-009-mandatory-toolchain-registry]]"
  - "[[ADR-010-dispatch-review-order-scripts]]"
---

# ADR-011: Validate skill health during `/lint`

## Context

Control Tower is operated through `.claude/skills/*/SKILL.md`, but `/lint`
previously checked only backlog tasks and knowledge files. A skill can therefore
break discovery before any task-level health check notices it; for example,
`dispatch/SKILL.md` was missing its required YAML frontmatter.

## Decision

Add `scripts/ct-validate-skills.py` to scan every `.claude/skills/*/SKILL.md`.
The validator follows the required-field and frontmatter checks from
`docs/opensource/quick_validate.py`, while accepting Control Tower extensions
such as `argument-hint` and `allowed-tools`. `/lint` runs it in JSON mode and
reports each finding without modifying any skill. The `dispatch` skill receives
the missing frontmatter so the current skill set is clean.

## Consequences

- Skill metadata defects become visible in the regular backlog health check.
- The validator can be used by CI because it returns a non-zero exit code when
  findings exist and supports machine-readable JSON output.
- `/lint` remains read-only; fixing a skill still requires a separate change and
  review.
- New skill metadata fields do not require validator changes unless they affect
  the required frontmatter structure.

## Alternatives Considered

- Keep using `quick_validate.py` directly: rejected because it validates one
  skill at a time and returns human text rather than an aggregate finding list.
- Make `/lint` repair skill files: rejected because it would violate the
  read-only and review boundaries of the lint workflow.

## Status

Accepted
