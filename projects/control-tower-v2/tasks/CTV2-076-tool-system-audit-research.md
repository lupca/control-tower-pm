---
id: CTV2-076
title: "Research: Tool System Audit & Unified Design Strategy"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: high
risk: normal
deadline: null
executor: "@claude-opus"
reviewer: null
result_ref: null
depends_on: []
files:
  - backend/app/services/tool_definitions.py
  - backend/app/services/command_router.py
  - backend/app/api/tasks.py
  - backend/app/api/chat.py
  - backend/app/prompts/global_context.md
flows: []
tests: []
dispatched: 2026-07-27
in_review: null
predicted_success: high
prediction_factors:
  score: 0.9
  deductions:
    - "research task, no code changes (-0.0)"
    - "no existing tests (-0.1)"
created: 2026-07-27
updated: 2026-07-27
---

# CTV2-076: Research: Tool System Audit & Unified Design Strategy

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Tiêu chí nghiệm thu (AC)

- [ ] Complete audit of all tools in the system (tool_definitions.py, command_router.py, API endpoints, MCP)
- [ ] Document how CLI mode handles slash commands and where it gets tool info
- [ ] Document what tools the chat UI shows to users
- [ ] Propose unified tool architecture with single source of truth
- [ ] Research doc created at `docs/research/tool-system-architecture.md`

## Verification

- `ls docs/research/tool-system-architecture.md` → file exists
- Research doc contains: Tool Audit section, CLI Analysis section, Architecture Proposal section

## Context

Current state (scattered tools):
- **API mode**: `tool_definitions.py` has EAGER_TOOLS (pm_create_task, get_status) and DEFERRED_TOOLS (dispatch_task, record_verdict, approve_gate, cancel_task, compact_context)
- **CLI mode**: agy/claude have built-in tools (Bash, Read, Write) + can call APIs directly
- **Slash commands**: `/pm`, `/status`, `/dispatch` go through `command_router.py`
- **No single source of truth** for tool definitions

Key questions:
1. What tools exist where?
2. How does CLI handle `/pm`? Where does it get tool schema?
3. How to unify API mode tools and CLI mode capabilities?
4. Should we use MCP server for Control Tower tools?

## Plan

1. Audit `tool_definitions.py` - list EAGER_TOOLS and DEFERRED_TOOLS
2. Audit `command_router.py` - list all handlers and their mappings
3. Audit `backend/app/api/*.py` - list all endpoints that could be tools
4. Check MCP config and any MCP tools
5. Trace CLI slash command flow - how does agy/claude handle `/pm`?
6. Document chat UI tool display
7. Design unified architecture proposal:
   - Single source of truth (tools.md or tools.yaml?)
   - How to expose to API mode (auto-generate tool_definitions.py?)
   - How to expose to CLI mode (include in system prompt?)
   - MCP server consideration
8. Write research doc

## Sub-tasks

- [ ] Audit all tool locations
- [ ] Trace CLI slash command handling
- [ ] Design unified tool architecture
- [ ] Write research doc
