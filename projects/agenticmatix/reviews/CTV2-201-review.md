---
task_id: CTV2-201
result_ref: "9ea9243..58d1163"
reviewer: @gemini-3.1-pro-high
executor: "@claude-sonnet-high"
created: 2026-07-29
---

# Review Sheet: CTV2-201 — Add TaskRound table for multi-round history

## Result Reference
- Base: `9ea9243`
- Head: `58d1163`
- Diff: `git diff 9ea9243..58d1163`

## Acceptance Criteria Checklist

- [ ] Create TaskRound model with fields: id, task_id, round_no, status, base_sha, plan_ref, executor_agent_id, executor_run_id, reviewer_agent_id, reviewer_run_id, result_ref, verdict, findings_ref, started_at, completed_at
- [ ] Add Task.current_round_id FK and Task.final_result_ref, Task.final_verdict projection fields
- [ ] Migrate TaskOrchestrationService.request_dispatch to create TaskRound on dispatch
- [ ] Migrate TaskOrchestrationService verdict recording to update TaskRound
- [ ] Update advance_task to use TaskRound.round_no for round counting instead of audit log queries
- [ ] Add alembic migration with data migration for existing tasks (create TaskRound records for tasks with existing executor/result_ref)
- [ ] Tests: test_task_orchestration.py updated to verify TaskRound creation/update on dispatch and verdict

## Verification Commands

```bash
cd /home/lupca/projects/control-tower-v2
pytest backend/tests/test_task_orchestration.py -v
alembic upgrade head
alembic downgrade -1 && alembic upgrade head
```

## Review Instructions

1. Read the diff: `git diff 9ea9243..58d1163`
2. Verify each AC item against the code changes
3. Run verification commands
4. Check for regressions in existing tests
5. Report verdict: PASS or CHANGES with findings
