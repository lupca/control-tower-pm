# /dispatch — Auto spawn CLI executor/reviewer

**Usage:** `/dispatch <task-id> @<agent-id> [--review]`

**Examples:**
- `/dispatch MVA-001 @claude-sonnet-medium` — dispatch executor
- `/dispatch MVA-001 @gpt-5.6-sol --review` — dispatch reviewer

> **CRITICAL:** Use `Bash()` to spawn CLI processes, NOT `Agent()` tool!
> - ✅ `Bash("cd <repo> && claude -p '...'")` — separate process, outside the system
> - ❌ `Agent("Execute task...")` — subagent in same session, still inside control-tower

## Steps

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
  - **claude:** `cd <repo> && claude -m <model> -p "..." --dangerously-skip-permissions`
  - **agy:** `cd <repo> && agy -m <model> -p "..."`
  - **codex:** `cd <repo> && codex exec -m <model> [--reasoning <effort>] --dangerously-bypass-approvals-and-sandbox "..."`
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

```bash
cd <repo_root> && <cli> -m <model> -p "<prompt>" <bypass_flag>
```

Where:
- `<bypass_flag>` = from spawn-patterns.md
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
   If file missing, run /code-review as default.
2. Verify each AC item in the review sheet.
3. Report: tool findings + AC results + tests + verdict.
```

### 6. Update task file and audit
- Set `executor:` or `reviewer:` field
- Set `status: dispatched` or `status: in-review`
- Set `dispatched:` or `in_review:` date
- Set `updated:` to today's date.
- Append one `dispatch` entry to `log.md` using `AGENTS-REFERENCE.md` §7. In
  `bypass`, include `auto-approved: dispatch`. Preserve all normal audit details.

### 7. Spawn and output

Run the constructed command with Bash. This must be a separate CLI process,
never an `Agent()` subagent. After it starts/completes, print the command and
terse status:

```
Spawning @<agent-id> for <task-id>:

cd /home/lupca/projects/xxx && claude -m claude-sonnet-5 -p "Execute task at /home/.../tasks/XXX-001-slug.md" --dangerously-skip-permissions

Task status → dispatched, executor → @<agent-id>
```

## Terse mode
- No explanations
- Just: command + status update confirmation
