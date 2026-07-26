---
id: CTV2-043
task_path: projects/control-tower-v2/tasks/CTV2-043-agent-matching-chat-actions.md
project: control-tower-v2
result_ref: cd45531
executor: "@gpt-5.6-luna-high"
reviewer: "@gpt-5.6-sol"
status: changes-requested
issued: 2026-07-26
verdict: changes
verdict_date: 2026-07-26
---

# Phiếu Review: CTV2-043 — Agent-Task Matching + Chat Quick Actions

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-043-agent-matching-chat-actions.md`
- Result-ref: cd45531
- Executor: @gpt-5.6-luna-high
- Reviewer: @gpt-5.6-sol
- Ngày phát phiếu: 2026-07-26

## Acceptance Criteria cần verify

- [ ] AC1: `GET /api/tasks/{id}/suggested-agents` returns ranked list
- [ ] AC2: AgentMatcher considers skill match + past performance
- [ ] AC3: DispatchButton shows suggestions with scores
- [ ] AC4: Chat has Quick Actions bar with context-aware buttons
- [ ] AC5: Clicking action button triggers corresponding command

## Definition of Done

- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: test_agent_matcher.py
- [ ] Không regression
- [ ] Reviewer khác executor (bạn đang review, hãy xác nhận bạn ≠ @gpt-5.6-luna-high)

## Files to Review

- backend/app/services/agent_matcher.py
- backend/app/api/tasks.py
- backend/tests/test_agent_matcher.py
- frontend/src/components/chat/QuickActions.tsx
- frontend/src/components/task/DispatchButton.tsx

## Trả kết quả

`/verdict CTV2-043 <pass|changes> --reviewer @gpt-5.6-sol [--notes "..."]`

## Kết quả review

**Verdict: changes**

### Acceptance Criteria

- [x] AC1: `GET /api/tasks/{id}/suggested-agents` returns a score-ranked list.
- [x] AC2: `AgentMatcher` combines skill overlap and similar-run/configured success performance.
- [x] AC3: `DispatchButton` displays ranked suggestions with scores and reasons.
- [x] AC4: Chat renders status-dependent Quick Actions (`todo`, `dispatched`, `in-review`, and hidden for terminal/default states).
- [ ] AC5: Status, Cancel, and Verdict send their commands, but Dispatch does not create a runnable dispatch.

### Blocking findings

1. `backend/app/services/command_router.py:96-105` sends `run_agent` a generated run ID but never inserts an `AgentRun`. The worker explicitly discards unknown runs at `backend/app/workers/agent_runner.py:106-110`. A runtime probe confirmed `run_agent.send()` was called while `AgentRun` count remained zero and the task was incorrectly left `dispatched`. Route chat dispatch through the durable dispatch service, or create/commit the run before enqueueing it.
2. `frontend/src/components/task/DispatchButton.tsx:121-138` replaces the complete agent list with only the top suggestions whenever suggestions exist. This prevents the required user override to any non-top-N available agent. Keep ranked suggestions first, then include the remaining available agents.

### Additional finding

- Quick Actions receive a snapshot of `task` and have no completion callback/refetch path. After Dispatch, Cancel, or Verdict, the bar continues showing actions for the old status until an external refresh.

### Verification evidence

- `pytest -q tests/test_agent_matcher.py tests/test_command_router.py tests/unit/test_command_router.py` — **7 passed**.
- Frontend `tsc && vite build` in a clean Node 20 container — **passed**.
- Full backend suite — **159 passed, 3 failed**. The same three worker-process failures reproduce at parent `b4fadd4`, so they are not regressions from `cd45531`.
- Reviewer separation confirmed: `@gpt-5.6-sol` ≠ `@gpt-5.6-luna-high`.

### Report command

`/verdict CTV2-043 changes --reviewer @gpt-5.6-sol --notes "Chat /dispatch queues no AgentRun, so the worker discards it; DispatchButton also prevents override outside top suggestions."`
