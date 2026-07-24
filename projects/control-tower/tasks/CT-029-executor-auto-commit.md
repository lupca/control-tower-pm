---
id: CT-029
title: "Fix dispatch executor auto commit"
status: dispatched
priority: high
risk: normal
depends_on: []
files:
  - .agents/skills/dispatch/SKILL.md
flows: []
tests: []
dispatched: 2026-07-25
in_review: null
executor: "@antigravity"
predicted_success: high
prediction_factors:
  score: 1.0
  deductions: []
created: 2026-07-25
updated: 2026-07-25
---

# CT-029: Fix dispatch executor auto commit

> Dự án: [[projects/control-tower/control-tower]]

## Tiêu chí nghiệm thu (AC)
- [ ] Lệnh spawn executor trong file `dispatch/SKILL.md` (hoặc prompt template) yêu cầu rõ ràng agent phải commit code và trả về `commit hash`.

## Verification
- Kiểm tra nội dung chuỗi `Executor (default):` trong file `.agents/skills/dispatch/SKILL.md`.
- Chắc chắn prompt có lệnh yêu cầu agent commit.

## Plan
1. Mở file `.agents/skills/dispatch/SKILL.md`.
2. Sửa block prompt của `Executor (default):` để thêm câu: "When you are done, you MUST commit your changes and provide the resulting commit hash."
3. Lưu file.

## Sub-tasks
- [ ] Thêm yêu cầu commit code vào prompt của executor trong file `.agents/skills/dispatch/SKILL.md`.
