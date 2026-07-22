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
predicted_success: high              # high (>=0.7) | medium (0.4-0.7) | low (<0.4) - calculated by /pm
prediction_factors:                  # list of factors & score deductions
  score: 0.8
  deductions:
    - "blast_radius: 5 (-0.0)"
    - "hub_bridge: false (-0.0)"
    - "no_tests: false (-0.0)"
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

A task that closes via `/verdict pass` gets a `## Causal Analysis` section added — not just THAT the fix worked, but WHY (§2.1b).

**Changing state = updating `status:` + `updated:` in the frontmatter + a commit** (audit trail comes naturally through git — see §2.3 below).

**Rule:** `/pm` MUST NOT write a task missing `files:`, `## Tiêu chí nghiệm thu (AC)`, or `tests:` — all three must come from a real code-review-graph query (§6). If the graph hasn't been queried yet, the task must not be written.

### 2.1a. ID Assignment Rule

- `/pm` and `/ingest` read the frontmatter of `<project-name>.md` → `task_prefix` + `next_task_id`.
- Create the file: `tasks/<PREFIX>-<NNN>-<slug>.md` (slug = kebab-case of the title, max 40 ASCII characters).
- After creating the file, increment `next_task_id` in `<project-name>.md` by 1.

### 2.1b. Causal Analysis (added by `/verdict pass`)

When a task closes via `/verdict pass`, the reviewer fills in a `## Causal Analysis` section on the task body — the point is to capture WHY the fix works, not just THAT it works, so the same root cause can be recognized and reused next time (§13):

```yaml
causal_analysis:
  root_cause: "N+1 query in ProductService.get_all()"
  mechanism: "Added .select_related('category') reduces DB calls from N+1 to 2"
  counterfactual: "Without fix, latency would remain 450ms under 100 concurrent users"
  pattern_id: "n-plus-one-query"  # reusable pattern identifier, see knowledge/patterns/
```

- **Required** when `risk: high` — `/verdict` must prompt the reviewer for all four fields and refuse to record `pass` until they're filled in.
- **Optional but encouraged** when `risk: normal` — `/verdict` still prompts; if the reviewer declines, the task closes without a `## Causal Analysis` section.
- `pattern_id` should match an existing file in `knowledge/patterns/<pattern_id>.md` (§13). If no existing pattern fits, `/verdict` proposes creating a new one (COLLABORATIVE, §1) rather than inventing pattern content unilaterally.
- Whenever `pattern_id` is set and matches an existing pattern file, `/verdict` appends this task's ID + a 1-line summary to that pattern's **Past Instances** list.

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

---

## 12. AGENT REPUTATION & PROFILE STANDARD

System tracks execution and review performance history for all agents (`ai` and `human`) under `knowledge/agents/@<agent_id>.md`.

### 12.1. Agent Profile Schema

```yaml
---
agent_id: "@antigravity"
type: ai                    # ai | human
total_tasks_executed: 4
total_tasks_reviewed: 0
success_rate: 1.0           # (pass on first review) / total_tasks_executed
avg_review_rounds: 1.0      # average review iterations required
strengths: [backend, frontend, testing, infra, database]
weaknesses: []
recent_trend: improving      # improving | stable | declining
last_active: 2026-07-22
---
```

### 12.2. Domain Strength Auto-Detection Rules

Task `files:` match against rules:
- `*.py`, `/backend/` → `backend`
- `*.tsx`, `*.vue`, `/web/` → `frontend`
- `*models.py`, `migrations/` → `database`
- `*test*.py`, `/tests/` → `testing`
- `docker*`, `.github/` → `infra`

### 12.3. Reputation Lifecycle
- **Update on `/verdict`**: Updates `total_tasks_executed` / `total_tasks_reviewed`, `success_rate`, `avg_review_rounds`, `strengths`, `recent_trend`, and `last_active`.
- **Recommendation on `/pm`**: Matches task domain requirements with agent `strengths` during dispatch, suggesting optimal executors and surfacing warnings for low success rates (< 0.6) or matching weaknesses.

---

## 13. PATTERN LIBRARY (Causal Analysis)

