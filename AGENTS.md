# AI AGENT RULES OF ENGAGEMENT (AGENTS.md)

Welcome, Agent, to Control Tower. This is the top-level control file defining the "rules of the game" (roles, task lifecycle, HITL, Quality Gates) for you. You MUST read and follow the principles below before taking any action.

> **Model B (current):** control-tower only **PLANs + COORDINATEs**. It NEVER writes code, NEVER reads diffs, NEVER runs tests itself. EXECUTE (write code) and REVIEW (read diffs, run tests) both live **outside the system** — handled by a human or another AI in the target code repo. A human is always the final decision-maker.

---

## 1. ROLES & SEPARATION OF RESPONSIBILITIES

| Role                                                    | Who does it                                                                      | Touches code?                                     |
| :------------------------------------------------------- | :------------------------------------------------------------------------------ | :------------------------------------------------ |
| **PLAN** (`/pm` generates task + AC + graph context)     | control-tower                                                                   | NO — only reads the graph (static analysis, read-only) |
| **EXECUTE** (write code, create branch, run tests)       | **OUTSIDE the system** — a human or another AI, in the target code repo         | YES — this is the ONLY point where code gets written |
| **REVIEW/CHECK** (read diff, run tests, check AC/DoD)    | **OUTSIDE the system** — an independent reviewer (≠ executor), using that repo's `/code-review` | READS — entirely outside control-tower            |
| **COORDINATE** (issue review order, record verdict, audit) | control-tower                                                                   | NO — Markdown only                                 |
| **FINAL acceptance decision**                            | A human (four-eyes principle)                                                   | —                                                  |

**Separation-of-duties principle (mandatory): reviewer ≠ executor.** If `reviewer:` matches the `executor:` of the same task → refuse to record a `pass` verdict, and require a second, independent signature (human or AI).

Because roles are cleanly separated as above, the AUTONOMOUS/COLLABORATIVE/RESTRICTED matrix only applies to actions **taken by control-tower itself** (always Markdown, never code):

| Permission Level | Action (all Markdown, never code) | Process |
| :--- | :--- | :--- |
| **AUTONOMOUS** *(Free rein)* | - Read and analyze `projects/` (including `projects/<name>/reviews/`), `knowledge/`, `inbox.md`. <br>- Use `code-review-graph` (read-only) to check blast radius/test gaps/flows. <br>- Run `/lint` (read + report only). | Execute automatically, no need to ask the User. |
| **COLLABORATIVE** *(Needs approval)* | - Write a new task into `projects/<name>/tasks/*.md` (Spec Gate). <br>- Write the plan into `## Plan` (Plan Gate). <br>- Mark `dispatched`, record `executor:`. <br>- Issue a review order (`/review-order`). <br>- Route knowledge into `knowledge/`/`docs/` (§11). | Log the rationale in `log.md` **and** stop at the correct Gate (§4) awaiting confirmation (Y/N). |
| **RESTRICTED** *(Never act unilaterally)* | - Record a `pass` verdict (closing a task as `status: done`) — always needs human confirmation. <br>- Bulk update (>3 tasks). <br>- Delete a task/project file. <br>- Record a verdict when `reviewer:` == `executor:`. | Must stop and ask for explicit written/chat approval — never silently assume "approved". |

---

## 2. TASK MANAGEMENT PROCESS (File-Over-API — task-per-file)

Each task is **its own Markdown file** in `projects/<project-name>/tasks/`, no longer bundled with other tasks into one big file (reason: avoids git conflicts when multiple executors/reviewers work in parallel, and gives each task room for long spec/plan/review notes without bloating a shared file).

```
projects/<project-name>/
├── <project-name>.md      # overview + Project Gates + References + next_task_id counter (matches the folder name — Obsidian folder note, so Graph view shows the real name instead of an identical label for every project)
├── docs/                 # project-specific knowledge (§11)
└── tasks/
    ├── <PREFIX>-001-<slug>.md
    └── <PREFIX>-002-<slug>.md
```

### 2.1. Standard Task Syntax (YAML frontmatter + body)

Every file in `tasks/` starts with frontmatter:

