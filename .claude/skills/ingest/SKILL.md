---
name: ingest
description: Read every raw note in inbox.md, classify each one into the right project and enrich it via code-review-graph before creating a task or routing it as knowledge — reconcile into an existing similar task rather than creating a duplicate. Activate when the user types /ingest.
allowed-tools: Read, Edit, Write, Grep, Glob, mcp__code-review-graph__get_minimal_context_tool, mcp__code-review-graph__get_impact_radius_tool, mcp__code-review-graph__query_graph_tool, mcp__code-review-graph__semantic_search_nodes_tool
---

## Ingest — classify inbox.md into tasks or knowledge (reconcile, don't append)

### Process

1. Read `AGENTS.md` (core rules) and `AGENTS-PLAYBOOK.md` (especially §9 "Reconcile, don't append" and §11 "Knowledge management") and `index.md` §2 (PROJECT REGISTRY) if not already read this session.
2. Read the entirety of `inbox.md`. For each raw note:
   a. **Classify task vs. knowledge first** (`AGENTS-PLAYBOOK.md` §11.1): an actionable note, with work/a deadline attached → task (steps b-d below). A note that's domain knowledge/a decision/a convention, needing no immediate action → knowledge (step e).
   b. Determine the target project (keywords: OMS/order/invoice → `topvnsport-oms`; PMI/variant/product → `topvnsport-pmi`; unclear → ask the User instead of guessing).
   c. Look up that project's `repo_root` in the PROJECT REGISTRY. **Glob `projects/<name>/tasks/*.md`** — if a similar task already exists (same related file/symbol, or same business topic), read its frontmatter + body, **augment/rewrite it coherently** (add a sub-task, update `files:`/AC/`tests:` if the new note adds information, update `updated:`) — do NOT create a new duplicate task.
   d. If no similar task exists, follow the same graph process as `.claude/skills/pm/references/task-creation.md`: `get_minimal_context_tool` → `semantic_search_nodes_tool`/`get_impact_radius_tool` → `query_graph_tool(pattern="tests_for", target=...)`, always with `repo_root` and `detail_level="minimal"`, to confirm real paths instead of the guessed ones in the raw note. Read `<name>.md` (the file matching the project's folder name) to get `task_prefix`/`next_task_id`, create `projects/<name>/tasks/<ID>-<slug>.md` following `AGENTS.md` §2.1 syntax (with `files:`/AC/`tests:`, `status: todo`), increment `next_task_id`.
   e. **Route knowledge** (`AGENTS-PLAYBOOK.md` §11.5): create a file under `knowledge/<type>/` (scope=general, applies to multiple projects) or `projects/<name>/docs/` (scope=specific project) with the standard §11.3 frontmatter. Do NOT create a fake task for this non-actionable content.
3. Once a note has been reconciled/turned into a task/routed as knowledge → remove that item from `inbox.md`. Leave anything unresolved (e.g. missing info to determine the project, or ambiguous between task/knowledge) — don't delete it, ask the User.
4. Write 1 entry to `log.md` (`operation: ingest`, format in `AGENTS-REFERENCE.md` §7) — listing: how many notes were ingested, which were reconciled into an existing task vs. a new task vs. routed as knowledge.
5. Give the User a short report: how many notes were processed, which task/knowledge got augmented vs. newly created, how the graph-confirmed paths differ from the original note (if there's a notable discrepancy).

### Notes
- `/ingest` never marks a task `status: done` and never edits code itself — it only turns raw notes into structured tasks or knowledge files, following the same Spec Gate as `/pm` for tasks (stop and wait for approval, don't automatically move to the Plan Gate).
- **`source: auto-detected` notes** (`AGENTS-EXPERIMENTAL.md` §19.2, auto-remediation POC): a note tagged this way came from an alert/monitoring webhook rather than a human. Treat it exactly like any other note through steps a-e, with one addition — cross-reference it against `knowledge/patterns/*.md` (§13) for a likely root cause, and if it matches, draft a `tnr_spec:` block (`AGENTS-EXPERIMENTAL.md` §19.1) into the task before showing it at the Spec Gate. Still stops at the Spec Gate like every other task — auto-detected origin never skips human approval.
- Prefer reconciling over creating new: a backlog with many duplicate tasks on the same issue is harder to review than one task that keeps getting updated.
- Never invent domain/ADR content — knowledge is supplied/approved by the User, `/ingest` only routes it to the right place with the right frontmatter.
- If a note doesn't have enough information to determine the project, isn't clearly task or knowledge, or is too vague, leave it in `inbox.md` and ask the User instead of guessing.