A task closing tells you THAT a fix worked; it doesn't tell you WHY, so the same root cause quietly resurfaces elsewhere. Recurring root causes are captured as reusable **patterns** under `knowledge/patterns/`, so `/pm` can suggest "this looks like pattern X, see how `<task>` fixed it" at Spec Gate, and `/lint` can flag the same signature recurring elsewhere before it's fixed everywhere.

### 13.1. Pattern file schema (`knowledge/patterns/<pattern_id>.md`)

```yaml
---
pattern_id: n-plus-one-query
category: performance          # performance | correctness | security | reliability | maintainability
severity: medium                # low | medium | high | critical
created: 2026-07-22
updated: 2026-07-22
---

# <pattern_id>

## Problem Signature
<How to recognize this pattern — code shape, symptoms, metrics/log signals>

## Detection
<How to spot it in this codebase: grep pattern, code-review-graph query, metric threshold...>

## Solution Template
<The general fix shape — not tied to any one task>

## Past Instances
- [[<TASK-ID>]] — <1-line summary of what happened>
```

### 13.2. Lifecycle
- **Created**: manually, or proposed by `/verdict pass` when a reviewer's `causal_analysis.pattern_id` (§2.1b) doesn't match an existing file — `/verdict` stops and asks the User before writing a new pattern file (COLLABORATIVE, §1); it never invents pattern content unilaterally (mirrors the rule in §11.6 for knowledge in general).
- **Past Instances updated**: whenever `/verdict pass` records a `causal_analysis.pattern_id` that matches an existing pattern file, it appends `- [[<task ID>]] — <1-line summary>` to that file's **Past Instances** section.
- **Consulted by `/pm`** (Spec Gate): matches the new task's description against `knowledge/patterns/*.md` Problem Signatures and surfaces a suggestion — "this looks like pattern `<id>`, see how `<task from Past Instances>` was fixed" — as a hint only, never auto-applied, never blocks the gate.
- **Consulted by `/lint`**: cross-references each pattern's `Detection` heuristic against the codebase (via `code-review-graph`, read-only) to flag places the pattern may recur without a task referencing it in `Past Instances` → surfaced as a suggested **preventive task**, never created automatically (read-only, same as the rest of `/lint`, §1).

### 13.3. Index (`knowledge/patterns/_index.md`)
A flat registry table (`pattern_id`, `category`, `severity`, instance count) — maintained alongside the pattern files; add a row whenever a new pattern file is created.

---

## 14. CROSS-REPOSITORY INTELLIGENCE

`/pm` no longer treats each registered repo as an island — before writing a new task, it also checks whether a similar implementation already exists in ANOTHER registered repo, so the same fix doesn't get reinvented per-project. (`paradigm_source`: RepoGraph 2024, BLAZE 2024 — see ADR-002.)

### 14.1. PROJECT REGISTRY field: `patterns_exportable`
Each row in the PROJECT REGISTRY (`index.md` §2) carries a `patterns_exportable: true|false` flag — `true` marks a repo whose patterns are generic enough to be worth surfacing to other projects (e.g. a shared monorepo utility), `false` marks domain-specific code unlikely to transfer. Set manually when onboarding a project (§10); treat as `false` if the column is missing for an older row.

### 14.2. Cross-repo search at Spec Gate
When `/pm` locates the target file/symbol (task-creation.md step 2), it also calls `cross_repo_search_tool(query=<keywords from the task description>, repo_root=<target repo_root>)` scoped across every OTHER registered repo with `patterns_exportable: true`. A match above ~70% similarity gets surfaced as a note in the task draft (never a blocker): "Similar implementation exists in `<project>/<file>` (`<score>`% match) — consider reusing/adapting instead of reimplementing." The User decides whether to reuse or proceed independently.

### 14.3. `knowledge/patterns/cross-repo/`
A confirmed-useful cross-repo match (User said "yes, reuse this") gets cached as a lightweight note under `knowledge/patterns/cross-repo/<slug>.md` (frontmatter: `source_project`, `target_project`, `similarity_score`, `created`), so the next `/pm` search on a related keyword hits this cache before re-querying the graph. Indexed in `knowledge/patterns/cross-repo/_index.md` (same shape as §13.3).

