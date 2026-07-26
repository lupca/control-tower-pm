---
title: "Spawn Patterns"
type: guide
tags: [dispatch, cli, agents, control-tower]
updated: 2026-07-24
---

# Spawn Patterns

CLI spawn commands for each tool — ready to copy-paste with placeholders.

## Variables

- `<repo_root>` — from PROJECT REGISTRY in index.md
- `<model>` — from agent roster (`knowledge/agents/@<agent-id>.md`)
- `<task_path>` — absolute path to task file
- `<role>` — "Execute" or "Review"

## Claude Code

```bash
cd <repo_root> && claude --model <model> -p "<role> task at <task_path>" --dangerously-skip-permissions
```

**Models:** claude-sonnet-5, claude-opus-4-5-20251101

## Agy (Antigravity/Gemini)

```bash
cd <repo_root> && agy --agent <model> --effort <effort> --print "<role> task at <task_path>" --dangerously-skip-permissions < /dev/null
```

**Flags:** `--agent` (model name), `--effort` (low/medium/high), `--print` (prompt)
**Models:** gemini-2.5-flash, gemini-2.5-pro, gemini-3.6-flash
**Note:** Always add `< /dev/null` to prevent stdin hang

## Codex (OpenAI)

```bash
cd <repo_root> && codex exec -m <model> -c model_reasoning_effort=<effort> --dangerously-bypass-approvals-and-sandbox "<role> task at <task_path>"
```

Note: prompt is positional argument (at the end), NOT `-p` (that's `--profile`).

**Models:** gpt-5.6-luna, gpt-5.6-sol
**Effort:** low, medium, high (via `-c model_reasoning_effort=<effort>`)
**Tiers:** @gpt-5.6-luna-high = gpt-5.6-luna + effort=high

## Example

Task: `/home/lupca/projects/control-tower/projects/marketing-video-agent/tasks/MVA-001-simplify-architecture.md`
Agent: @gpt-5.6-luna-high
Repo: `/data/projects/marketing-video-agent`

```bash
cd /data/projects/marketing-video-agent && codex exec -m gpt-5.6-luna -c model_reasoning_effort=high --dangerously-bypass-approvals-and-sandbox "Execute task at /home/lupca/projects/control-tower/projects/marketing-video-agent/tasks/MVA-001-simplify-architecture.md"
```
