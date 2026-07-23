---
name: pm
description: Hand off a new task or break down an ambiguous request into a task with verifiable Acceptance Criteria, using code-review-graph (read-only) to find blast radius/tests/risk, compute pre-execution prediction score (predicted_success), walk it through Spec Gate + Plan Gate + Dispatch Gate according to state/mode.md, then dispatch it to an executor outside the system. Never writes code itself, never self-verifies — review happens entirely outside control-tower (see /review-order, /verdict). Activate when the user types /pm or talks about handing off/managing/planning a task for a specific project.
argument-hint: <task description> [--project <project name>]
allowed-tools: Read, Edit, Write, Grep, Glob, Bash, mcp__code-review-graph__get_minimal_context_tool, mcp__code-review-graph__get_impact_radius_tool, mcp__code-review-graph__query_graph_tool, mcp__code-review-graph__semantic_search_nodes_tool, mcp__code-review-graph__get_knowledge_gaps_tool, mcp__code-review-graph__get_hub_nodes_tool, mcp__code-review-graph__get_bridge_nodes_tool, mcp__code-review-graph__get_affected_flows_tool, mcp__code-review-graph__get_architecture_overview_tool, mcp__code-review-graph__cross_repo_search_tool
---

## Project Manager — PLAN + COORDINATE, never EXECUTE

The user invokes: `/pm $ARGUMENTS`. You're running inside the `control-tower` repo, NOT the target repo — every graph tool call must include an absolute `repo_root`. **Model B: `/pm` only plans and coordinates. It NEVER writes code itself, never spawns an executing subagent, never runs tests, never closes a task.** EXECUTE and REVIEW both happen outside the system (see `AGENTS.md` §1, §4).

### Coordinator output style

Keep responses to 1–2 terse sentences with no long explanation. In
`supervised`, ask one terse confirmation when the current Gate is reached; do
not pre-approve or batch a later Gate whose actions have not run yet. After
spawning a CLI process, report only pass/fail and the next action, without
summarizing its output.

### Gate check (run at every Gate)

Read `state/mode.md` fresh at Spec, Plan, and Dispatch; a missing/invalid file
means `supervised`.

- `plan-only`: prompt at Spec and Plan; block Dispatch.
- `supervised`: stop and request explicit confirmation.
- `bypass`: add `auto-approved: <gate>` to that stage's audit entry and continue
  immediately in the same invocation.

The Gate changes only stop/continue behavior. Perform every stage's task,
prediction, audit, executor-selection, and dispatch side effect exactly once.
The Dispatch stage is executed through `/dispatch`, which owns the Dispatch Gate
check; `/pm` must not prompt for that same Gate a second time.

### Step 0 — Locate the project

1. Read `AGENTS.md` (roles, DoD, gates, task syntax) and `AGENTS-REFERENCE.md` §6 (graph rules) and `index.md` §2 (PROJECT REGISTRY) if not already read this session.
2. Determine the target project:
   - If `$ARGUMENTS` includes `--project <name>`, use that exact name to look up the registry.
   - Otherwise, infer it from the description (e.g. "variant"/"PMI" → `topvnsport-pmi`; "order"/"OMS" → `topvnsport-oms`). If unsure, ask the User.
   - Get the absolute `repo_root` + `Task dir` (`projects/<name>/tasks/`) from the registry. Read `projects/<name>/<name>.md` (the file matching the folder name) to get `task_prefix` + `next_task_id`. If the project isn't in the registry yet, stop and tell the User it needs onboarding first (`AGENTS.md` §10).

### Step 1 — Determine the current stage and continue as mode permits

- **New request / no matching task file yet in `projects/<name>/tasks/*.md`**
  (Glob to check) → follow `references/task-creation.md`. It creates the `todo`
  task and checks the Spec Gate.
- **Existing `todo` task with Spec approved** → follow
  `references/task-execution.md`. It writes the Plan, checks the Plan Gate, then
  enters the `/dispatch` stage.
- **In `bypass` mode**, do not return after creating the task or writing the
  Plan. Continue through creation → planning → best-fit executor selection →
  `/dispatch` in this invocation. If the User did not specify an executor,
  select the highest-ranked compatible executor from `knowledge/agents/*.md`
  and record that choice in the dispatch audit entry.
- **In `supervised` mode**, resume from the stage immediately after the Gate the
  User explicitly confirmed. Silence or ambiguity is not approval.
- **In `plan-only` mode**, planning can complete but `/dispatch` blocks.

Once a task is `status: dispatched`, `/pm` is done. Executor completion resumes
through `/review-order`, not through `/pm`.

### Common mistakes to avoid

- Forgetting `repo_root` → the graph tool auto-detects based on `control-tower`'s cwd and returns wrong/empty results.
- Calling `query_graph_tool` with an `edge` parameter — the real tool only has `pattern`/`target`, no `edge`.
- Using the default `top_n` (10) for `get_hub_nodes_tool`/`get_bridge_nodes_tool` — far too small for a large repo, so `⚠️high-risk` almost never triggers. Always pass `top_n=50`.
- Writing an absolute path into `files:` instead of a path relative to `repo_root`.
- Caching coordination mode across Gates instead of rereading `state/mode.md`.
- Treating a `bypass` auto-approval as permission to omit logging or other stage side effects.
- **Writing code yourself, running tests yourself, or closing a task yourself (`- [x]`).** This is no longer `/pm`'s job under Model B — no matter how simple a task looks, writing code always happens outside the system and closing a task always goes through `/verdict`.
