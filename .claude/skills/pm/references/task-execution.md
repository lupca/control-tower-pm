# Task Execution — Plan Gate → Dispatch

Applies after the User has approved the Spec Gate (the task's scope + AC have been confirmed, `status: todo`).

## Plan Gate

1. Dig deeper into the target codebase if needed (read the actual source of the files in `files:`, not just relying on the graph) to write a concrete implementation plan — not a vague one.
2. Write the plan DIRECTLY into the `## Plan` section of the task file at `projects/<name>/tasks/<ID>-<slug>.md`: list the order of files/functions/migrations to change (if any), matching the sub-tasks already listed at the Spec Gate.
3. If, while planning, you find you need to touch a file **outside** the already-approved `files:` → go back to the Spec Gate, don't expand the scope unilaterally.
4. Write 1 entry to `log.md` (`operation: plan`), update `updated:` in the frontmatter.
5. Stop, show `## Plan` to the User, wait for approval. Apply the same confidence-based friction rule as the Spec Gate (`AGENTS.md` §16.2, using the task's recorded `confidence_interval:`): narrow-and-high still stops here but accepts a quick "ok"; wide-or-low asks the User to confirm specific uncertain points, not just approve in general. The gate itself never disappears — only how much scrutiny is requested.

## After the Plan Gate is approved: move to `ready` then `dispatched`

**This is where control-tower stops — do NOT write code yourself, do NOT run tests yourself, do NOT spawn an executing subagent.** Writing code is an action that happens outside the system (`AGENTS.md` §1, §4).

1. Update `status: ready` in the task's frontmatter.
2. **Suggest Best-Fit Executor(s)** (Reputation System `AGENTS.md` §12):
   - Scan task `files:` to identify required domain strengths (`backend`, `frontend`, `database`, `testing`, `infra`).
   - Read profiles in `knowledge/agents/*.md`.
   - Rank candidate executors by matching `strengths` + highest `success_rate`.
   - Show recommendations to the User (e.g., "Recommended executor: @antigravity (strengths: backend, testing; success rate: 100%)").
   - **Warning**: If User selects an agent with low success rate (< 0.6) in that domain or matching `weaknesses: [...]`, display a warning flag.
3. Ask the User: who will be the `executor:` for this task (a human or another AI, in the target code repo)?
4. Record `executor: "@name"`, `status: dispatched`, `dispatched: <today's date>`, `updated: <today's date>` in the frontmatter.
5. Write 1 entry to `log.md` (`operation: dispatch`) — summarizing: which task, handed to whom, noting the task file is already a self-contained work order with AC/`files:`/`tests:`/`## Plan`/DoD, no extra tooling needed.
6. Tell the User: the task is ready to hand to the executor — they only need the path to `projects/<name>/tasks/<ID>-<slug>.md` (no need for control-tower access or any other tooling).
7. **Stop completely.** Once the executor reports done (with `result_ref:`), the User (or the executor themselves) will run `/review-order` — that's the next step, not part of `/pm`.

## If the task is flagged `⚠️high-risk` or touches `schemas/`/`models.py`/migrations

RESTRICTED (`AGENTS.md` §1 & §4): the Plan Gate requires explicit written/chat confirmation from the User before moving to `dispatched` — never assume approval silently.
