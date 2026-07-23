---
type: decision
scope: general
created: 2026-07-23
updated: 2026-07-23
tags: [control-tower, coordination, gates, workflow]
related:
  - "[[ADR-001-file-over-api]]"
  - "[[ADR-003-model-a-cli-agent-orchestration]]"
---

# ADR-006: Separate coordination modes, gates, and task states

## Context

The task lifecycle used `ready` both as a durable state and as a short-lived
marker between Plan approval and dispatch. At the same time, every interactive
Gate unconditionally ended the current invocation. That made a fully authorized
automated run require several disconnected turns and encouraged callers to
mistake a Gate for a task state.

Control Tower still needs a conservative default, a planning-only posture, and
an explicit way for a human to authorize a complete coordination flow without
removing audit side effects or weakening separation of duties.

## Decision

Store one repository-wide coordination mode in `state/mode.md`:

- `plan-only` allows planning checkpoints but blocks Dispatch and Verdict;
- `supervised` is the default and stops for explicit confirmation at every Gate;
- `bypass` treats ordinary Gates as pre-authorized, logs each auto-approval, and
  continues within the same invocation.

Task state is reduced to `todo → dispatched → in-review → done`, with
`changes-requested` returning to `dispatched`. Spec, Plan, Dispatch,
Review-order, and Verdict remain Gates, but Gates are checkpoints rather than
frontmatter states.

Deleting a task/project and bulk-updating more than three tasks remain protected
and always require confirmation. A verdict where reviewer equals executor is a
hard refusal in every mode. Gate mode changes only stop/continue behavior: each
skill must still perform all of its normal audit, metrics, state, and agent-stat
side effects exactly once.

## Consequences

- `supervised` preserves the existing multi-turn safety posture by default.
- `bypass` supports single-invocation Spec-to-Dispatch and verdict flows after a
  human explicitly selects it.
- `plan-only` prevents execution handoff and closure while still allowing plans
  and review coordination to be prepared.
- Skills must read the mode at every Gate rather than cache it.
- Historical task files, audit entries, research, and archived experiments keep
  their original wording; only active workflow documents use the new state
  machine.

## Status

Accepted
