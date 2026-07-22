# AI AGENT RULES OF ENGAGEMENT (AGENTS.md)

Welcome, Agent, to Control Tower. This is the top-level control file defining the "rules of the game" (roles, task lifecycle, HITL, Quality Gates) for you. You MUST read and follow the principles below before taking any action.

> **Model B (current):** control-tower only **PLANs + COORDINATEs**. It NEVER writes code, NEVER reads diffs, NEVER runs tests itself. EXECUTE (write code) and REVIEW (read diffs, run tests) both live **outside the system** — handled by a human or another AI in the target code repo. A human is always the final decision-maker.

**Detail files (load when needed):**
- `AGENTS-REFERENCE.md` — §5-§7: handoff artifacts, code-review-graph usage, audit log
- `AGENTS-PLAYBOOK.md` — §8-§11: macros, reconcile rule, onboarding, knowledge management
- `AGENTS-EXPERIMENTAL.md` — §12-§20: POC features (reputation, patterns, verifier, goals, etc.)

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
status: done                         # todo | ready | dispatched | in-review | done | changes-requested
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
📋 todo → ✅ ready → 📤 dispatched → 🔍 in-review → ✔️ done
                                          ↓
                                  🔁 changes-requested → (handed back) → 📤 dispatched
```

- `todo`: task just written at Spec Gate, awaiting approval of the AC.
- `ready`: Spec + Plan Gate both approved, `## Plan` filled in, ready to hand off.
- `dispatched`: `executor:` + `dispatched: <date>` recorded — executor is working on it.
- `in-review`: executor reported done, `/review-order` issued — reviewer is checking it.
- `done`: `/verdict pass` recorded with human confirmation.
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

## 4. THE TWO GATES INSIDE CONTROL-TOWER + HANDOFF OUTSIDE

Control-tower is only responsible for the first two gates (PLAN); everything after is handed off outside.

1. **Spec Gate** — `/pm` creates a new task file with `files:`/AC/`tests:`/`flows:` (`status: todo`) → stops, shows the User the **scope & AC** for approval.
2. **Plan Gate** — once Spec is approved, write the implementation plan into `## Plan` → stop, wait for User approval. Once approved: `status: ready`, ask who the `executor:` will be → record `status: dispatched`. **control-tower stops here.**

After the Plan Gate, the task's lifecycle continues **outside the system**:

3. **Execution handoff** — the executor does the work, creates a branch/commit/PR, reports back `result_ref:`.
4. **`/review-order`** — control-tower issues a review sheet → hands to an independent reviewer. `status: in-review`.
5. **Review outside the system** — the reviewer reads the diff, runs tests, checks AC/DoD in the target repo.
6. **`/verdict`** — the reviewer reports the outcome: `pass` → close (`status: done`, needs human confirmation); `changes` → `status: changes-requested`.

**Automatic escalation to RESTRICTED:** if `risk: high` or touches `schemas/`/`models.py`/migrations → both gates require explicit confirmation. Closing a task (`/verdict pass`) ALWAYS needs human confirmation.
