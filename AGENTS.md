# AI AGENT RULES OF ENGAGEMENT (AGENTS.md)

Welcome, Agent, to Control Tower. This is the top-level control file defining the "rules of the game" (roles, task lifecycle, HITL, Quality Gates) for you. You MUST read and follow the principles below before taking any action.

**Detail files (load when needed):**
- `AGENTS-REFERENCE.md` — §5-§7: handoff artifacts, code-review-graph usage, audit log
- `AGENTS-PLAYBOOK.md` — §8-§11: macros, reconcile rule, onboarding, knowledge management
- `docs/experimental-archive.md` — archive of dormant experimental features (§14, §17-§20); reference only, not operational guidance loaded by skills.

---

## 1. ROLES & SEPARATION OF RESPONSIBILITIES

| Role                                                    | Who does it                                                                      | Touches code?                                     |
| :------------------------------------------------------- | :------------------------------------------------------------------------------ | :------------------------------------------------ |
| **PLAN** (`/pm` generates task + AC + graph context)     | control-tower                                                                   | NO — only reads the graph (static analysis, read-only) |
| **EXECUTE** (write code, create branch, run tests)       | **OUTSIDE the system** — a human or another AI, in the target code repo         | YES — this is the ONLY point where code gets written |
| **REVIEW/CHECK** (read diff, run tests, check AC/DoD)    | **OUTSIDE the system** — an independent reviewer (≠ executor), using that repo's `/code-review` | READS — entirely outside control-tower            |
| **COORDINATE** (issue review order, record verdict, audit) | control-tower                                                                   | NO — Markdown only                                 |
| **FINAL acceptance decision**                            | A human (four-eyes principle)                                                   | —                                                  |

**Separation-of-duties principle (mandatory): reviewer ≠ executor.** If
`reviewer:` matches the `executor:` of the same task, refuse to record any
verdict and require a different, independent reviewer (human or AI).

**"Outside the system" means a SEPARATE CLI process, NOT a subagent:**
- ✅ `Bash("cd <repo> && claude -p '...' --dangerously-skip-permissions")` — spawns a new Claude Code process in the target repo
- ✅ `Bash("cd <repo> && codex exec ...")` — spawns a new Codex process
- ❌ `Agent()` tool — this is a subagent WITHIN the same Claude Code session, still "inside" control-tower
- See `spawn-patterns.md` (memory) and `/dispatch` skill for correct CLI commands.

Because roles are cleanly separated as above, the AUTONOMOUS/COLLABORATIVE/RESTRICTED matrix only applies to actions **taken by control-tower itself** (always Markdown, never code):

| Permission Level | Action (all Markdown, never code) | Process |
| :--- | :--- | :--- |
| **AUTONOMOUS** *(Free rein)* | - Read and analyze `projects/` (including `projects/<name>/reviews/`), `knowledge/`, `inbox.md`. <br>- Use `code-review-graph` (read-only) to check blast radius/test gaps/flows. <br>- Run `/lint` (read + report only). | Execute automatically, no need to ask the User. |
| **COLLABORATIVE** *(Mode-controlled)* | - Write a new task into `projects/<name>/tasks/*.md` (Spec Gate). <br>- Write the plan into `## Plan` (Plan Gate). <br>- Mark `dispatched`, record `executor:`. <br>- Issue a review order (`/review-order`). <br>- Record a reviewer verdict. <br>- Route knowledge into `knowledge/`/`docs/` (§11). | Log the rationale in `log.md`, then use the coordination-mode behavior at the matching Gate (§4). |
| **RESTRICTED** *(Protected actions)* | - Bulk update (>3 tasks). <br>- Delete a task/project file. | Always stop and ask for explicit written/chat approval, including in `bypass` mode. |

The four-eyes rule is harder than either permission level: when `reviewer:` equals
`executor:`, refuse the verdict immediately. Do not prompt for an override and do
not let coordination mode weaken this rule.

---

## 2. TASK MANAGEMENT PROCESS (File-Over-API — task-per-file)

