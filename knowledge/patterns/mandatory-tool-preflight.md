---
pattern_id: mandatory-tool-preflight
category: process
severity: high
created: 2026-07-24
updated: 2026-07-24
---

# mandatory-tool-preflight

## Problem Signature
A workflow depends on an external tool (static analyzer, linter, knowledge graph, OCR, validator, formatter…) but treats it as **optional**: when the tool is missing, broken, or its CLI/MCP can't be called, the step **silently falls back to a manual/best-effort path**. The degraded output is indistinguishable from tool-produced output, so quality drops with **no signal and no auto-remediation** — nobody notices until much later.

## Detection
- Skill/docs contain fallback phrasing for a quality-critical tool: *"skip silently"*, *"if not found → skip"*, *"fall back to manual"*, *"use X as the default"*.
- No health-check runs before the tool is used, and there's no install/repair path — tool absence just routes around the tool.
- Tool identity is **hardcoded across many call sites**, so enforcing or adding a tool means editing every site (no single source of truth) → enforcement never happens uniformly.

## Solution Template
Split **declaration** from **enforcement**:
1. **Declarative registry** (single source of truth) — one entry per tool with `scope` (where it runs), `applies_to`, `health_check`, `install`, `required` (`hard` | `soft`), `used_by`, `fallback` (`none` for hard).
2. **Mandatory Preflight gate** before any tool-using step: `health_check` → on fail run `install` (on the correct scope: coordinator system or target repo) → re-check → if a `hard` tool still fails, **BLOCK + escalate** with the failing command + install output (never a silent manual fallback). A `soft` tool may skip **only with an explicit log** — never silently.
3. Skills read the registry **generically by `used_by`**, never hardcoding tool names — so both enforcement and extensibility come from **one declaration line**, not per-site edits. Adding a new tool = adding one registry row.

Baseline tools (e.g. a default reviewer/linter) live **in** the registry as regular entries, not as an escape hatch that bypasses the others.

## Past Instances
- [[CT-025-mandatory-tool-registry-preflight]] (control-tower, 2026-07-24) — code-review-graph/OCR could silently fall back to manual in `/pm`, `/dispatch`, `/review-order` and the review-toolchain guide. Fixed with `knowledge/tools/tool-registry.md` (declarative source of truth) + AGENTS-REFERENCE §8 Tool Preflight; skills rewired to match on `used_by`. See [[ADR-009-mandatory-toolchain-registry]].
