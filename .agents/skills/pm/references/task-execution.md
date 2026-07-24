# Task Execution — Plan Gate → Dispatch

Applies after the User has approved the Spec Gate (the task's scope + AC have been confirmed, `status: todo`).

## Plan Gate

1. Dig deeper into the target codebase if needed (read the actual source of the files in `files:`, not just relying on the graph) to write a concrete implementation plan — not a vague one.
2. Write the plan DIRECTLY into the `## Plan` section of the task file at `projects/<name>/tasks/<ID>-<slug>.md`: list the order of files/functions/migrations to change (if any), matching the sub-tasks already listed at the Spec Gate.
3. If, while planning, you find you need to touch a file **outside** the already-approved `files:` → go back to the Spec Gate, don't expand the scope unilaterally.
4. Read `state/mode.md` fresh; a missing/invalid value means `supervised`.
5. Write 1 entry to `log.md` (`operation: plan`), update `updated:` in the
   frontmatter. In `bypass`, include `auto-approved: plan`.
6. Apply the Plan Gate:
   - `supervised` or `plan-only`: stop, show `## Plan`, and wait for approval.
     Apply the confidence-based friction rule using `confidence_interval:`:
     narrow-and-high accepts a quick "ok"; wide-or-low asks the User to confirm
     the uncertain points.
   - `bypass`: continue immediately to executor selection and Dispatch in this
     invocation.

## After the Plan Gate is approved: dispatch

**This is where control-tower stops — do NOT write code yourself, do NOT run tests yourself, do NOT spawn an executing subagent.** Writing code is an action that happens outside the system (`AGENTS.md` §1, §4).

1. **Suggest Best-Fit Executor(s)** (Reputation System):
   - Scan task `files:` to identify required domain strengths (`backend`, `frontend`, `database`, `testing`, `infra`).
   - Read profiles in `knowledge/agents/*.md`.
   - Rank candidate executors by matching `strengths` + highest `success_rate`.
   - Show recommendations to the User (e.g., "Recommended executor: @antigravity (strengths: backend, testing; success rate: 100%)").
   - **Warning**: If User selects an agent with low success rate (< 0.6) in that domain or matching `weaknesses: [...]`, display a warning flag.
2. Choose the executor:
   - `supervised`: ask the User to select/confirm an executor.
   - `bypass`: use an executor supplied in the request; otherwise select the
     highest-ranked compatible executor and record that automatic selection.
   - `plan-only`: proceed to `/dispatch`, which will block without mutating task
     state or spawning a process.
3. **Run the executor handoff using `/dispatch`:**
   ```
   /dispatch <task-id> @<executor>
   ```
   `/dispatch` reads mode again, owns the Dispatch Gate, then records
   `executor:`/`status: dispatched`/dates, writes its audit entry, and spawns a
   separate CLI process via Bash (NOT `Agent()`). `/pm` must not duplicate these
   mutations or the gate prompt.
4. **Stop completely after dispatch.** Once the executor reports done (with
   `result_ref:`), the User (or executor) runs `/review-order`.

## If the task is flagged `⚠️high-risk` or touches `schemas/`/`models.py`/migrations

In `supervised` or `plan-only`, the Plan Gate requires explicit written/chat
confirmation. An explicitly selected `bypass` mode may auto-approve the Gate,
but it must log that fact and does not weaken protected actions or four-eyes.