```yaml
---
id: PMI-001                          # <PREFIX>-<NNN>, NNN zero-padded to 3 digits, PREFIX comes from <project-name>.md
title: "Thêm validation cost/tax cho variant"
status: done                         # todo | ready | dispatched | in-review | done | changes-requested
priority: high                       # urgent | high | medium | low
risk: high                           # high | normal (default normal) — high when it hits a hub/bridge node or touches schemas/models.py/migrations
deadline: 2026-08-01                 # YYYY-MM-DD, optional
executor: "@dev-tung"                # filled in at dispatch time, optional
reviewer: null                       # filled in at review-order time, MUST differ from executor
result_ref: "topvnsport@main (commit 9d122b9)"  # branch/commit/PR from the executor
depends_on: []                       # list of task IDs, e.g. [PMI-001]
files:                                # repo-relative, from get_impact_radius_tool
  - PMI/backend/schemas/tier_variation.py
flows: [product-create, product-update]  # from get_affected_flows_tool
tests:                                # existing tests, from query_graph_tool
  - PMI/backend/tests/test_variant_cost_tax.py
dispatched: null                     # YYYY-MM-DD when it moves to dispatched
in_review: null                      # YYYY-MM-DD when it moves to in-review
created: 2026-07-21
updated: 2026-07-21
---
```

Followed by the standard body:

```markdown
# <ID>: <title>

> Dự án: [[projects/<tên>/<tên>]]

## Tiêu chí nghiệm thu (AC)
- [ ] <verifiable condition>

## Plan
*(filled in at Plan Gate)*

## Sub-tasks
- [ ] <small step, one file/concern per step>
```

The `> Dự án: [[...]]` line is a real wikilink (not plain path text) — its purpose is to let Obsidian's Graph view draw an edge between the task and the project file (Graph only recognizes `[[wikilinks]]`, not paths inside tables/YAML). Use the full path `[[projects/<name>/<name>]]` — no alias needed since the project file's name already matches `<name>` (folder-note convention), so Obsidian displays the right name automatically and no longer shows an identical "_project" label across different projects on the Graph. This is purely Markdown content supporting navigation/visualization in Obsidian — no skill parses this line, and it has no effect on the lifecycle/gates.

The project file (`projects/<name>/<name>.md`) also has a `## Tasks` section listing wikilinks to every file under `tasks/` — this section is regenerated automatically by `/report` on every run (§6.1 skill table).

A task that goes `done` after a `/verdict changes` gets a `## Findings từ reviewer` section added by `/verdict`.

**Changing state = updating `status:` + `updated:` in the frontmatter + a commit** (audit trail comes naturally through git — see §2.3 below).

**Rule:** `/pm` MUST NOT write a task missing `files:`, `## Tiêu chí nghiệm thu (AC)`, or `tests:` — all three must come from a real code-review-graph query (§6). If the graph hasn't been queried yet, the task must not be written.

### 2.1a. ID Assignment Rule

- `/pm` and `/ingest` read the frontmatter of `<project-name>.md` → `task_prefix` + `next_task_id`.
- Create the file: `tasks/<PREFIX>-<NNN>-<slug>.md` (slug = kebab-case of the title, max 40 ASCII characters).
- After creating the file, increment `next_task_id` in `<project-name>.md` by 1.

### 2.2. Task Decomposition Rule

- Each sub-task touches **at most 1 file / 1 concern**.
- A task whose blast radius (`get_impact_radius_tool`) exceeds **8 files** → proactively propose splitting it into smaller tasks, each mapping to 1 PR/1 branch. Sizing principle: **"1 task = 1 context window = 1 branch/PR"**.
- Prioritize by `depends_on:` (if declared) and risk level (`risk: high` goes first or gets split out for easier review).

### 2.3. Task Lifecycle (state machine)

```
📋 todo → ✅ ready → 📤 dispatched → 🔍 in-review → ✔️ done
                                          ↓
                                  🔁 changes-requested → (handed back) → 📤 dispatched
```

- `todo`: task just written at Spec Gate, awaiting the User's approval of the AC.
- `ready`: Spec + Plan Gate both approved, `## Plan` is filled in, ready to hand off — **no one working on it yet**.
- `dispatched`: `executor:` + `dispatched: <date>` have been recorded in the frontmatter — the executor (outside the system) is working on it.
- `in-review`: executor reported done (`result_ref:` filled in), `/review-order` has issued the review sheet, `in_review: <date>` recorded — an independent reviewer (outside the system, ≠ executor) is checking it.
- `done`: `/verdict pass` has been recorded, with `reviewer:` + a real commit hash + human confirmation. Other tasks with `depends_on:` referencing this ID may now be unblocked (not automatic yet — §6.1, `/verdict` only surfaces this).
- `changes-requested`: `/verdict changes` has been recorded with findings — goes back to `dispatched` once the executor addresses them.

Changing state = updating `status:` + `updated:` in the frontmatter + a commit in control-tower (audit trail comes naturally through git).

---

## 3. DEFINITION OF DONE (system-wide default DoD)