Each task is **its own Markdown file** in `projects/<project-name>/tasks/`, no longer bundled with other tasks into one big file (reason: avoids git conflicts when multiple executors/reviewers work in parallel, and gives each task room for long spec/plan/review notes without bloating a shared file).

```
projects/<project-name>/
├── <project-name>.md      # overview + Project Gates + References + next_task_id counter
├── docs/                 # project-specific knowledge (§11)
└── tasks/
    ├── <PREFIX>-001-<slug>.md
    └── <PREFIX>-002-<slug>.md
```

### 2.1. Standard Task Syntax (YAML frontmatter + body)

Every file in `tasks/` starts with frontmatter:

```yaml
---
id: PMI-001                          # <PREFIX>-<NNN>, NNN zero-padded to 3 digits
title: "Thêm validation cost/tax cho variant"
status: done                         # todo | dispatched | in-review | done | changes-requested
priority: high                       # urgent | high | medium | low
risk: high                           # high | normal (default normal)
deadline: 2026-08-01                 # YYYY-MM-DD, optional
executor: "@dev-tung"                # filled in at dispatch time
reviewer: null                       # filled in at review-order time, MUST differ from executor
result_ref: "topvnsport@main (commit 9d122b9)"  # branch/commit/PR from the executor
depends_on: []                       # list of task IDs
files:                                # repo-relative, from get_impact_radius_tool
  - PMI/backend/schemas/tier_variation.py
flows: [product-create, product-update]  # from get_affected_flows_tool
tests:                                # existing tests, from query_graph_tool
  - PMI/backend/tests/test_variant_cost_tax.py
dispatched: null                     # YYYY-MM-DD when it moves to dispatched
in_review: null                      # YYYY-MM-DD when it moves to in-review
predicted_success: high              # high (>=0.7) | medium (0.4-0.7) | low (<0.4)
prediction_factors:                  # list of factors & score deductions
  score: 0.8
  deductions:
    - "blast_radius: 5 (-0.0)"
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

## Verification
*(commands executor runs to verify AC — model nhỏ chỉ cần chạy, không cần nghĩ)*
- `pytest tests/unit/test_*.py` → 100% pass
- `grep -r "hardcoded" src/` → 0 matches

## Plan
*(filled in at Plan Gate)*

## Sub-tasks
- [ ] <small step, one file/concern per step>
```

**Rule:** `/pm` MUST NOT write a task missing `files:`, `## Tiêu chí nghiệm thu (AC)`, `## Verification`, or `tests:` — `files:`/`tests:` must come from a real code-review-graph query (see `AGENTS-REFERENCE.md` §6). `## Verification` contains concrete commands (pytest, curl, grep) so executor chỉ cần chạy theo, không cần tự nghĩ cách verify.

### 2.2. Task Decomposition Rule

- Each sub-task touches **at most 1 file / 1 concern**.
- A task whose blast radius exceeds **8 files** → proactively propose splitting it into smaller tasks.
- Prioritize by `depends_on:` and risk level (`risk: high` goes first or gets split out).

### 2.3. Task Lifecycle (state machine)

```
📋 todo → 📤 dispatched → 🔍 in-review → ✔️ done
                                ↓
                        🔁 changes-requested → (handed back) → 📤 dispatched
```

- `todo`: task just written at Spec Gate, awaiting approval of the AC.
- `dispatched`: Spec + Plan are approved, `## Plan`, `executor:`, and
  `dispatched: <date>` are recorded — executor is working on it.
- `in-review`: executor reported done, `/review-order` issued — reviewer is checking it.
- `done`: `/verdict pass` recorded after an independent review and a permitted
  Verdict Gate (explicit confirmation or human-selected `bypass`).
- `changes-requested`: `/verdict changes` recorded — goes back to `dispatched`.

---

## 3. DEFINITION OF DONE (system-wide default DoD)

A task may only be closed (`status: done`) when **all** of the following hold, **confirmed by an independent reviewer via `/verdict pass`** (control-tower never checks these itself):

