# Headless CLI Orchestration — Design Doc

**Task:** CT-012  
**Date:** 2026-07-22  
**Status:** Complete

---

## 1. CLI Headless Commands (AC2)

| CLI | Headless Command | Bypass Permissions | Structured Output |
|-----|------------------|-------------------|-------------------|
| `claude` | `claude -p "<prompt>"` | `--dangerously-skip-permissions` or `--allowedTools "Read,Edit,Bash(git *)"` | `--output-format json --json-schema '<schema>'` |
| `agy` | `agy -p "<prompt>"` | `--dangerously-skip-permissions` | Text only; parse stdout or run `git rev-parse HEAD` after |
| `codex` | `codex exec "<prompt>"` | `--sandbox workspace-write --ask-for-approval never` | `--json` (JSONL stream) or `--output-schema` |
| `gh copilot` | `gh copilot -p "<prompt>"` | `--allow-all-tools` or `--allow-tool <tool>` | Text only; parse stdout or `gh pr list` after |

### Spawn Pattern

```bash
cd <repo_root> && <cli> <headless-flags> "<AC + Plan prompt>"
```

`repo_root` is looked up from PROJECT REGISTRY in `index.md`.

---

## 2. Result Extraction (result_ref)

**Two-layer strategy:**

1. **Native JSON (claude, codex):** Define schema requiring `branch`, `commit_sha`, `pr_url` fields. Extract with `jq`.

2. **Fallback (agy, copilot, or JSON missing):** After exit code 0:
   ```bash
   git rev-parse HEAD          # commit hash
   git branch --show-current   # branch name
   gh pr list --head $(git branch --show-current) --json url -q '.[0].url'  # PR URL
   ```

---

## 3. Four-Eyes Enforcement (AC3)

**Rule:** Executor CLI ≠ Reviewer CLI.

Example mapping:
| Executor | Reviewer |
|----------|----------|
| `claude` | `agy` |
| `agy` | `codex` |
| `codex` | `claude` |
| `gh copilot` | `claude` |

Control-tower records:
- `executor: @claude-cli` (or `@agy-cli`, etc.)
- `reviewer: @codex-cli` (different from executor)

`/verdict pass` refuses if `reviewer == executor`.

---

## 4. Safety Boundaries (AC4)

### 4.1 Gates Still Mandatory

Spawn executor ONLY after:
1. Spec Gate approved (AC written)
2. Plan Gate approved (`## Plan` filled)
3. `status: dispatched` recorded

### 4.2 No Auto-Commit/Auto-Merge

- Executor may create commits/branches
- Executor must NOT push to protected branches or merge PRs
- Use `--allowedTools "Bash(git add *),Bash(git commit *)"` but NOT `Bash(git push *)` or `Bash(git merge *)`
- Human confirms `/verdict pass` → then manually merges

### 4.3 Audit Every Spawn

Each spawn logs to `log.md`:
```markdown
## [YYYY-MM-DD HH:MM:SS] spawn | <task-id> executor=@<cli> repo=<repo_root>
## [YYYY-MM-DD HH:MM:SS] spawn | <task-id> reviewer=@<cli> repo=<repo_root>
```

---

## 5. Integration Points (AC5)

### Reputation (CT-002)
- Track success/failure per CLI-agent
- Prefer higher-reputation CLI for complex tasks

### Goal-Conditioned Autonomy (CT-007)
- Model A fits "high autonomy" goal setting
- Human sets goal (AC), agent executes to completion

### Auto-Remediation TNR (CT-009)
- §19.2 no-auto-commit applies: executor creates commit, but merge is human-gated

### Required Changes (future tasks)
- `AGENTS.md §1`: Add Model A row to roles table
- `CLAUDE.md`: Document Model A as opt-in
- New skill: `/spawn-executor`, `/spawn-reviewer` (or integrate into existing macros)

---

## 6. Example Spawn Commands

### Claude as Executor
```bash
cd /home/lupca/projects/topvnsport && claude -p "$(cat <<'EOF'
Task: PMI-042 - Add discount validation

AC:
- [ ] validate discount percentage 0-100
- [ ] validate discount dates (start < end)

Plan:
1. Edit PMI/backend/schemas/discount.py
2. Add tests to PMI/backend/tests/test_discount.py
3. Run pytest

Return JSON: {"branch": "...", "commit_sha": "...", "summary": "..."}
EOF
)" --dangerously-skip-permissions --output-format json --json-schema '{"type":"object","properties":{"branch":{"type":"string"},"commit_sha":{"type":"string"},"summary":{"type":"string"}},"required":["branch","commit_sha","summary"]}'
```

### Codex as Reviewer
```bash
cd /home/lupca/projects/topvnsport && codex exec "$(cat <<'EOF'
Review task PMI-042 - Add discount validation

Check:
- [ ] AC1: discount 0-100 validated
- [ ] AC2: date validation (start < end)
- [ ] Tests pass

Run: pytest PMI/backend/tests/test_discount.py

Return JSON: {"pass": true/false, "findings": ["..."]}
EOF
)" --sandbox workspace-write --ask-for-approval never --json
```

---

## 7. Verification Checklist

- [x] AC1: ADR-003 written — Model A opt-in, Model B default
- [x] AC2: Headless commands documented for claude/agy/codex/copilot
- [x] AC3: Four-eyes via different CLI (executor ≠ reviewer)
- [x] AC4: Gates mandatory, no-auto-commit, audit logging
- [x] AC5: Integration with CT-002/CT-007/CT-009, future changes listed
