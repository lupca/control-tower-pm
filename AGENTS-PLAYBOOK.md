# AGENTS-PLAYBOOK.md

Runbooks for macros, reconciliation, project onboarding, and knowledge management. Load when running `/ingest`, `/lint`, onboarding a new project, or routing knowledge.

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

> Obsidian visualization (graph.json colorGroups, control-tower-map.canvas) was **removed** per ADR-004 (2026-07-22) — no visualization step is needed when onboarding.

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
