---
id: CT-018
title: "Tạo /dispatch skill — auto spawn CLI từ task + agent"
status: done
priority: high
risk: low
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: [CT-017]
files:
  - .claude/skills/dispatch/SKILL.md
predicted_success: high
prediction_factors:
  score: 0.9
  deductions:
    - "new_skill: chưa có template (-0.1)"
created: 2026-07-22
updated: 2026-07-22
---

# CT-018: Tạo /dispatch skill

> Dự án: [[projects/control-tower/control-tower]]

## Bối cảnh

Hiện tại dispatch manual:
1. Đọc agent profile → lấy model
2. Lookup spawn pattern cho CLI
3. Construct command
4. Update task status

Skill `/dispatch` sẽ automate steps 1-4.

## Tiêu chí nghiệm thu (AC)

- [x] AC1: Skill file `.claude/skills/dispatch/SKILL.md` tồn tại
- [x] AC2: Input: `<task-id> @<agent-id>` (e.g., `/dispatch MVA-001 @claude-sonnet-medium`)
- [x] AC3: Output: spawn command ready to run + auto update task status to `dispatched`
- [x] AC4: Skill reads from memory (CT-017) instead of agent files

## Verification

- `cat .claude/skills/dispatch/SKILL.md` → có SKILL.md
- File chứa instructions cho constructing spawn command
- File references memory files từ CT-017

## Plan

### Step 1 — Create skill directory
`.claude/skills/dispatch/`

### Step 2 — Write SKILL.md
- Input parsing: extract task-id và agent-id
- Lookup agent từ memory (agent-roster.md)
- Lookup spawn pattern từ memory (spawn-patterns.md)
- Construct command với: repo_root từ index.md, model từ roster, task path
- Update task status + executor field

### Step 3 — Test với dry-run

## Sub-tasks

- [ ] Create .claude/skills/dispatch/SKILL.md
- [ ] Test skill với example task
