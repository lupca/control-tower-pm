---
name: dispatch
description: Build and hand off executor or reviewer CLI commands for a task, including lifecycle and four-eyes checks. Activate on /dispatch.
argument-hint: "<task-id> @<agent-id> [--review]"
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
---

# /dispatch — Auto spawn CLI executor/reviewer

**Usage:** `/dispatch <task-id> @<agent-id> [--review]`

**Examples:**
- `/dispatch MVA-001 @claude-sonnet-medium` — dispatch executor
- `/dispatch MVA-001 @gpt-5.6-sol --review` — dispatch reviewer

> **CRITICAL:** Use `Bash()` to spawn CLI processes, NOT `Agent()` tool!
> - ✅ `Bash("cd <repo> && claude -p '...'")` — separate process, outside the system
> - ❌ `Agent("Execute task...")` — subagent in same session, still inside control-tower

> **CRITICAL: REPO PATH CONFUSION PREVENTION**
> - `control-tower` (this repo, cwd) = coordination only, NO code, NO backend/
> - `control-tower-v2` = actual code repo at `/home/lupca/projects/control-tower-v2`
> - Executor MUST `cd <repo_root>` from PROJECT REGISTRY before writing code
> - If executor writes to `/home/lupca/projects/control-tower/backend/` → WRONG REPO!

## Steps

## Mechanical handoff script

After the LLM has selected the agent, checked the Gate, and completed the
narrative audit work, call the mechanical builder:

```bash
python3 scripts/ct-dispatch.py <task-id> [--role execute|review] [--reviewer @id] [--print-only]
```

The script reads the task, PROJECT REGISTRY, agent profile, and
`knowledge/guides/spawn-patterns.md`, then prints the exact command. It never
spawns a process. Use `--print-only` while presenting the command for
confirmation; after the Dispatch Gate, rerun without it so the task state is
recorded. `--role review` uses `--reviewer` (or the task's `reviewer:`) and
requires the task already to be `in-review`.

If the script fails or is unavailable, use the manual lookup/command-building
steps below as a fallback, report the error, and preserve the same status,
four-eyes, and no-implicit-spawn rules.

### 1. Parse input
- Extract `<task-id>` (e.g., MVA-001, CT-017)
- Extract `@<agent-id>` (e.g., @claude-sonnet-medium)
- Check `--review` flag

### 2. Lookup agent + spawn pattern
- Read `knowledge/agents/@<agent-id>.md` → get model, effort
- Infer CLI from model name:
  - `claude-*` → **claude** CLI
  - `gemini-*` → **agy** CLI
  - `gpt-*` → **codex** CLI
- Spawn pattern:
  - Use the exact CLI-specific command in `knowledge/guides/spawn-patterns.md`:
    Claude uses `--model` + `-p`, Agy uses `--model` + `--print`, and Codex
    uses `exec -m` + `-c model_reasoning_effort=...`.
- **MCP required:** If repo has no `.mcp.json`, see `knowledge/guides/setup-code-review-graph.md`

### 3. Lookup task + project
- Find task file: `projects/*/tasks/<task-id>-*.md`
- Get `repo_root` from project's `.md` file (PROJECT REGISTRY in index.md)
- Validate the requested transition before any mutation:
  - executor dispatch accepts `status: todo` or `changes-requested`;
  - reviewer dispatch accepts `status: in-review`;
  - otherwise stop and report the invalid state.
- For `--review`, compare the requested reviewer with the task's `executor:`.
  Equality is a hard refusal before the Gate: do not prompt and do not offer a
  mode-based override.

### 4. Dispatch Gate

Read `state/mode.md` now; a missing/invalid value means `supervised`.

- `plan-only`: block without updating the task or spawning a process.
- `supervised`: show the agent, task, role, and command summary; stop for
  explicit confirmation.
- `bypass`: continue immediately and include `auto-approved: dispatch` in the
  dispatch audit entry.

This Gate controls stop/continue only. Once permitted, all task mutation,
logging, and process-spawn steps below are mandatory and run exactly once.

### 5. Construct spawn command

Normally this step is performed by `scripts/ct-dispatch.py`; the LLM still
chooses the agent and supplies the Gate decision. The command is printed for
the coordinator/User to run as a separate CLI process.

```bash
cd <repo_root> && <exact CLI command from knowledge/guides/spawn-patterns.md>
```

Where:
- `<bypass_flag>` = from `knowledge/guides/spawn-patterns.md`
- `<prompt>` depends on role:

**Executor (default):**
```
Execute task at <task_path>
```

**Reviewer (--review):**
```
Review task at <task_path>.
Result ref: <result_ref>. Review sheet: <review_sheet_path>.
1. Read .claude/review-toolchain.md — run each tool in pipeline.
   For each tool: preflight per knowledge/tools/tool-registry.md (health check → install if needed → re-check).
   If a required tool fails preflight after install attempt → BLOCK + escalate, do NOT proceed with partial review.
   /code-review is a baseline tool in the registry, not a fallback that bypasses other tools.
2. Verify each AC item in the review sheet.
3. Report: tool findings + AC results + tests + verdict.
```

### 6. Update task file and audit

For executor dispatch, the script records `status: dispatched`, `executor:`,
`dispatched:`, and `updated:`. For reviewer dispatch, it records `reviewer:`
and `updated:` while preserving `status: in-review`. The LLM remains
responsible for the Gate, `log.md` narrative, and any risk explanation.
- Set `executor:` or `reviewer:` field
- Set `status: dispatched` or `status: in-review`
- Set `dispatched:` or `in_review:` date
- Set `updated:` to today's date.
- Append one `dispatch` entry to `log.md` using `AGENTS-REFERENCE.md` §7. In
  `bypass`, include `auto-approved: dispatch`. Preserve all normal audit details.

### 7. Spawn and output

Run the printed command with Bash only after the User/Gate permits it. This
must be a separate CLI process, never an `Agent()` subagent. After it
starts/completes, print the command and terse status:

```
Spawning @<agent-id> for <task-id>:

  cd /home/lupca/projects/xxx && claude --model claude-sonnet-5 -p "Execute task at /home/.../tasks/XXX-001-slug.md" --dangerously-skip-permissions

Task status → dispatched, executor → @<agent-id>
```

## Terse mode
- No explanations
- Just: command + status update confirmation
