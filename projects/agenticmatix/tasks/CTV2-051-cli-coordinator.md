---
id: CTV2-051
title: "Refactor Coordinator to CLI Dispatch"
status: done
dispatched: 2026-07-26
result_ref: "27ea213"
priority: high
risk: normal
deadline: 2026-08-02
executor: "@gpt-5.6-luna-high"
reviewer: "@claude-opus"
in_review: 2026-07-26
files:
  - backend/app/services/coordinator.py
  - backend/app/services/cli_dispatcher.py
  - backend/app/api/chat.py
  - backend/app/db/models.py
tests:
  - test_cli_coordinator.py
created: 2026-07-26
effort: 4h
updated: 2026-07-26
plan_approved: 2026-07-26
---

# CTV2-051: Refactor Coordinator to CLI Dispatch

## Context

CTV2-050 implemented SDK-direct coordinator with Anthropic/Google adapters. However:
- SDK requires API key (separate billing)
- User has Claude Max + Google AI Pro subscriptions
- CLI tools (`claude`, `agy`) can use account login (no API key)

## Objective

Refactor coordinator to spawn CLI instead of SDK calls, while keeping session continuity via PostgreSQL.

## Architecture

```
User message
    ↓
CoordinatorService.chat()
    ↓
Load session history from PostgreSQL
    ↓
Format history + new message as prompt
    ↓
CLIDispatcher.spawn("claude", prompt)  # Uses account login
    ↓
Parse response
    ↓
Save assistant message to PostgreSQL
    ↓
Return to user (SSE stream)
```

## Deliverables

1. **CLIDispatcher** (`backend/app/services/cli_dispatcher.py`)
   - Spawn `claude`/`agy`/`codex` CLI
   - Stream output via SSE
   - Handle timeout/cancellation
   - Similar to `agent_runner.py` but for coordinator

2. **Refactor CoordinatorService** (`backend/app/services/coordinator.py`)
   - Replace SDK adapter calls with CLI dispatch
   - Keep session history loading from PostgreSQL
   - Format messages as prompt string for CLI
   - Parse CLI output back to message format

3. **Prompt formatting**
   - Convert message history to readable prompt
   - Include system prompt
   - Handle tool calls/results if any

4. **Session continuity**
   - Session ID preserved in PostgreSQL
   - Each CLI spawn loads full history
   - No reliance on CLI's internal session

## CLI Commands

```bash
# Claude (uses account login)
claude --model claude-sonnet-4-20250514 -p "<formatted_prompt>"

# Gemini (uses account login)  
agy --agent gemini-2.5-pro --print "<formatted_prompt>"
```

## AC

- [ ] AC1: CLIDispatcher spawns CLI with formatted prompt
- [ ] AC2: Session history loaded from PostgreSQL before each spawn
- [ ] AC3: CLI output parsed and saved back to PostgreSQL
- [ ] AC4: SSE streaming works with CLI output
- [ ] AC5: Model switching works (claude ↔ agy)
- [ ] AC6: No API key required (uses account login)
- [ ] AC7: Session ID preserved across CLI spawns
- [ ] AC8: Tests verify session continuity

## Plan

1. **Create `cli_dispatcher.py`** (~80 lines)
   - `CLIDispatcher` class with `spawn(cli, model, prompt)` method
   - Reuse `ProcessManager` for subprocess lifecycle
   - Build CLI command: `claude -p "<prompt>"` or `agy --print "<prompt>"`
   - Return async iterator for SSE streaming
   - Handle timeout/cancellation via `ProcessManager`

2. **Add prompt formatter** (in `cli_dispatcher.py` or separate)
   - `format_history_as_prompt(messages: list[dict]) -> str`
   - Include system message as preamble
   - Format user/assistant turns as conversation
   - Handle tool calls/results if present

3. **Refactor `CoordinatorService`**
   - Replace `ProviderRouter`/adapters with `CLIDispatcher`
   - In `complete_turn()`: format canonical messages → spawn CLI → parse output
   - In `stream_turn()`: same but yield chunks from CLI stdout
   - Keep session history loading unchanged (PostgreSQL)
   - Keep `_persist_success`/`_persist_failure` unchanged

4. **Model routing**
   - `claude` in model name → spawn `claude` CLI
   - `gemini` in model name → spawn `agy` CLI
   - Keep `selected_model`/`selected_provider` in session for continuity

5. **Tests** (`test_cli_coordinator.py`)
   - Mock `ProcessManager.run_with_streaming`
   - Test prompt formatting with multi-turn history
   - Test model switching (claude ↔ gemini)
   - Test session continuity across spawns
