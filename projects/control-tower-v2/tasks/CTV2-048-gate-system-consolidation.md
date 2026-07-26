---
id: CTV2-048
title: "Implement Gate System Consolidation"
status: done
priority: critical
risk: high
deadline: 2026-08-02
executor: "@gpt-5.6-sol"
dispatched: 2026-07-26
result_ref: "92b7fbc"
in_review: 2026-07-26
reviewer: "@claude-opus"
reviewer_2: "@gemini-3.1-pro"
files:
  - backend/app/services/task_orchestration.py
  - backend/app/api/tasks.py
  - backend/app/api/dispatch.py
  - backend/app/services/command_router.py
  - backend/app/workers/agent_runner.py
  - backend/app/db/models.py
tests:
  - test_task_orchestration.py
  - test_gate_transitions.py
created: 2026-07-26
effort: 8h
updated: 2026-07-26
---

# CTV2-048: Implement Gate System Consolidation

## Context

Gap analysis CTV2-046 identified 6 critical regressions in V2's gate system:
- C1: 6 mutation paths with different validation
- C2: Supervised approval is fake (auto-clears)
- C3: Executor success writes `done` directly
- C4: Verdict has zero prerequisite checks
- C5: Four-eyes is nullable inequality
- C6: Tool errors silent (return empty)

## Objective

Create a single `TaskOrchestrationService` that ALL paths must call. Restore V1's governance model around V2's infrastructure.

## Deliverables

1. **TaskOrchestrationService** (`backend/app/services/task_orchestration.py`)
   - Single entry point for all state transitions
   - Compare-and-set with idempotency keys
   - Mode enforcement (supervised truly pauses, plan-only blocks dispatch)

2. **GateRecord as ledger** (`backend/app/db/models.py`)
   - Immutable records: `pending`, `approved`, `rejected`
   - Actor, timestamp, mode, input hash, output reference

3. **Fix C3**: Executor success → `awaiting-review`, NOT `done`

4. **Fix C4**: Verdict requires:
   - `status: in-review`
   - `reviewer` present
   - `executor ≠ reviewer`
   - `result_ref` present
   - AC evaluation results

5. **Fix C5**: Completion invariant
   ```
   status = done ⇒
     executor IS NOT NULL
     AND reviewer IS NOT NULL
     AND executor ≠ reviewer
     AND result_ref IS NOT NULL
     AND passing verdict record exists
   ```

6. **Remove direct mutation** from:
   - Generic PATCH `/api/tasks/{id}` (remove status/gate/executor/reviewer)
   - Chat commands (must call orchestration service)
   - Worker (must call orchestration service)

## AC

- [x] AC1: TaskOrchestrationService created with transition validation
- [x] AC2: All API routes call orchestration service (no direct status writes)
- [x] AC3: Supervised mode truly pauses (returns pending, waits for approval)
- [x] AC4: Executor success transitions to `awaiting-review`
- [x] AC5: Verdict requires all prerequisites (reviewer, result_ref, AC results)
- [x] AC6: Four-eyes enforced as completion invariant (DB constraint)
- [x] AC7: GateRecord becomes authoritative transition ledger
- [x] AC8: Tests cover all transition paths and rejection cases