### 14.4. Pattern learning on task close
When `/verdict pass` closes a task whose project has `patterns_exportable: true`, it checks — informational only, never blocks closing — whether the fix looks generic enough to apply elsewhere; if so it suggests to the User: "This may apply to `<other patterns_exportable project>` too — consider filing a task there." `/verdict` never auto-files that task itself.

---

## 15. LLM-MODULO VERIFIER

Per the LLM-Modulo framework (ICML 2024, see ADR-002): `/pm` should not present a plan to the human until a symbolic (non-LLM) checklist has validated it — the LLM proposes, deterministic rules verify.

### 15.1. Verifier rules (`.claude/verifier-rules.yaml`)
```yaml
rules:
  - id: no-circular-deps
    check: "depends_on does not create a cycle"
  - id: files-exist
    check: "every path in files: exists in the graph (or is flagged '(path not confirmed via graph)')"
  - id: reasonable-scope
    check: "blast radius <= 8 files, or already proposed as a split"
  - id: tests-for-changes
    check: "at least one entry in tests:, or a knowledge-gap sub-task was added (AGENTS.md §6.2)"
  - id: no-conflicting-tasks
    check: "no other task with overlapping files: is currently dispatched/in-review"
```
Extensible — add a rule by appending an entry with `id`/`check`; no code changes needed since every check is evaluated by the agent reading the task draft + graph/backlog state, not executed as a program.

### 15.2. When `/pm` runs it
Right after computing `predicted_success` (task-creation.md, before "Closing the Spec Gate"), `/pm` evaluates every rule in `.claude/verifier-rules.yaml` against the draft task and prints the results block (§15.3) above the task summary. A `❌` requires either a mechanical auto-fix (e.g. narrowing `files:`, adding the missing test sub-task) or an explicit User override (§15.4) before the Spec Gate can close; a `⚠️` is shown but doesn't block.

### 15.3. Output format
```
✅ no-circular-deps: passed
✅ files-exist: passed
⚠️ reasonable-scope: 12 files, suggest splitting
❌ tests-for-changes: missing test for services/payment.py
```

### 15.4. Override
The User can override a `❌`/`⚠️` explicitly ("proceed anyway", "I accept the risk on X"). `/pm` records the override verbatim in a `## Verifier Overrides` section of the task body and in the `pm-create` log entry — auditable later via `/lint`. Never silently downgrade a `❌` to pass without a recorded override.

---

## 16. CONFIDENCE CALIBRATION

Builds on CT-001's `predicted_success` score (§8.1/`pm/references/task-creation.md`) — turns a static score into a calibrated interval that decides how much human-gate friction a task actually needs. (`paradigm_source`: MIT Conformal Prediction for NLP 2025 — see ADR-002.)

### 16.1. `confidence_interval:` in frontmatter
```yaml
confidence_interval: [0.72, 0.91]   # [lower, upper], computed alongside predicted_success
```
Computed from: the `predicted_success` score (§ task-creation.md step 9), whether `.claude/verifier-rules.yaml` (§15) passed clean, and historical accuracy on similar tasks from `knowledge/metrics/prediction-accuracy.md`. More historical agreement on similar tasks → narrower interval; a novel task shape → wider interval (no historical precedent to narrow it).

### 16.2. Dynamic gate rule
```
If confidence_interval is narrow AND lower > 0.85:
  → Spec/Plan Gate still show the task, but the User may quick-approve with a single "ok" (log only, no extended review expected).
If confidence_interval is wide OR lower < 0.60:
  → REQUIRE explicit, itemized human approval (not a bare "ok") — call out specifically what's uncertain.
Else:
  → Standard gate (current default behavior, §4).
```
This adjusts gate FRICTION, never gate PRESENCE — every task still stops at Spec Gate and Plan Gate (§4); confidence only changes how much the agent asks the User to scrutinize before accepting a quick approval.

### 16.3. Always-overridable
The User can force standard/strict gating regardless of confidence ("review every task this week", "don't fast-path anything for project X") — `/pm` honors a standing instruction like this for its stated scope without re-deriving confidence per task.

