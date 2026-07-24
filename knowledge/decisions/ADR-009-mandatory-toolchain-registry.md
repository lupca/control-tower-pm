# ADR-009: Mandatory Toolchain Registry + Tool Preflight

**Status:** Accepted  
**Date:** 2026-07-24  
**Related:** CT-025, CT-023 (toolchain integration)

---

## Context

`code-review-graph` and `ocr` are core tools in control-tower's flow:
- **PLAN phase**: graph provides `files:`/`tests:`/`flows:` for tasks
- **REVIEW phase**: OCR + toolchain runs static analysis before AC verification

Current behavior when tools are unavailable (not installed, MCP down, CLI fails):
- `pm/task-creation.md` step 8.5: "skip silently" when `ocr` not found
- `dispatch/SKILL.md` step 5: "If file missing, run /code-review as default"
- `review-toolchain.md`: "no toolchain → use /code-review as the default"

**Problem:** Silent fallback to manual work degrades quality:
- Missing graph data → executor guesses files, misses blast radius
- Skipped OCR → bugs reach review that could have been caught
- Defaulting to `/code-review` only → repo-specific tools (custom linters, analyzers) never run

**Extensibility problem:** Adding a new tool requires editing multiple skill files — no single source of truth.

---

## Decision

1. **Centralized Tool Registry** (`knowledge/tools/tool-registry.md`)
   - Single source of truth for all tools: id, scope, health_check, install, required, used_by
   - Skills read the registry dynamically by `used_by` field
   - Adding a tool = adding one row; no skill edits needed

2. **Mandatory Preflight Algorithm** (`AGENTS-REFERENCE.md` §8)
   - Before any step that uses a tool: run `health_check`
   - If fail: run `install` (respecting `scope`: control-tower vs target-repo)
   - Re-check: if still fail and `required: hard` → **BLOCK gate + escalate to user**
   - `required: soft` → skip **with explicit log** (never silent)
   - **No silent manual fallback ever**

3. **Rewire existing silent-fallback points**
   - `task-creation.md` step 8.5: preflight OCR, block/log instead of "skip silently"
   - `dispatch/SKILL.md`: reviewer runs preflight per registry, no "/code-review as default" escape
   - `review-toolchain.md`: every repo must declare toolchain; tools installed per registry; `/code-review` is baseline tool in registry, not escape hatch

---

## Consequences

**Positive:**
- Tool failures surface immediately, not silently degrade output
- Reviewers/executors get guidance on how to install missing tools
- New tools added via registry declaration only — consistent, auditable
- `/code-review` remains available but as a registered baseline, not a bypass

**Negative:**
- Extra friction when tools genuinely can't be installed (rare edge case)
- Requires user intervention to unblock when install fails
- Slightly longer preflight before steps that use tools

**Mitigations:**
- `soft` required level for optional scans (pm pre-scan) allows logging + skip
- Clear escalation message includes exact command that failed + install output tried
- User can add `# preflight-override: skip <tool-id>` in task body for known edge cases (audit trail)

---

## Alternatives Considered

### A. Keep silent fallback, improve logging only
Rejected: logging helps debugging but doesn't prevent quality degradation. The executor/reviewer still proceeds without the tool's findings.

### B. Hardcode tool checks in each skill
Rejected: each new tool requires editing multiple skills. Not extensible, prone to drift.

### C. Make all tools `soft` and rely on review to catch gaps
Rejected: shifts burden to review phase, where catching issues is more expensive. Better to fail fast.

---

## Migration

1. CT-023 toolchain guide now references registry for install commands
2. Existing repos with `.claude/review-toolchain.md` continue working — registry adds preflight before running tools, doesn't change which tools to run
3. New repos should declare toolchain upfront; registry provides install guidance
