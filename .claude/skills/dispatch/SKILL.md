# /dispatch — Auto spawn CLI executor/reviewer

**Usage:** `/dispatch <task-id> @<agent-id> [--review]`

**Examples:**
- `/dispatch MVA-001 @claude-sonnet-medium` — dispatch executor
- `/dispatch MVA-001 @gpt-5.6-sol --review` — dispatch reviewer

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
  - **codex:** `cd <repo> && codex exec -m <model> [--reasoning <effort>] --mcp-config .mcp.json --dangerously-bypass-approvals-and-sandbox "..."`
- **MCP required:** If repo has no `.mcp.json`, see `knowledge/guides/setup-code-review-graph.md`

### 3. Lookup task + project
- Find task file: `projects/*/tasks/<task-id>-*.md`
- Get `repo_root` from project's `.md` file (PROJECT REGISTRY in index.md)

### 4. Construct spawn command

```bash
cd <repo_root> && <cli> -m <model> -p "<role> task at <task_path>" <bypass_flag>
```

Where:
- `<role>` = "Execute" (default) or "Review" (if --review)
- `<bypass_flag>` = from spawn-patterns.md

### 5. Update task file
- Set `executor:` or `reviewer:` field
- Set `status: dispatched` or `status: in-review`
- Set `dispatched:` or `in_review:` date

### 6. Output
Print the ready-to-run command:

```
Spawning @<agent-id> for <task-id>:

cd /home/lupca/projects/xxx && claude -m claude-sonnet-5 -p "Execute task at /home/.../tasks/XXX-001-slug.md" --dangerously-skip-permissions

Task status → dispatched, executor → @<agent-id>
```

## Terse mode
- No explanations
- Just: command + status update confirmation