- [ ] All AC pass — confirmed by the reviewer.
- [ ] Related tests (`tests:`) are 100% green.
- [ ] No regressions — other tests are still green.
- [ ] `reviewer:` differs from `executor:` (separation of duties).
- [ ] The real commit hash (`result_ref:`) has been recorded.

A project may declare additional project-specific DoD in `projects/<project>/<project>.md`; project DoD is ADDITIVE to this default DoD.

---

## 4. TASK STATES, COORDINATION MODES, AND GATES

### 4.1. States are durable task lifecycle data

Task states are the frontmatter values in §2.3:
`todo → dispatched → in-review → done`, with `changes-requested` looping back
to `dispatched`. A Gate is not a state and must never be encoded as a temporary
frontmatter status.

### 4.2. Coordination mode

The active mode is stored in `state/mode.md`. If the file is missing or invalid,
fail safely to `supervised`.

| Mode | Gate behavior | Dispatch/verdict | Protected actions |
| :--- | :--- | :--- | :--- |
| `plan-only` | Spec, Plan, and Review-order still require confirmation. | Block; explain that the mode must change before continuing. | n/a because these actions are already blocked or still prompt. |
| `supervised` *(default)* | Stop at every Gate and wait for explicit User confirmation. | Prompt at the matching Gate. | Prompt. |
| `bypass` | Auto-approve each Gate, record `auto-approved: <gate>` in the action's audit entry, and continue in the same invocation. | Continue without stopping. | **Prompt; bypass never auto-approves them.** |

Use `/mode` to display the current level and `/mode <plan-only|supervised|bypass>`
to change it. Mode changes are themselves recorded in `log.md`.

Protected actions are always interactive:

- deleting a task or project;
- bulk-updating more than three tasks.

The four-eyes equality check is a hard refusal, not a protected prompt:
`reviewer == executor` must always stop without offering an override.

### 4.3. Gates are stop-or-continue checkpoints

Every gate-bearing skill reads `state/mode.md` at each Gate; it must not cache
the value from an earlier Gate. A Gate decides whether the flow stops, continues,
or is blocked. It does not omit the action before or after it. Audit entries,
task updates, prediction records, agent-stat updates, and all other specified
side effects still run exactly once when their corresponding action executes.

| Gate | `plan-only` | `supervised` | `bypass` |
| :--- | :--- | :--- | :--- |
| Spec (`/pm`) | Prompt | Prompt | Auto-approve + continue |
| Plan (`/pm`) | Prompt | Prompt | Auto-approve + continue |
| Dispatch (`/pm` → `/dispatch`, or direct `/dispatch`) | Block | Prompt | Auto-approve + continue |
| Review-order (`/review-order`) | Prompt | Prompt | Auto-approve + continue |
| Verdict (`/verdict`) | Block | Prompt | Auto-approve + continue |

If `risk: high` or a task touches `schemas/`, `models.py`, or migrations,
Spec and Plan remain explicit-confirmation Gates in `plan-only` and
`supervised`. Only an explicitly selected `bypass` mode auto-approves them;
protected actions and the four-eyes hard rule remain unchanged.

### 4.4. Flow and outside handoff

1. **Spec Gate** — `/pm` creates a `todo` task with
   `files:`/AC/`tests:`/`flows:`, performs its required logging and prediction
   side effects, then checks the Gate.
2. **Plan Gate** — after Spec approval, `/pm` writes `## Plan`, performs its
   required side effects, then checks the Gate.
3. **Dispatch Gate** — select/confirm an executor and run `/dispatch`. On
   approval it records `status: dispatched` and hands execution outside the
   system. In `bypass`, `/pm` proceeds through all three Gates in one invocation.
4. **Execution handoff** — the outside executor writes code, runs tests, and
   reports a real `result_ref:`.
5. **Review-order Gate** — `/review-order` records the result reference, creates
   the review sheet, and moves the task to `in-review` after the Gate permits it.
6. **Review outside the system** — an independent reviewer reads the diff, runs
   tests, and checks AC/DoD in the target repo.
7. **Verdict Gate** — `/verdict` records `pass` as `done` or `changes` as
   `changes-requested` after the Gate permits it and the hard four-eyes check
   passes.
