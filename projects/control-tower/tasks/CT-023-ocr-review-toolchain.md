---
id: CT-023
title: "Tích hợp OCR vào review layer — review toolchain architecture"
status: done
priority: high
risk: normal
deadline: null
executor: "@claude-opus"
reviewer: "@antigravity"
result_ref: "0d0754c"
depends_on: []
files:
  - .claude/skills/pm/SKILL.md
  - .claude/skills/review-order/SKILL.md
  - .claude/skills/dispatch/SKILL.md
  - knowledge/guides/review-toolchain.md
flows: []
tests: []
dispatched: 2026-07-24
in_review: 2026-07-24
predicted_success: high
prediction_factors:
  score: 0.9
  deductions:
    - "no_tests: meta-project, markdown files only (-0.1)"
created: 2026-07-24
updated: 2026-07-24
---


# CT-023: Tích hợp OCR vào review layer — review toolchain architecture

> Dự án: [[projects/control-tower/control-tower]]

## Tiêu chí nghiệm thu (AC)

- [ ] `review-order/SKILL.md` Step 6: section "Gợi ý công cụ" được thay bằng "Review Toolchain" trỏ về `.claude/review-toolchain.md` của repo đích
- [ ] `dispatch/SKILL.md` Step 5: reviewer prompt (khi có `--review`) hướng dẫn reviewer đọc `.claude/review-toolchain.md` rồi chạy pipeline, fallback `/code-review` nếu file không tồn tại
- [ ] `pm/SKILL.md`: thêm optional step sau graph queries — nếu repo có `ocr` CLI, chạy `ocr scan --path <files>` và ghi kết quả vào `## Plan` dưới section `## Pre-scan findings (OCR)`
- [ ] `knowledge/guides/review-toolchain.md` tồn tại: template + hướng dẫn tạo `.claude/review-toolchain.md` cho repo mới. Toolchain chỉ chứa review tools (OCR, linters) — KHÔNG chứa test commands (tests đã có trong review sheet `## Test gợi ý`)
- [ ] Không thay đổi task lifecycle, gates, hay bất kỳ rule nào trong AGENTS.md — chỉ thay đổi skill implementation

## Verification

- `grep -c "review-toolchain" .claude/skills/review-order/SKILL.md` → ≥1
- `grep -c "review-toolchain" .claude/skills/dispatch/SKILL.md` → ≥1
- `grep -c "ocr scan" .claude/skills/pm/SKILL.md` → ≥1
- `test -f knowledge/guides/review-toolchain.md` → exit 0
- `grep -c "Gợi ý công cụ" .claude/skills/review-order/SKILL.md` → 0 (replaced)

## Plan

### 1. `review-order/SKILL.md` — Step 6 template
Thay section `## Gợi ý công cụ` (lines 100-101) bằng:
```markdown
## Review Toolchain
Chạy review theo repo's toolchain:
  cat .claude/review-toolchain.md
Nếu file không tồn tại → dùng /code-review mặc định.
Chạy tất cả tools trong pipeline, aggregate kết quả,
rồi verify từng AC item.
```

### 2. `dispatch/SKILL.md` — Step 5 reviewer prompt
Khi có `--review` flag, thay prompt `"Review task at <task_path>"` bằng:
```
Review task at <task_path>.
Result ref: <result_ref>. Review sheet: <review_sheet_path>.
1. Read .claude/review-toolchain.md — run each tool in pipeline.
   If file missing, run /code-review as default.
2. Verify each AC item in the review sheet.
3. Report: tool findings + AC results + tests + verdict.
```

### 3. `pm/SKILL.md` — Optional OCR pre-scan
Thêm step 8.5 (sau `get_affected_flows_tool`, trước prediction):
- Chạy `cd <repo_root> && ocr scan --path <files> --format json` (via Bash, repo_root từ PROJECT REGISTRY)
- Nếu `ocr` không có trên system hoặc fail → skip silently
- Nếu có findings → ghi vào task body dưới `## Pre-scan findings (OCR)`
- Executor sẽ thấy bug tiềm ẩn trước khi bắt đầu

### 4. `knowledge/guides/review-toolchain.md` — Convention doc
Tạo file mới:
- Mục đích: hướng dẫn tạo `.claude/review-toolchain.md` cho repo mới
- Chỉ chứa review tools (OCR, linters) — KHÔNG chứa test commands (tests đã có trong review sheet `## Test gợi ý` + task `tests:` field)
- OCR tự detect changed files từ git range (`--from main --to $RESULT_REF`) → không cần conditional file matching
- Ví dụ: `ocr review --from main --to $RESULT_REF --format json`
- Fallback rule: không có file → `/code-review` mặc định

## Sub-tasks
- [ ] Sửa `review-order/SKILL.md` Step 6: thay "Gợi ý công cụ" → "Review Toolchain"
- [ ] Sửa `dispatch/SKILL.md` Step 5: genericize reviewer prompt với review-toolchain.md reference
- [ ] Sửa `pm/SKILL.md`: thêm optional ocr scan step sau graph queries (step 8.5)
- [ ] Tạo `knowledge/guides/review-toolchain.md` — convention template
