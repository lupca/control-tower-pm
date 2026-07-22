# AGENTS-REFERENCE.md

Detail reference for handoff artifacts, code-review-graph usage, and audit logging. Load when running `/pm`, `/review-order`, or debugging graph queries.

---

## 5. HANDOFF ARTIFACTS

- **OUT (handing off work)**: the task file is a self-contained work order (AC + `files:` + `tests:` + `## Plan` + DoD). The executor only needs the task's path; they don't need to share control-tower's tooling/system.
- **IN (work returned)**: the executor reports "done" with a **result-ref** (branch/commit/PR) → recorded in `result_ref:`, task moves to `status: in-review`.
- The executor can be: a separate Claude session in the code repo (recommended), another AI (Antigravity/Cursor…), or a human. Control-tower **assumes nothing** about the executor.
- **REVIEW-OUT**: `/review-order` generates a review sheet (`projects/<name>/reviews/<ID>-review.md`) → hands it to an independent reviewer (≠ executor). control-tower never creates/deletes a sheet outside the `/review-order` flow — don't hand-edit files in this directory except to correct information.
- **VERDICT-IN**: the reviewer reports the outcome → `/verdict` records it in the system. The reviewer can also be a human or another AI; control-tower assumes nothing about the reviewer.

---

## 6. USING `code-review-graph` (read-only, only during PLAN/COORDINATE)

The toolset has ~30 MCP tools. **Every call MUST include `repo_root=<absolute path>` looked up from the PROJECT REGISTRY (`index.md` §2)** — the session's cwd is `control-tower`, so auto-detect will be wrong. Always start with `get_minimal_context_tool`; use `detail_level="minimal"` wherever a tool supports it. **This entire section is static analysis — none of these tools reads the executor's actual diff or runs tests; that's the reviewer's job, outside the system.**

### 6.1. Table: which tool `/pm` calls at which step (Spec Gate + Plan Gate)

| Step | Tool (real name & args) | Result recorded in the task |
|---|---|---|
| 0. Startup | `get_minimal_context_tool(task=..., repo_root=...)` | orientation, saves tokens |
| 1. Locate | `semantic_search_nodes_tool(query=..., repo_root=..., detail_level="minimal")` | find the right symbol/file (real path, not a guess) |
| 2. Blast radius | `get_impact_radius_tool(changed_files=[...], repo_root=..., detail_level="minimal")` | fills in `files:` (file/caller/dependent) |
| 3. Existing tests | `query_graph_tool(pattern="tests_for", target=<file/symbol>, repo_root=..., detail_level="minimal")` | fills in `tests:` with existing tests |
| 4. Test gaps | `get_knowledge_gaps_tool(repo_root=...)` | auto-generates a test sub-task (§6.2) |
| 5. Risk ranking | `get_hub_nodes_tool(top_n=50, repo_root=...)`, `get_bridge_nodes_tool(top_n=50, repo_root=...)` | flags `risk: high` on a match (§6.3) |
| 6. Business impact | `get_affected_flows_tool(changed_files=[...], repo_root=...)` | fills in `flows:` |

> **Note:** `query_graph_tool` does NOT take an `edge` parameter — the correct params are `pattern` (value `"tests_for"` to find tests) and `target` (the node/file name to query). Calling it with the wrong param fails immediately.
>
> **There is no step 7 "Verify via `detect_changes_tool`"** as in the old Model A draft — verification is now the independent reviewer's job (§4, §5). `/pm` stops at step 6 and never self-verifies.

### 6.2. Auto-generating a test sub-task from `get_knowledge_gaps_tool`

If the impacted area contains a hotspot **not covered by tests** (per `get_knowledge_gaps_tool`), automatically add a sub-task:
`- [ ] Write a test for <symbol/file> (currently no coverage — knowledge gap) — suggested test file: <suggested test file>`

### 6.3. Risk flags from hub/bridge nodes

`get_hub_nodes_tool`/`get_bridge_nodes_tool` return the **repo-wide global top**, not scoped to the task — so you must call them with a large enough `top_n` (use **50**, not the tool's default of 10). If any file/symbol in `files:` matches the returned list → flag `risk: high` and apply the RESTRICTED escalation (§4).

### 6.4. Read-only tools used by `/review-order` (enriching the review sheet, NOT verification)

- `get_suggested_questions_tool(repo_root=...)` — generates priority review questions (bridge node missing tests, uncovered hub node, unexpected coupling...), used as-is, no `changed_files` needed.
- `get_affected_flows_tool(changed_files=<the files: recorded in the task at Spec Gate>, repo_root=...)` — REUSES the file list already locked in at Spec Gate, does NOT read the executor's new git diff (this boundary keeps control-tower from encroaching on the reviewer's job).

### 6.5. Checking graph "freshness"

`list_graph_stats_tool` (MCP) does **not** return commit-matching info — only `total_nodes`, `total_edges`, `embeddings_count`, `last_updated`. To check whether the graph matches the current commit, run the CLI via Bash:
```bash
/home/lupca/.local/share/code-review-graph-venv/bin/python3 -m code_review_graph status --repo <repo_root> --json
```
and compare `built_at_commit` against `current_sha`.

### 6.6. `crg-daemon` — background graph auto-update

The `crg-daemon` binary is NOT on the default PATH — call it through the Python module:
```bash
/home/lupca/.local/share/code-review-graph-venv/bin/python3 -m code_review_graph daemon add <repo_root> --alias <name>
/home/lupca/.local/share/code-review-graph-venv/bin/python3 -m code_review_graph daemon start
/home/lupca/.local/share/code-review-graph-venv/bin/python3 -m code_review_graph daemon status
```
The daemon polls every 2s, auto-updating the graph whenever the code changes (including when the executor pushes a new commit) → `/pm`/`/review-order` always query a fresh graph. Cap token usage via env vars when needed: `CRG_MAX_IMPACT_DEPTH`, `CRG_MAX_IMPACT_NODES`, `CRG_TOOL_TIMEOUT`.

---

## 7. AUDIT STANDARD (log.md - Audit Trail)

Append-only format, with a consistent prefix so `grep`/`awk` can parse it:

```markdown
## [YYYY-MM-DD HH:MM:SS] <operation> | <title>
- Dự án: <project file>
- Mô tả: <summary of what was just done>
- Giải trình: <why was it done this way? what did the AI find via the graph?>
- Files touched: <path1, path2>
- Trạng thái: [Thành công | Chờ duyệt | Đã hủy]
- Commit: <hash | n/a>
```
`<operation>` ∈ `{ingest, pm-create, plan, dispatch, review-order, verdict, report, lint}`. Write one entry for every COLLABORATIVE or RESTRICTED action.
