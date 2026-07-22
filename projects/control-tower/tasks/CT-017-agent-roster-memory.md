---
id: CT-017
title: "Save agent roster + spawn patterns vào memory"
status: done
priority: high
risk: low
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: []
files:
  - knowledge/agents/*.md
  - .claude/memory/MEMORY.md
predicted_success: high
prediction_factors:
  score: 0.95
  deductions: []
created: 2026-07-22
updated: 2026-07-22
---

# CT-017: Save agent roster + spawn patterns vào memory

> Dự án: [[projects/control-tower/control-tower]]

## Bối cảnh

Mỗi lần dispatch, coordinator phải đọc nhiều file để biết:
- Agent nào available, model/effort gì
- Spawn command format cho từng CLI (claude, agy, codex)

Dẫn đến: chậm, tốn token, dễ quên (như MVA-001 session không biết spawn).

## Tiêu chí nghiệm thu (AC)

- [x] AC1: Memory file `agent-roster.md` chứa table: agent_id, type (executor/reviewer), model, CLI, spawn command template
- [x] AC2: Memory file `spawn-patterns.md` chứa spawn command cho từng CLI với bypass flags
- [x] AC3: MEMORY.md index updated với 2 files trên
- [x] AC4: Coordinator có thể lookup từ memory thay vì đọc `knowledge/agents/*.md`

## Verification

- `cat .claude/memory/agent-roster.md` → có table với ít nhất 6 agents
- `cat .claude/memory/spawn-patterns.md` → có 3 CLI patterns (claude, agy, codex)
- `grep "agent-roster" .claude/memory/MEMORY.md` → found

## Plan

### Step 1 — Tạo agent-roster.md
Table format với columns: agent_id, tier (executor/reviewer), model, strengths.

### Step 2 — Tạo spawn-patterns.md
Template cho mỗi CLI:
- claude: `cd <repo> && claude -m <model> -p "..." --dangerously-skip-permissions`
- agy: `cd <repo> && agy -m <model> -p "..."`
- codex: `cd <repo> && codex exec -m <model> -p "..." --dangerously-bypass-approvals-and-sandbox`

### Step 3 — Update MEMORY.md index

## Sub-tasks

- [x] Tạo agent-roster.md
- [x] Tạo spawn-patterns.md
- [x] Update MEMORY.md
