---
name: goal
description: "POC (AGENTS.md §17): define a Goal with measurable completion_conditions and spawn the first task toward it via /pm's Spec Gate. Does NOT auto-loop hypothesis->task->remeasure — that's future work beyond this POC. Activate when the user types /goal."
argument-hint: "<goal description> [--project <name>]"
allowed-tools: Read, Edit, Write, Glob
---

## Goal — POC entry point for goal-conditioned autonomy

**This is a POC** (`AGENTS.md` §17, Tier 3 per `ADR-002`). It creates a `Goal` file and spawns exactly ONE task toward it — it does not automatically iterate. Treat every run as a single step the User re-invokes, not a background loop.

### Step 1 — Define the Goal

1. Read `AGENTS.md` §17 if not already read this session.
2. Determine the target project the same way `/pm` does (`--project` flag, or infer + ask if unsure). Get `repo_root` from `index.md` §2.
3. Ask the User for `completion_conditions:` if the description doesn't already state a measurable target — **never invent a metric/threshold yourself**. A goal like "make search faster" needs the User to say what "faster" means and how it's measured before a Goal file gets written.
4. Determine `GOAL-<NNN>` — Glob `projects/<name>/goals/GOAL-*.md`, take the highest NNN + 1 (create the `goals/` directory if this is the project's first Goal).
5. Write `projects/<name>/goals/GOAL-<NNN>.md` per the schema in `AGENTS.md` §17.1: `status: pursuing`, `current_iteration: 0`, `spawned_tasks: []`, `max_iterations:` (ask the User, default 5 if they have no preference), `escalate_if:` (ask, default "2 consecutive failed attempts").

### Step 2 — Spawn the first task

1. Hand off to `.claude/skills/pm/references/task-creation.md` exactly as `/pm` would, using the Goal's description + first `completion_conditions:` entry as the task description.
2. Once the task file is written, add its ID to the Goal's `spawned_tasks:` list and set `current_iteration: 1`.
3. Write 1 entry to `log.md` (`operation: pm-create`, note in the description that this task was spawned from `GOAL-<NNN>`).

### Step 3 — Stop

Tell the User: the Goal is defined, the first task is at the Spec Gate awaiting approval like any other `/pm` task. **This skill does not re-invoke itself when the task closes** — re-measuring the Goal and deciding whether to spawn a next task is manual for now (`AGENTS.md` §17.3, not built in this POC), except for the one escalation rule that IS enforced: if a task under `spawned_tasks:` comes back `changes-requested` twice in a row, `/verdict` (not this skill) tells the User the Goal needs a look.

### Common mistakes to avoid
- Inventing `completion_conditions:` instead of asking the User for a real measurable target.
- Treating this as a background loop — it is not; nothing here auto-spawns a second task.
- Skipping the normal `/pm` Spec Gate/Plan Gate for the spawned task just because it came from `/goal`.
