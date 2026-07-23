---
name: lint
description: Health-check the entire control-tower backlog — detect broken, overdue, orphaned tasks, missing AC, dead file links, contradictions. Run periodically or when the backlog seems off. Activate when the user types /lint.
argument-hint: "[--project <name>] (default: all)"
allowed-tools: Read, Glob, Grep, mcp__code-review-graph__query_graph_tool, mcp__code-review-graph__semantic_search_nodes_tool
---

## Lint — backlog health-check (the 3rd loop, keeps the backlog from rotting)

Read and report only — **never edit/delete a task yourself** (this is RESTRICTED, see `AGENTS.md` §1).

### Process

1. Read `AGENTS.md` (core rules), `AGENTS-PLAYBOOK.md` (knowledge management) if not already read this session. Also read `index.md` §2 (PROJECT REGISTRY).
2. Determine scope: if `$ARGUMENTS` has `--project <name>`, only scan `projects/<name>/tasks/*.md` (+ `projects/<name>/docs/*.md`); otherwise scan all of `projects/*/tasks/*.md` + `knowledge/**/*.md` + `projects/*/docs/*.md`.
3. For each task file in scope, read the frontmatter, run the following checklist, and collect **Findings**:

   1. **Overdue task**: `deadline:` < today and `status:` != `done` → list it with days overdue.
   2. **Missing AC**: an open task (`status:` != `done`) whose `## Tiêu chí nghiệm thu (AC)` section is empty or missing → flag "ambiguous task, needs regenerating via `/pm`".
   3. **Dead file link**: for each path in `files:`, call `query_graph_tool(pattern="file_summary", target=<repo-relative path>, repo_root=<the project's repo_root>, detail_level="minimal")` (or `semantic_search_nodes_tool` if you need to cross-check by name) to verify the file/symbol still exists in the graph; if not found → flag "dead link, task may be stale — the path was likely renamed/deleted".
   4. **Orphan task**: a task file sitting in a project directory that doesn't appear in the PROJECT REGISTRY, or whose project has no valid `repo_root` (not an absolute path, or the directory doesn't exist).
   5. **Contradiction**: 2 tasks (same file or different files) share overlapping `files:` but their descriptions seem to conflict (heuristic: read the descriptions, no tool needed) → flag for the User to resolve manually.
   6. **State mismatch**: a task with `status: done` but no corresponding `Commit:` entry (other than `n/a`) found in `log.md` → flag "task closed but missing commit evidence".
   7. **Cleanup suggestion**: a task with `deadline:` more than 90 days in the past, still not `done`, with no recent log activity → suggest archiving (don't do it yourself).
   8. **Stuck in `dispatched`** (executor went silent): `status: dispatched` and `dispatched:` is more than 7 days ago, `result_ref:` still null → flag "executor hasn't reported back, consider pinging `executor:` or reassigning".
   9. **Stuck in `in-review`** (reviewer hasn't reviewed): `status: in-review` and `in_review:` is more than 3 days ago, no verdict yet in `log.md` → flag "reviewer hasn't returned a result, consider pinging `reviewer:`".
   10. **Orphan knowledge**: a file under `knowledge/` or `projects/*/docs/` with no inbound link (doesn't appear in another file's `related:`, no `[[wikilink]]` from any task) → flag "orphan knowledge, consider linking it or archiving".
   11. **Stale knowledge**: `updated:` more than 180 days ago and 0 inbound links (per item 10) → flag "stale knowledge, consider reviewing the content".
   12. **Pattern recurrence** (`AGENTS-EXPERIMENTAL.md` §13, once per `/lint` run, not per task): Glob `knowledge/patterns/*.md` (skip `_index.md`). For each pattern, read its `## Detection` heuristic and cross-reference it against the codebase in scope via `semantic_search_nodes_tool`/`query_graph_tool` (read-only — never write/refactor). If the pattern's signature appears to recur in a file/symbol NOT already listed in that pattern's `## Past Instances` and NOT covered by an existing open task → flag "pattern `<pattern_id>` may recur at `<file/symbol>`, consider a preventive task" (suggestion only — `/lint` never creates the task itself). If a tool errors out or the match is uncertain, write "could not verify" rather than guessing.
   13. **Calibration drift** (`AGENTS-EXPERIMENTAL.md` §16.4, once per run): read `knowledge/metrics/prediction-accuracy.md`'s log history. Among the last 5+ closed tasks that had a `confidence_interval:`, compute the actual-in-interval rate; if it's below 70% → flag "confidence calibration drifting (`<rate>`% in-interval on last `<N>`), consider widening intervals or reviewing the scoring formula". Skip this check (no finding, not an error) if fewer than 5 calibrated tasks exist yet.

4. Output the findings as a table in chat: columns Severity (🔴/🟡/🟢), Task/Knowledge (short description + file), Issue, Suggested action.
5. Write 1 `lint` entry to `log.md` following the format in `AGENTS-REFERENCE.md` §7 — summarizing the finding count by severity, no need to list everything in the log (the detail is already in chat).

### Notes
- If the backlog is clean (no findings), report briefly "Backlog is clean, no issues found" — still log it so there's a trace that `/lint` ran.
- Don't guess when checking for dead links — if the graph tool errors out or you're unsure, write "could not verify" rather than concluding on your own whether the file still exists.