### 16.4. Calibration tracking + drift
`knowledge/metrics/prediction-accuracy.md` gains a `confidence_interval` column next to `predicted_success`; `/verdict` records whether the actual outcome (`pass`/`changes`) fell inside the predicted interval. `/lint` gains a checklist item: if the last 5+ calibrated predictions have an actual-in-interval rate below 70%, flag "confidence calibration drifting — consider widening intervals or reviewing the scoring formula."

---

## 17. GOAL-CONDITIONED AUTONOMY (POC)

**Status: POC** — Tier 3 paradigm shift (ADR-002 §Trade-offs: "Tier 3 as research/POC, no committed deadline"). Ships as an opt-in path alongside the existing task-list flow, never a replacement for it. Depends on CT-001, CT-005, CT-006.

### 17.1. `Goal` entity (new, distinct from `Task`)
`projects/<name>/goals/GOAL-<NNN>.md`:
```yaml
---
id: GOAL-001
title: "API response time < 100ms for /products"
status: pursuing | achieved | abandoned
completion_conditions:
  - metric: p99_latency
    target: "< 100ms"
    measurement: "production APM"
max_iterations: 5
current_iteration: 0
escalate_if: "2 consecutive failed attempts"
spawned_tasks: []
---
```
A Goal has no `executor:`/`reviewer:` of its own — those live on its `spawned_tasks:`.

### 17.2. `/goal` macro — POC scope only
New skill `.claude/skills/goal/SKILL.md`: `/goal <description> [--project <name>]` creates a Goal file — the User supplies (or confirms) `completion_conditions:` since `/goal` never invents a measurable target unilaterally — then spawns exactly ONE task toward it via the normal `/pm` Spec Gate flow, recorded in `spawned_tasks:`. **The POC stops there** — it does not yet auto-loop hypothesis → task → remeasure → next hypothesis (§17.3 is the intended full design, explicitly NOT built in this POC).

### 17.3. Intended full design (future work, beyond POC)
- On a spawned task's `/verdict`, re-measure the Goal's `completion_conditions:`; if unmet, generate a new hypothesis and spawn the next task automatically, incrementing `current_iteration`.
- Escalate to the User when `max_iterations` is reached, on `escalate_if` (e.g. 2 consecutive `changes-requested`), or when confidence (§16) drops below a threshold.
- Hierarchical goals: a Goal's `completion_conditions:` may reference sub-Goals.

### 17.4. Escalation (the one piece of §17.3 the POC does enforce)
Even at POC scope: if a task spawned under a `spawned_tasks:` Goal comes back `changes-requested` twice in a row, `/verdict` tells the User the Goal needs a human look rather than silently letting the User re-dispatch a third attempt unprompted.

---

## 18. STIGMERGIC COORDINATION (POC)

**Status: POC** (ADR-002 §Trade-offs). Depends on CT-002 (reputation, done).

### 18.1. `events.jsonl` (new, append-only, root of the repo)
One JSON line per task state change control-tower already makes (dispatch, review-order, verdict) — a machine-readable mirror of `log.md`'s human-readable entries, not a replacement for it:
```json
{"ts": "2026-07-22T17:00:00Z", "op": "verdict", "task": "CT-003", "status": "done", "actor": "@claude"}
```
Written by the same skills that already write `log.md` (§7) — one more append alongside the existing entry, not a new workflow.

### 18.2. Task auto-claiming (POC scope, opt-in per agent)
An agent MAY self-claim an unassigned (`status: ready`, `executor: null`) task whose domain matches its own `strengths:` (`knowledge/agents/@<id>.md`, §12) by writing `executor:` + `dispatched:` itself and logging a `dispatch` entry noting `claimed_by: self`. This is opt-in — the default remains the User assigning `executor:` at the Plan Gate (§4); auto-claiming only applies when an agent has been explicitly told to operate this way. First-claim wins: if two agents write `executor:` near-simultaneously, whichever commits first to git wins — the other detects the conflict on its next read and backs off without contesting it.

