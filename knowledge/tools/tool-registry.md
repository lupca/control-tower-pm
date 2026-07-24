# Tool Registry

Source of truth for all tools used by control-tower skills. Skills read this registry dynamically by `used_by` — adding a new tool requires only a new entry here, no skill edits needed.

---

## Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique tool identifier |
| `scope` | `control-tower` \| `target-repo` \| `both` | Where the tool must be available |
| `applies_to` | string | Condition/projects when this tool applies |
| `health_check` | string | Command/MCP call to verify tool availability |
| `install` | string | How to install/fix if health check fails |
| `required` | `hard` \| `soft` | `hard` = BLOCK on failure; `soft` = skip with log |
| `used_by` | string[] | Skills/steps that use this tool |
| `fallback` | `none` \| string | `none` for hard-required; alternative for soft |

---

## Tools

### code-review-graph

| Field | Value |
|-------|-------|
| **id** | `code-review-graph` |
| **scope** | `control-tower` |
| **applies_to** | Repos with `Graph build ✅` in PROJECT REGISTRY (`index.md` §2) |
| **health_check** | MCP: `list_repos_tool()` or `list_graph_stats_tool(repo_root=<absolute>)` — returns without error |
| **install** | Follow `knowledge/guides/setup-code-review-graph.md`: (1) ensure venv exists at `~/.local/share/code-review-graph-venv/`, (2) verify `.mcp.json` in control-tower, (3) if graph missing/stale run `build_or_update_graph_tool(repo_root=<absolute>)` |
| **required** | `hard` |
| **used_by** | `pm` (graph queries: steps 1-8 in `AGENTS-REFERENCE.md` §6.1), `review-order` (step 5 enrichment) |
| **fallback** | `none` |

**Preflight behavior:** If `list_graph_stats_tool(repo_root)` fails or returns empty → attempt install steps → re-check → still fail → **BLOCK gate + escalate** with command + output shown. Never fabricate `files:`/`tests:`/`flows:` manually.

---

### ocr

| Field | Value |
|-------|-------|
| **id** | `ocr` |
| **scope** | `target-repo` |
| **applies_to** | All repos (pre-scan optional; review toolchain when declared) |
| **health_check** | `cd <repo_root> && ocr --version` — exits 0 |
| **install** | Download binary from https://github.com/alibaba/open-code-review/releases or `npm install -g @alibaba-group/ocr-linux-x64` (Linux) / `@alibaba-group/ocr-darwin-x64` (macOS) |
| **required** | `soft` for `/pm` pre-scan (step 8.5); `hard` when declared in repo's `.claude/review-toolchain.md` |
| **used_by** | `pm` (pre-scan step 8.5), `review` (toolchain) |
| **fallback** | `none` |

**Preflight behavior:** Run `ocr --version` in target repo → fail → attempt install → re-check → still fail:
- `/pm` pre-scan (soft): **skip with log** ("OCR not available, pre-scan skipped — findings may be missed")
- Review toolchain (hard): **BLOCK + escalate** ("OCR required by toolchain but install failed: <output>")

---

### /code-review (baseline)

| Field | Value |
|-------|-------|
| **id** | `code-review` |
| **scope** | `target-repo` |
| **applies_to** | All repos with Claude Code CLI available |
| **health_check** | `which claude` — exits 0, or `claude --version` |
| **install** | See Anthropic docs; typically pre-installed when Claude Code is the executor |
| **required** | `hard` (baseline for all reviews) |
| **used_by** | `review` (baseline tool in any toolchain) |
| **fallback** | `none` |

**Note:** `/code-review` is a **baseline tool in the registry**, not an escape hatch to bypass other tools. Every toolchain runs it alongside (not instead of) declared tools.

---

## Adding a new tool

1. Add a new `### <tool-name>` section with the fields above.
2. Fill in `used_by` to list which skills/steps use it.
3. Done — skills read the registry by `used_by` and apply preflight automatically.

**No skill code changes required.** The preflight algorithm (`AGENTS-REFERENCE.md` §8) reads this registry and enforces it generically.

Example for a new linter:

```markdown
### eslint

| Field | Value |
|-------|-------|
| **id** | `eslint` |
| **scope** | `target-repo` |
| **applies_to** | JS/TS repos (detected by `package.json` containing `eslint`) |
| **health_check** | `cd <repo_root> && npx eslint --version` |
| **install** | `npm install eslint` or `pnpm add eslint` |
| **required** | `soft` |
| **used_by** | `review` (toolchain) |
| **fallback** | `none` |
```

---

## Registry maintenance

- Update `install` commands when tools change their install process.
- Move `required` from `soft` to `hard` if experience shows silent skips cause quality issues.
- Archive deprecated tools to an `## Archived` section rather than deleting (preserves audit trail).
