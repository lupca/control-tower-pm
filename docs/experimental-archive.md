# Experimental Features Archive

Dormant experimental features formerly documented in `AGENTS-EXPERIMENTAL.md`.
This file is retained for future reference only; these features are disabled and
must not be treated as operational guidance unless explicitly re-enabled by a
later decision.

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
