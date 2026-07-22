# AGENTS-EXPERIMENTAL.md

POC and experimental features (§12-§20). Load only when working with these specific capabilities.

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
