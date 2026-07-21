# Task Creation — Spec Gate

Applies when the User hands off a new request via `/pm`. Goal: create a dedicated task file, complete with `files:`/AC/`tests:`/`flows:` (frontmatter syntax in `AGENTS.md` §2.1), **never write the task before the graph has been queried**.

## Steps (per the table in `AGENTS.md` §6.1)

Every tool below must be called with `repo_root=<absolute, looked up from index.md §2>`; use `detail_level="minimal"` wherever the tool supports it.

1. `get_minimal_context_tool(task="<task description>", repo_root=...)` — get oriented first, avoid blind searching.
2. `semantic_search_nodes_tool(query="<keywords from the task description>", repo_root=..., detail_level="minimal")` — find the real file/symbol. If the result shows the feature **already exists** (passing test, schema constraint already in place...), STOP, tell the User the request may already be implemented — don't create a fake task for something already done (real-world example: `PMI-001` — "add cost/tax validation for variant" was once discovered to already exist in topvnsport).
3. `get_impact_radius_tool(changed_files=[...paths found in step 2...], repo_root=..., detail_level="minimal")` → fills in `files:`.
   - If the blast radius has more than **8** files, do NOT write one big task — propose splitting into smaller tasks (1 PR each), present the split plan to the User before writing any task.
4. `query_graph_tool(pattern="tests_for", target=<file/symbol from step 3>, repo_root=..., detail_level="minimal")` → fills in `tests:` (existing tests).
   - **The correct params are `pattern`/`target`, there is NO `edge` param.** Calling it wrong fails immediately.
5. `get_knowledge_gaps_tool(repo_root=...)` — if the impacted area touches an uncovered hotspot, add a sub-task:
   `- [ ] Write a test for <symbol/file> (currently no coverage — knowledge gap) — suggested test file: <suggested test file>`
6. `get_hub_nodes_tool(top_n=50, repo_root=...)` and `get_bridge_nodes_tool(top_n=50, repo_root=...)` — if any node in `files:` matches the returned list → flag `risk: high` in the frontmatter.
7. `get_affected_flows_tool(changed_files=[...], repo_root=...)` → fills in `flows:`.

## Writing the task

- Convert every absolute path returned by the graph into a **repo-relative** path (strip the `repo_root` prefix). Never write a guessed path — if the graph can't confirm it, write `*(path not confirmed via graph)*` instead of making one up.
- Read `<name>.md` (the file matching the project's folder name) → get `task_prefix` + `next_task_id`. ID = `<task_prefix>-<NNN>` (NNN = `next_task_id`, zero-padded to 3 digits). Slug = kebab-case of the title (max 40 ASCII characters).
- Create the file `projects/<name>/tasks/<ID>-<slug>.md` with the standard frontmatter + body (`AGENTS.md` §2.1), `status: todo`. The body MUST have the backlink line `> Dự án: [[projects/<name>/<name>]]` right below the H1 title (a real wikilink, not path text — so Obsidian's Graph can draw the edge; no alias needed since the filename already matches `<name>`). Do NOT fill in `executor:`/`reviewer:`/`result_ref:` — those fields only get filled in later (Plan Gate/dispatch, review-order, verdict).
- Increment `next_task_id` in `<name>.md` by 1 once the file is created.
- Add 1 line to the `## Tasks` section of `<name>.md`: `- [[<ID>-<slug>]] — <title> (todo)`. If `<name>.md` doesn't have a `## Tasks` section yet, create one (placed before the "Quy tắc phê duyệt riêng" section). This doesn't need to be perfect — `/report` regenerates this whole section on every run, so small mistakes self-heal.
- If the task touches `schemas/`, `models.py`, or a migration directory → automatic RESTRICTED (`AGENTS.md` §1 & §4), flag `risk: high` and call it out explicitly in the task.
- Leave the `## Plan` section of the body empty — it gets filled in at the Plan Gate (see `task-execution.md`), don't pre-fill it.

## Closing the Spec Gate

1. Write 1 entry to `log.md` (`operation: pm-create`, format in `AGENTS.md` §7).
2. Show the User the task you just wrote, stop and wait for approval of the scope & AC. **Do not** automatically move on to the Plan Gate — you need explicit User confirmation.