### 18.3. Emergent prioritization (documented signal, not an enforced field)
Tasks referenced by more `depends_on:`/`related:` edges, or mentioned across more `log.md` entries, read as informally higher-priority. `/lint` may surface this as a sort hint in its report, but no priority is auto-written — this stays a hint so it never fights with the human-set `priority:` field.

### 18.4. Explicitly NOT in this POC
No removal of the explicit-dispatch default; no automated "graph-change watcher" daemon that auto-creates task candidates from knowledge gaps or test failures (AC1 of the original research task) — that's future work. The POC only defines the event-log format an agent could poll (§18.1) and the opt-in claiming rule (§18.2); it does not ship a poller or a central-dispatcher removal.

---

## 19. AUTO-REMEDIATION WITH TNR SAFETY (POC)

**Status: POC** (ADR-002 §Trade-offs). Depends on CT-003 (causal analysis) + CT-005 (verifier).

### 19.1. `tnr_spec:` (task frontmatter, optional)
```yaml
tnr_spec:
  invariants:
    - "All existing tests must pass"
    - "No new critical/high severity issues"
    - "Response time p99 not increase > 10%"
  rollback_trigger: "Any invariant violated"
```

### 19.2. POC scope: diagnosis-assist only, never auto-commit
The POC covers diagnosis (an inbox item tagged `source: auto-detected` — see `.claude/skills/ingest/SKILL.md` — gets matched against `knowledge/patterns/*.md`, §13, for a likely root cause, and the drafted task gets a suggested `tnr_spec:` block) but explicitly NOT sandboxed auto-execution or auto-commit. A human/executor still writes and applies the fix through the normal `/pm` → dispatch → `/review-order` → `/verdict` pipeline (§4). No fix is ever auto-committed by control-tower.

### 19.3. Why full auto-remediation is out of scope for control-tower
Control-tower has no code, no test runner, no staging environment (`CLAUDE.md`: "This repo does NOT contain product code"). Deploying a fix to staging, running the test suite, and comparing metrics (the TNR sandbox itself) is EXECUTE-role work that belongs in the target repo, entirely outside this system (§1) — a future task should define that at the target-repo level (e.g. a GitHub Action implementing the `tnr_spec:` invariants), with control-tower only recording the outcome (§19.4).

### 19.4. `auto_remediated: true` verdict flag
If an executor in the target repo already ran their own TNR-style safety check before reporting back, `/verdict pass --auto-remediated` records `auto_remediated: true` in the frontmatter. This is metadata about HOW the fix was validated — it changes nothing about the close gate itself: `pass` still always needs human confirmation (§3, §4, no exception), and reviewer still ≠ executor (§1).

---

## 20. VERICODING (POC)

**Status: POC** (ADR-002 §Trade-offs).

### 20.1. `formal_spec:` (task frontmatter, optional)
```yaml
formal_spec:
  language: dafny   # or lean4, verus
  spec: |
    ensures result >= 0
    ensures forall i :: 0 <= i < items.Length ==> items[i].price > 0
```

### 20.2. `/pm` NL→spec assist (POC scope: suggestion only, never verified here)
When the User opts in (the task description mentions a formal-methods keyword, or asks explicitly), `/pm` drafts a `formal_spec:` block by best-effort rephrasing the AC's measurable clauses as `ensures`/`requires` — this draft is LLM-generated and NOT verified by `/pm` itself (control-tower has no Dafny/Lean/Verus toolchain to run). It's a starting point for the target repo's own formal-methods setup, never auto-inserted without the User reviewing it.

### 20.3. Executor + reviewer implications
If a task carries `formal_spec:`, the EXECUTOR (outside the system, in the target repo, §1) is responsible for actually running the proof verifier. If the executor reports the proof passed (noted in `result_ref`), the reviewer may substitute "proof kernel passed" for "ran the test suite" on that specific AC in the DoD (§3) — but the reviewer still confirms the spec matches the AC's INTENT, and `/verdict pass` still always needs human confirmation, no exception (§3, §4).

### 20.4. Gradual adoption
`formal_spec:` stays optional per-task, per the original task's AC5 — no project is required to adopt it. Suggested starting point: payment/auth-adjacent tasks, at the User's discretion; non-critical paths keep using traditional testing.

