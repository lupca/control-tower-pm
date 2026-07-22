---
id: CT-016
title: "Coordinator terse mode: giảm output token, batch confirmations"
status: done
priority: high
risk: low
deadline: null
executor: "@gpt-5.6-luna"
reviewer: "@gpt-5.6-sol"
result_ref: null
depends_on: [CT-014, CT-015]
files:
  - CLAUDE.md
  - .claude/skills/pm/SKILL.md
  - .claude/skills/verdict/SKILL.md
dispatched: 2026-07-22
in_review: null
predicted_success: high
prediction_factors:
  score: 0.9
  deductions:
    - "blast_radius: 3 files (-0.0)"
confidence_interval: [0.8, 0.95]
created: 2026-07-22
updated: 2026-07-22
---

# CT-016: Coordinator terse mode

> Dự án: [[projects/control-tower/control-tower]]

## Tiêu chí nghiệm thu (AC)

- [x] AC1: CLAUDE.md thêm section "Coordinator Style" với rule: terse responses, 1-2 câu, không giải thích dài
- [x] AC2: Batch confirmation pattern: "Spec+Plan ok? Dispatch @agent? [y/n]" thay vì hỏi từng bước
- [x] AC3: Sau khi spawn CLI, không tóm tắt output — chỉ báo pass/fail + action tiếp theo
- [x] AC4: Skills (pm, verdict) update để follow terse style

## Plan

### Step 1 — Edit CLAUDE.md
Thêm "## Coordinator Style" với rules terse.

### Step 2 — Update skills
pm/SKILL.md, verdict/SKILL.md — thêm note về terse output.

### Step 3 — Verify
Đọc lại, confirm 4 AC.
