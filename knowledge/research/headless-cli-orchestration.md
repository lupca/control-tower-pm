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

Superseded by §8 (Correct Spawn Pattern) — see §8.1 for the canonical template and §8.3 for a full worked example. The prior version of this section inlined AC/Plan text directly into the prompt, which §8's rationale (¶151) explicitly rules out in favor of pointing at the task file path.

---

## 8. Correct Spawn Pattern

Every spawn MUST pin four things explicitly: **cwd** (`cd <repo_root>`, the *target* repo — not control-tower), **model** (`--model <model>`, resolved via reputation, §8.2), **prompt** (`-p "<task_file_path>"` — the task file's path, never inlined AC/Plan text), and the CLI-specific **bypass** flag. Do NOT rely on the CLI's default model, and do NOT paste AC/Plan into the prompt — pin the model so the executor/reviewer mapping stays deterministic and auditable, and point at the task file so the CLI always reads the current AC/Plan from the one place they're tracked.

### 8.1 Canonical Template

```bash
cd <repo_root> && <cli> --model <model> -p "Execute task at <task_file_path>" <bypass>
```

- `<repo_root>` — absolute path from PROJECT REGISTRY in `index.md` (the *target* project's repo, e.g. `/home/lupca/projects/topvnsport`).
- `<task_file_path>` — **absolute** path to the task file inside the **control-tower** repo, e.g. `/home/lupca/projects/control-tower/projects/topvnsport-pmi/tasks/PMI-042-add-discount-validation.md`. The task file does NOT live in `<repo_root>` — control-tower and the target repo are two different repos, so a relative path would break as soon as the CLI's cwd is the target repo. Never inline AC/Plan into the prompt: the task file is the single source of truth, and inlining lets the dispatched prompt drift from what's recorded there (e.g. after a `/verdict changes` edit adds findings).
- `<model>` — never hardcoded; resolved per §8.2 from `knowledge/agents/*.md` reputation, tiered per §8.4.
- `<bypass>` — CLI-specific permission flag from §1.

### 8.2 Model Selection via Reputation (§12.3)

Do NOT hardcode a CLI→model table. At dispatch time, resolve the model by querying reputation:

1. Derive the task's domain(s) from its `files:` field using the §12.2 auto-detection rules (e.g. `*.py` / `/backend/` → `backend`).
2. Read every `knowledge/agents/@*.md` profile; filter to agents whose `strengths` include a matching domain.
3. Drop/flag any match with `success_rate < 0.6` or a matching `weaknesses` entry (§12.3's low-success/weakness warning) — surface the warning, don't silently dispatch to it.
4. Rank remaining candidates by `success_rate` (tie-break: lower `avg_review_rounds`, then `recent_trend: improving` > `stable` > `declining`).
5. Split by tier (§8.4): pick the top **executor-tier** match to execute, and a **reviewer-tier** match on a *different* CLI (four-eyes, §3) to review.
6. Record the resolved `agent_id` + model in the spawn command and the audit log entry (§4.3).

Re-run this lookup at every dispatch — never cache a fixed table. The roster below is a snapshot of current profiles for illustration only:

| Agent profile | CLI | Model flag | Domains (`strengths`) | Tier (§8.4) |
|---|---|---|---|---|
| `@sonnet-5` | `claude` | `--model claude-sonnet-5` | skills, documentation, process-design | executor |
| `@antigravity` | `agy` | `--model antigravity` | backend, frontend, testing, infra, database | executor |
| `@antigravity-3.6` | `agy` | `--model antigravity-3.6` | frontend, backend, database — `weaknesses: [scope-compliance]`, `success_rate: 0.0` | executor — fails step 3, flag/skip unless scope is unusually tight |
| `@gpt-5.6-luna` | `codex` | `--model gpt-5.6` | backend, frontend, cleanup | executor |
| `@claude-opus` | `claude` | `--model claude-opus-4-8` | code-review, architecture, backend, frontend, database | reviewer |
| `@claude` | `claude` | (review-only profile) | code-review, backend, frontend, infra, testing | reviewer |
| `@dev-tung` | human | n/a | backend, database | either (human) |

### 8.3 Full Example — cwd + task file path + reputation-recommended model

Task `PMI-042` touches `PMI/backend/schemas/discount.py` + `PMI/backend/tests/test_discount.py` → §12.2 domain = `backend` + `testing`. Reputation lookup (§8.2): `@antigravity` (backend/frontend/testing/infra/database, 100% success) and `@gpt-5.6-luna` (backend/frontend/cleanup, 100% success) both match; `@antigravity` ranks first on `recent_trend` (§8.2 step 4 tie-break), so it's the executor. The reviewer must be a different CLI and reviewer-tier: `@claude-opus` (code-review, architecture, backend) fits — its `total_tasks_executed: 0` doesn't disqualify it, since reviewer-tier is picked for thoroughness, not `success_rate` (§8.4).

Executor (`@antigravity` via `agy`, reputation-recommended, cwd = target repo):

```bash
cd /home/lupca/projects/topvnsport && agy --model antigravity -p "Execute task at /home/lupca/projects/control-tower/projects/topvnsport-pmi/tasks/PMI-042-add-discount-validation.md" --dangerously-skip-permissions --output-format json --json-schema '{"type":"object","properties":{"branch":{"type":"string"},"commit_sha":{"type":"string"},"summary":{"type":"string"}},"required":["branch","commit_sha","summary"]}'
```

Reviewer (`@claude-opus` via `claude`, different CLI → four-eyes holds):

```bash
cd /home/lupca/projects/topvnsport && claude --model claude-opus-4-8 -p "Review task at /home/lupca/projects/control-tower/projects/topvnsport-pmi/tasks/PMI-042-add-discount-validation.md — verify AC, run tests, return pass/fail + findings" --dangerously-skip-permissions --output-format json
```

### 8.4 Tiering Rule: Executor (cheap) vs Reviewer (expensive)

- **Executor tier** — optimized for cost/throughput: cheap, fast models with a proven high `success_rate` on the matching domain (`@sonnet-5`, `@antigravity`, `@gpt-5.6-luna`). Pick the cheapest model that clears the success-rate bar in §8.2 step 3 — don't default to the most expensive model just because it's available.
- **Reviewer tier** — optimized for thoroughness, not cost: models chosen for depth of review even at higher per-call cost (`@claude-opus`, `@claude`). A reviewer profile with `total_tasks_executed: 0` is expected — these agents are dispatched review-only, and their value is bugs caught (e.g. `@claude-opus` catching the scope mismatch + OMS bug on WEB-001), not raw `success_rate`.
- Executor and reviewer must never resolve to the same `agent_id`, and should run on different CLIs (§3 four-eyes).

---

## 7. Verification Checklist

- [x] AC1: ADR-003 written — Model A opt-in, Model B default
- [x] AC2: Headless commands documented for claude/agy/codex/copilot
- [x] AC3: Four-eyes via different CLI (executor ≠ reviewer)
- [x] AC4: Gates mandatory, no-auto-commit, audit logging
- [x] AC5: Integration with CT-002/CT-007/CT-009, future changes listed
