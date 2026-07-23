---
id: CT-020
title: "Xóa AGENTS-EXPERIMENTAL.md, archive dormant features"
status: done
priority: high
risk: normal
deadline: null
executor: "@gpt-5.6-sol"
reviewer: "@claude-sonnet-high"
result_ref: "83d437de4a482d30a9622b3b6d463fd45bfda783"
depends_on: [CT-019]
files:
  - AGENTS-EXPERIMENTAL.md
  - AGENTS.md
  - .claude/skills/ingest/SKILL.md
  - .claude/skills/pm/references/task-creation.md
  - .claude/skills/pm/references/task-execution.md
  - .claude/skills/lint/SKILL.md
flows: []
tests: []
dispatched: 2026-07-23
in_review: null
predicted_success: high
prediction_factors:
  score: 0.9
  deductions:
    - "content_only: markdown cleanup (-0.0)"
    - "no_tests: meta-project (-0.1)"
confidence_interval: [0.8, 0.95]
created: 2026-07-23
updated: 2026-07-23
---

# CT-020: Xóa AGENTS-EXPERIMENTAL.md, archive dormant features

> Dự án: [[projects/control-tower/control-tower]]

## Bối cảnh

CT-019 đã slim `/verdict` từ 91→52 dòng nhưng giữ nguyên `AGENTS-EXPERIMENTAL.md` (270 dòng) làm "archive". Vấn đề: 8 skills vẫn reference file này → vẫn tốn token load. Cần xóa hẳn file, archive dormant features sang `docs/`, và xóa references trong skills.

## Tiêu chí nghiệm thu (AC)

- [x] **AC1:** Xóa `AGENTS-EXPERIMENTAL.md` khỏi root
- [x] **AC2:** Tạo `docs/experimental-archive.md` chứa §14, §17-§20 (dormant features) để reference tương lai
- [x] **AC3:** Xóa tất cả references `(AGENTS-EXPERIMENTAL.md §xx)` trong skills:
  - `.claude/skills/ingest/SKILL.md` — xóa reference §19.1, §19.2
  - `.claude/skills/pm/references/task-creation.md` — xóa reference §13, §15, §16
  - `.claude/skills/pm/references/task-execution.md` — xóa reference §12, §16.2
  - `.claude/skills/lint/SKILL.md` — xóa reference §13, §16.4
- [x] **AC4:** Cập nhật `AGENTS.md` header — xóa dòng về AGENTS-EXPERIMENTAL.md, thêm note về `docs/experimental-archive.md`

## Verification

```bash
# File đã xóa
test ! -f AGENTS-EXPERIMENTAL.md && echo "PASS: file deleted"

# Archive tồn tại
test -f docs/experimental-archive.md && echo "PASS: archive exists"

# Không còn reference
grep -r "AGENTS-EXPERIMENTAL" .claude/skills/ && echo "FAIL" || echo "PASS: no refs"
```

## Plan

1. Tạo `docs/experimental-archive.md` với header + §14, §17-§20
2. Xóa `AGENTS-EXPERIMENTAL.md`
3. Edit 4 skill files xóa references `(AGENTS-EXPERIMENTAL.md §xx)`
4. Edit `AGENTS.md` header
5. Run verification commands