A task may only be closed (`status: done`) when **all** of the following hold, **confirmed by an independent reviewer via `/verdict pass`** (control-tower never checks these itself — it doesn't run tests or read diffs):

- [ ] All of the task's AC (`## Tiêu chí nghiệm thu (AC)`) pass — confirmed by the reviewer in the review sheet.
- [ ] Related tests (`tests:`) are 100% green — the reviewer runs them in the target code repo (e.g. via that repo's `/code-review`).
- [ ] No regressions — the reviewer confirms the module's other tests are still green.
- [ ] `reviewer:` differs from `executor:` (separation of duties, §1).
- [ ] The real commit hash (`result_ref:`) has been recorded in `log.md` (§7, `Commit:` field).

A project may declare additional project-specific DoD in the "Project Gates" of `projects/<project>/<project>.md`; project DoD is ADDITIVE to this default DoD, never a replacement. The reviewer applies the DoD; control-tower only records the outcome.

---

## 4. THE TWO GATES INSIDE CONTROL-TOWER + HANDOFF OUTSIDE

Control-tower is only responsible for the first two gates (PLAN); everything after that is handed off outside — there is no internal "Code Gate" anymore.

1. **Spec Gate** — `/pm` creates a new task file under `tasks/` with `files:`/AC/`tests:`/`flows:` (`status: todo`) → stops, shows the User the **scope & AC** for approval. No code has been written yet, no `## Plan` yet.
2. **Plan Gate** — once the Spec is approved, write the concrete implementation plan into `## Plan` → stop, wait for the User to approve the **plan**. Once approved: `status: ready`, then ask the User who the `executor:` will be → record `status: dispatched` + `dispatched: <date>`. **control-tower stops here — it never writes code itself, never runs tests itself.**

After the Plan Gate, the task's lifecycle continues **outside the system**:

3. **Execution handoff** — the executor (a human/another AI, in the target code repo) does the work, runs their own tests, creates a branch/commit/PR, then reports back `result_ref:`.
4. **`/review-order`** — control-tower issues a review sheet (read-only, doesn't review itself) → hands it to an independent reviewer (≠ executor). `status: in-review`.
5. **Review outside the system** — the reviewer reads the diff, runs tests, checks AC/DoD in the target code repo (using that repo's `/code-review`) — entirely outside control-tower.
6. **`/verdict`** — the reviewer reports the outcome, control-tower records it in the frontmatter: `pass` → close the task (`status: done`, needs human confirmation); `changes` → `status: changes-requested`, handed back.

**Automatic escalation to RESTRICTED:** if a task is flagged `risk: high` (for touching a hub/bridge node — §6) or touches `schemas/`/`models.py`/migrations → both the Spec Gate and Plan Gate require explicit written/chat confirmation from the User — never silently assume approval. Closing a task (`/verdict pass`) ALWAYS needs human confirmation, regardless of risk level.

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

---

## 8. MACROS AND CONTROL COMMANDS

*   `/pm <task_description> [--project <name>]`: Spec Gate → Plan Gate → `ready` → `dispatched`. Creates a dedicated task file under `projects/<name>/tasks/` complete with `files:`/AC/`tests:`/`flows:` from the graph. **Never writes code itself, never self-verifies.**
*   `/ingest`: Reads `inbox.md`, **reconciles into an existing similar task** rather than creating a duplicate (§9), or routes it into a knowledge file (`knowledge/`/`docs/`, §11) if it isn't actionable, enriches it via the graph, removes the processed item from the inbox.
*   `/report`: Scans `projects/*/tasks/*.md`, aggregates Done/Total by `status:`, updates `<project-name>.md` + `index.md`; scans `knowledge/**/*.md` + `projects/*/docs/*.md`, updates `knowledge/_index.md`.
*   `/lint [--project <name>]`: Backlog health-check — overdue tasks, missing AC, dead file links, orphan tasks, contradictions, stuck too long in `dispatched`/`in-review`, orphan/stale knowledge (§6, §11, `.claude/skills/lint/SKILL.md`).
*   `/review-order <task ID/path> --ref <branch|commit|PR>`: Issues a review sheet for an independent reviewer, moves to `status: in-review`. Doesn't review itself, doesn't run tests.
*   `/verdict <task ID/path> <pass|changes> --reviewer @id [--commit <hash>] [--notes ...]`: Records the review outcome in the system. Checks four-eyes (`reviewer` ≠ `executor`). `pass` → closes the task (needs human confirmation); `changes` → reopens it with findings.

---

## 9. THE "RECONCILE, DON'T APPEND" RULE FOR `/ingest`

When classifying a note from `inbox.md`: if a **similar task already exists** in `projects/<name>/tasks/*.md` (same file/symbol or same topic) → **rewrite/augment that task coherently**, do NOT create a new duplicate task. Once an item is processed → remove it from `inbox.md`, log the `ingest` entry.

---

## 10. ONBOARDING A NEW PROJECT (Runbook)

When adding a new project to Control Tower:

1. Add 1 row to the **PROJECT REGISTRY** table in `index.md` (§2): project name, absolute `repo_root`, task directory.
2. Create `projects/<project-name>/` with a `<project-name>.md` file (filename MATCHES the folder name — copy the skeleton from `projects/topvnsport-pmi/topvnsport-pmi.md`, set `task_prefix` + `next_task_id: 1`), `tasks/`, `docs/`, `reviews/`.
3. Build the graph for that repo (if not already built):
   ```bash
   /home/lupca/.local/share/code-review-graph-venv/bin/python3 -m code_review_graph build --repo <repo_root>
   /home/lupca/.local/share/code-review-graph-venv/bin/python3 -m code_review_graph embed --repo <repo_root>
   ```
4. Register a daemon watch so the graph updates itself (§6.6): `daemon add <repo_root> --alias <name>`.
5. (Optional) `code-review-graph register <repo_root> --alias <name>` if you need `cross_repo_search_tool` to query across multiple projects at once.
6. **Update the Obsidian visualization** (mandatory — don't skip this the way it was skipped for WMS):
   - `.obsidian/graph.json`: add 1 entry to `colorGroups` — `{"query": "path:projects/<project-name>", "color": {"a": 1, "rgb": <a decimal rgb not already used by another entry>}}`.
   - `control-tower-map.canvas`: add 1 file node pointing to `projects/<project-name>/<project-name>.md` + 5 edges (dispatch→node, node→`g-exe` "dispatched", node→`n-review-order`, `n-verdict`→node "changes-requested loop", node→`n-lint` "scan backlog"). Copy the `n-proj-wms` node and edges `e15`-`e19` as a template (just change the id/path). `x`/`y` coordinates only need to land in empty space, no need for precision — this is purely a visual diagram.

---

## 11. KNOWLEDGE MANAGEMENT (domain knowledge, architecture decisions, conventions)

Control-tower manages 2 kinds of content: **tasks** (has a `status`, requires action — see §2) and **knowledge** (living reference material, no `status`/`executor`/`deadline`). Don't confuse the two — if a knowledge file needs action, create a separate task linking to it; don't turn a knowledge file into a task.

### 11.1. The "changes together" principle

| Document type | Example | Where |
|---|---|---|
| SYSTEM docs (change together with the code) | architecture.md, API docs, test guides | **In the code repo.** Control-tower only points to it via the References section of `<project-name>.md` — do NOT copy the content over. |
| Domain / business knowledge (changes with business rules) | VAT rules, product categorization, payment flow | **Control-tower** — `knowledge/domains/` (cross-project) or `projects/<name>/docs/` (per-project) |
| Architecture Decision Records (ADR) | Why File-Over-API? Why MinIO? | **Control-tower** — `knowledge/decisions/` (cross-project) or `projects/<name>/docs/` (per-project) |
| TODO / tech debt | Bugs, technical debt | **Turn into a task** in `tasks/` — not knowledge |

### 11.2. Directory structure

```
knowledge/                          # CROSS-PROJECT (applies to multiple projects)
├── _index.md                       # Index — updated by /report
├── domains/                        # Business domain knowledge
├── decisions/                      # Cross-project ADRs
├── conventions/                    # Shared coding/process conventions
└── research/                       # Longer research documents

projects/<name>/docs/                 # PER-PROJECT knowledge
```

### 11.3. Standard knowledge file frontmatter

```yaml
---
type: domain | decision | convention | research | reference | note
scope: general | <project-name>     # general → knowledge/, project-specific → projects/<name>/docs/
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2]
related: []                       # wikilinks to other files/ADRs, e.g. [[ADR-001-file-over-api]]
---
```

### 11.4. ADR template (`type: decision`)

```markdown
# ADR-<NNN>: <title>

## Context
<What's the problem? What pressure/constraint drove this?>

## Decision
<What was decided, and why?>

## Consequences
<What gets easier? What gets harder? What are the trade-offs?>

## Status
Accepted | Superseded by [[ADR-NNN]] | Deprecated
```

### 11.5. Routing rule for `/ingest`

When an item in `inbox.md` is **not actionable** (no deadline, no code needed, it's a business note/decision) → create a file under `knowledge/<type>/` (scope=general) or `projects/<name>/docs/` (scope=specific project), following the frontmatter in §11.3 — do NOT create a fake task for it. If it's ambiguous whether it's a task or knowledge, ask the User instead of guessing.

### 11.6. No auto-generating knowledge

Knowledge content is created/approved by humans; the agent only routes a note to the right place (§11.5) and updates the index (`/report`) — it never invents domain/ADR content the User hasn't confirmed.
