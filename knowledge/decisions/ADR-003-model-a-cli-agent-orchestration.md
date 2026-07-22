# ADR-003: Model A — CLI Agent Orchestration (Opt-in)

**Status:** Accepted  
**Date:** 2026-07-22  
**Deciders:** @lupca  
**Task:** CT-012

---

## Context

**Model B (current default):** control-tower only PLANs + COORDINATEs. It NEVER writes code, NEVER reads diffs, NEVER runs tests. EXECUTE and REVIEW happen **outside the system** — a human or another AI in the target repo, independent of control-tower.

This works, but requires manual handoff: human must copy the task spec, run the executor, copy result_ref back, run the reviewer, record verdict. Every handoff = context switch + token overhead.

**Model A (proposed):** control-tower **actively orchestrates** EXECUTE and REVIEW by spawning headless CLI agents (`claude`, `agy`, `codex`, `gh copilot`) in the target repo's `repo_root`. Control-tower still doesn't write code itself — it delegates to specialized agents.

## Decision

**Model A is opt-in, parallel to Model B. Model B remains the default.**

Key invariants preserved:
1. **Four-eyes (AGENTS.md §1):** `reviewer:` ≠ `executor:` — enforced by spawning different CLIs
2. **Two Gates (AGENTS.md §4):** Spec Gate + Plan Gate still mandatory before spawning executor
3. **No auto-commit/auto-merge:** Human confirms `/verdict pass` to close tasks
4. **Audit:** Every spawn logged to `log.md` (§7)

### When to use Model A vs Model B

| Scenario | Model |
|----------|-------|
| Human executor (contractor, team member) | B |
| Testing automated flow | A |
| High-volume mechanical tasks | A |
| Sensitive/production code | B (human review) |
| Meta-project (control-tower itself) | A (opt-in for dogfooding) |

## Consequences

**Positive:**
- Reduced token cost: executor/reviewer run in separate headless context, not bloating planner's context
- Faster iteration: no manual copy-paste handoff
- Reproducible: CLI commands are deterministic (same prompt → re-runnable)

**Negative:**
- Requires CLI setup: `claude`, `agy`, `codex`, `gh copilot` must be installed and authenticated
- Permission risk: headless mode bypasses interactive confirmations — must sandbox or use `--allowedTools`
- Debugging complexity: if agent fails silently, need to check stdout/exit code

## Implementation Notes

See `knowledge/research/headless-cli-orchestration.md` for detailed CLI comparison and spawn commands.
