# Task Creation — Spec Gate

Applies when the User hands off a new request via `/pm`. Goal: create a dedicated task file, complete with `files:`/AC/`tests:`/`flows:` (frontmatter syntax in `AGENTS.md` §2.1), **never write the task before the graph has been queried**.

## Steps (per the table in `AGENTS-REFERENCE.md` §6.1)

Every tool below must be called with `repo_root=<absolute, looked up from index.md §2>`; use `detail_level="minimal"` wherever the tool supports it.

1. `get_minimal_context_tool(task="<task description>", repo_root=...)` — get oriented first, avoid blind searching.
2. `semantic_search_nodes_tool(query="<keywords from the task description>", repo_root=..., detail_level="minimal")` — find the real file/symbol. If the result shows the feature **already exists** (passing test, schema constraint already in place...), STOP, tell the User the request may already be implemented — don't create a fake task for something already done (real-world example: `PMI-001` — "add cost/tax validation for variant" was once discovered to already exist in topvnsport).
3. **Pattern match**: Glob `knowledge/patterns/*.md` (skip `_index.md`), read each file's `## Problem Signature`. If the task description's symptoms match a pattern (e.g. "list page getting slower with more rows" ↔ `n-plus-one-query`'s signature), surface it to the User before writing the task: "This looks like pattern `<pattern_id>`, see how `<task from Past Instances>` was fixed" — a suggestion only, never auto-applied, never blocks the gate. If `Past Instances` is empty, still mention the matching pattern's `Solution Template` as a hint.
4. `get_impact_radius_tool(changed_files=[...paths found in step 2...], repo_root=..., detail_level="minimal")` → fills in `files:`.
   - If the blast radius has more than **8** files, do NOT write one big task — propose splitting into smaller tasks (1 PR each), present the split plan to the User before writing any task.
5. `query_graph_tool(pattern="tests_for", target=<file/symbol from step 3>, repo_root=..., detail_level="minimal")` → fills in `tests:` (existing tests).
   - **The correct params are `pattern`/`target`, there is NO `edge` param.** Calling it wrong fails immediately.
6. `get_knowledge_gaps_tool(repo_root=...)` — if the impacted area touches an uncovered hotspot, add a sub-task:
   `- [ ] Write a test for <symbol/file> (currently no coverage — knowledge gap) — suggested test file: <suggested test file>`
7. `get_hub_nodes_tool(top_n=50, repo_root=...)` and `get_bridge_nodes_tool(top_n=50, repo_root=...)` — if any node in `files:` matches the returned list → flag `risk: high` in the frontmatter.
8. `get_affected_flows_tool(changed_files=[...], repo_root=...)` → fills in `flows:`.
9. **Compute Pre-Execution Prediction Score (`predicted_success`)**:
    - Start with `Score = 1.0`.
    - `blast_radius > 8`: Score -= 0.3
    - `blast_radius > 15`: Score -= 0.2 (cumulative -0.5)
    - `hits hub/bridge node`: Score -= 0.2
    - `similar tasks in log.md (same files/flows) had < 50% success`: Score -= 0.3
    - `no existing tests (tests: [])`: Score -= 0.1
    - Classification:
      - `high`: Score >= 0.7
      - `medium`: 0.4 <= Score < 0.7
      - `low`: Score < 0.4
    - Record `predicted_success: <high|medium|low>` and `prediction_factors:` (with `score:` and list of `deductions:`) in the frontmatter.
    - **If `predicted_success: low`**, proactively generate auto-suggestions:
      - Blast radius large (>8 files) → suggest splitting task into smaller sub-tasks (1 PR each).
      - Hub/bridge node hit → suggest adding extra test coverage for the hub component.
      - Past task failure → reference the failed task from `log.md` and suggest addressing its root cause.
      - Missing tests → add a test creation sub-task.
10. **Confidence Calibration**: compute `confidence_interval: [lower, upper]` from the score in step 9, whether step 11's verifier passed clean, and historical accuracy on similar tasks in `knowledge/metrics/prediction-accuracy.md`. Record it in the frontmatter next to `predicted_success`. Apply the dynamic gate rule to decide how much scrutiny to ask for at the Spec Gate stop below — this changes gate FRICTION, never whether the gate happens.
11. **LLM-Modulo verifier**: evaluate every rule in `.claude/verifier-rules.yaml` against the draft task, print the results block. Any `❌` needs a mechanical auto-fix or an explicit User override (recorded in `## Verifier Overrides`) before the Spec Gate can close below.

## Writing the task

- Convert every absolute path returned by the graph into a **repo-relative** path (strip the `repo_root` prefix). Never write a guessed path — if the graph can't confirm it, write `*(path not confirmed via graph)*` instead of making one up.
- Read `<name>.md` (the file matching the project's folder name) → get `task_prefix` + `next_task_id`. ID = `<task_prefix>-<NNN>` (NNN = `next_task_id`, zero-padded to 3 digits). Slug = kebab-case of the title (max 40 ASCII characters).
- Create the file `projects/<name>/tasks/<ID>-<slug>.md` with standard frontmatter (`AGENTS.md` §2.1 including `predicted_success` & `prediction_factors`) + body, `status: todo`. The body MUST have the backlink line `> Dự án: [[projects/<name>/<name>]]` right below the H1 title (navigation convention linking task → project file). Do NOT fill in `executor:`/`reviewer:`/`result_ref:` — those fields only get filled in later (Plan Gate/dispatch, review-order, verdict).
- Increment `next_task_id` in `<name>.md` by 1 once the file is created.
- Add 1 line to the `## Tasks` section of `<name>.md`: `- [[<ID>-<slug>]] — <title> (todo)`. If `<name>.md` doesn't have a `## Tasks` section yet, create one (placed before the "Quy tắc phê duyệt riêng" section). This doesn't need to be perfect — `/report` regenerates this whole section on every run, so small mistakes self-heal.
- If the task touches `schemas/`, `models.py`, or a migration directory → automatic RESTRICTED (`AGENTS.md` §1 & §4), flag `risk: high` and call it out explicitly in the task.
- Leave the `## Plan` section of the body empty — it gets filled in at the Plan Gate (see `task-execution.md`), don't pre-fill it.

## Closing the Spec Gate

1. Write 1 entry to `log.md` (`operation: pm-create`, format in `AGENTS-REFERENCE.md` §7).
2. Show the User the task you just wrote, stop and wait for approval of the scope & AC. **Do not** automatically move on to the Plan Gate — you need explicit User confirmation.
