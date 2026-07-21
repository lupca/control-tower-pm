---
id: CT-002
title: "Reputation System — Track executor/reviewer performance"
status: dispatched
priority: high
risk: normal
deadline: null
executor: "@antigravity"
reviewer: null
result_ref: null
depends_on: []
files:
  - .claude/skills/verdict/SKILL.md
  - .claude/skills/pm/SKILL.md
  - log.md
  - AGENTS.md
flows: [verdict, dispatch]
tests: []
dispatched: 2026-07-22
in_review: null
created: 2026-07-22
updated: 2026-07-22
tier: 1
paradigm_source: "ERC-8004 AI Reputation Standard (Aug 2025)"
---

# CT-002: Reputation System — Track executor/reviewer performance

> Dự án: [[projects/control-tower/control-tower]]

## Bối cảnh (Context)

Hiện tại: `executor:` và `reviewer:` chỉ là labels — không track performance history.

Research: "Without accountability mechanisms, multi-agent cooperation falls below 20%" (tragedy of the commons). ERC-8004 là first blockchain-based standard cho AI agent reputation.

## Tiêu chí nghiệm thu (AC)

- [ ] AC1: Tạo `knowledge/agents/` directory với profile file cho mỗi executor/reviewer
- [ ] AC2: Profile format:
  ```yaml
  agent_id: "@antigravity"
  type: ai  # ai | human
  total_tasks_executed: 47
  total_tasks_reviewed: 12
  success_rate: 0.91  # tasks passed on first review
  avg_review_rounds: 1.3
  strengths: [backend, database, testing]  # auto-detected từ file patterns
  recent_trend: improving | stable | declining
  last_active: 2026-07-22
  ```
- [ ] AC3: `/verdict` auto-updates profile sau mỗi verdict:
  - `pass` first time → success_rate up
  - `changes` → success_rate down, increment review_rounds
- [ ] AC4: `/pm` suggests executor based on task's `files:` matching agent strengths
- [ ] AC5: Warning nếu assign task to agent với low success_rate trong domain đó

## Plan

### Phase 1: Schema & Directory
1. Tạo `knowledge/agents/` directory
2. AGENTS.md §12 — định nghĩa Agent Profile schema:
   ```yaml
   agent_id: "@antigravity"
   type: ai                    # ai | human
   total_tasks_executed: 0
   total_tasks_reviewed: 0
   success_rate: 1.0           # (pass on first review) / total_executed
   avg_review_rounds: 1.0
   strengths: []               # backend, frontend, database, testing, infra
   weaknesses: []
   recent_trend: stable        # improving | stable | declining
   last_active: null
   ```

### Phase 2: Strength Detection Logic
3. Strength mapping rules:
   - `*.py, /backend/` → backend
   - `*.tsx, *.vue, /web/` → frontend  
   - `*models.py, migrations/` → database
   - `*test*.py, /tests/` → testing
   - `docker*, .github/` → infra

### Phase 3: Verdict Integration
4. verdict/SKILL.md — sau mỗi verdict:
   - Read profile từ `knowledge/agents/@<executor>.md`
   - Update success_rate, avg_review_rounds, strengths, trend, last_active
   - Write profile back

### Phase 4: PM Integration  
5. pm/SKILL.md — khi dispatch:
   - Scan task's files → detect required strengths
   - Rank agents by matching strengths + success_rate
   - Suggest executor + warning nếu low success_rate

### Phase 5: Bootstrap & Index
6. Parse log.md để seed initial profiles
7. Update `knowledge/_index.md`

## Sub-tasks

- [ ] Tạo `knowledge/agents/` directory structure
- [ ] Define agent profile YAML schema trong AGENTS.md (new §12)
- [ ] Update `/verdict` skill to update profiles
- [ ] Parse log.md để bootstrap profiles từ historical data
- [ ] Add strength auto-detection (backend if touches .py, frontend if .tsx, etc.)
- [ ] Update `/pm` dispatch suggestions

## Research References

- [ERC-8004 AI Reputation Standard](https://rnwy.com/blog/ai-reputation-systems)
- [Game-Theoretic Lens on LLM-based MAS (2025)](https://arxiv.org/pdf/2601.15047)
- RepuNet finding: cooperation collapses without accountability
