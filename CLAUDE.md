# CLAUDE.md

This is the **control-tower** repo — where work is handed off to and tracked for other projects using natural language (File-Over-API). This repo does NOT contain product code; it only manages tasks as Markdown.

**Model B (current):** control-tower only **PLANs + COORDINATEs**. It NEVER writes code, NEVER reads diffs, NEVER runs tests itself. EXECUTE (write code) and REVIEW (read diffs, run tests) both live **outside the system** — a human or another AI, in the target code repo, independent of each other (reviewer ≠ executor).

## Before doing anything in this session

1. Read **`AGENTS.md`** — core rules (roles, gates, task syntax, DoD).
2. Read **`index.md`** — the project map + PROJECT REGISTRY (look up the target project's absolute `repo_root` here).

Detail files are loaded by skills when needed — don't read upfront:
- `AGENTS-REFERENCE.md` — §5-§7: handoff artifacts, code-review-graph usage, audit log
- `AGENTS-PLAYBOOK.md` — §8-§11: macros, reconcile rule, onboarding, knowledge management
- `AGENTS-EXPERIMENTAL.md` — §12-§20: POC features (reputation, patterns, verifier, goals, etc.)

## Macros

- `/pm <task description> [--project <name>]` — Spec Gate → Plan Gate → `ready` → `dispatched`. Creates a dedicated task file under `projects/<name>/tasks/`, NEVER writes code itself (skill `pm`).
- `/ingest` — classifies `inbox.md` into tasks (reconciling into an existing task rather than creating a duplicate), or routes it into a knowledge file under `knowledge/`/`projects/<name>/docs/` if not actionable (skill `ingest`).
- `/report` — updates progress in `<project-name>.md` + `index.md`, updates `knowledge/_index.md` (skill `report`).
- `/lint [--project <name>]` — backlog health-check: overdue tasks, missing AC, dead file links, orphans, stuck in `dispatched`/`in-review` (skill `lint`).
- `/review-order <task> --ref <branch|commit|PR>` — issues a review sheet for an independent reviewer (outside the system), doesn't review itself (skill `review-order`).
- `/verdict <task> <pass|changes> --reviewer @id ...` — records the review outcome, checks four-eyes, only `pass` closes the task (skill `verdict`).

## Coordinator Style

- Keep coordinator responses terse: 1–2 sentences, with no long explanations.
- Batch adjacent confirmations into one prompt instead of asking at every step: `Spec+Plan ok? Dispatch @agent? [y/n]`
- After spawning a CLI process, do not summarize its output; report only pass/fail and the next action.

## Remember

- This repo's `.mcp.json` already registers the `code-review-graph` server (sharing the same binary as other repos), so the graph tools are available even when the cwd is `control-tower`. This tool is ONLY for static analysis (read-only) during PLAN/COORDINATE — never to read an actual diff or run tests.
- Every `code-review-graph` tool call must be made with `repo_root=<absolute path>` looked up from the PROJECT REGISTRY in `index.md` — this session's cwd is `control-tower`, not the target repo, so auto-detect will be wrong.
- A task must have Acceptance Criteria, tests (`tests:`), and related files (`files:`) sourced from the real graph — see `AGENTS.md` §2, `AGENTS-REFERENCE.md` §6 before using `/pm`/`/ingest`.
- `/pm` only goes through Spec Gate → Plan Gate then stops at `dispatched` (`AGENTS.md` §4) — never skip a gate, never silently assume approval, and **there is no internal Code Gate**.
- Writing code always happens outside the system (executor); reviewing/verifying always happens outside the system (reviewer, using the target repo's `/code-review`) — control-tower only issues the review sheet (`/review-order`) and records the outcome (`/verdict`).
- Never close a task (`status: done`) outside the `/verdict pass` flow, and `/verdict pass` always refuses if `reviewer:` == `executor:` (separation of duties).
- Each task is its own file under `projects/<name>/tasks/<ID>-<slug>.md` with YAML frontmatter — tasks are no longer bundled into one shared file (`AGENTS.md` §2).
- Knowledge files (`knowledge/`, `projects/<name>/docs/`) have no `status`/`executor`/`deadline` — see `AGENTS-PLAYBOOK.md` §11 before creating/routing knowledge.
