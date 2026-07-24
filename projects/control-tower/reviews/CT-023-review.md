---
id: CT-023
task_path: projects/control-tower/tasks/CT-023-ocr-review-toolchain.md
project: control-tower
result_ref: "0d0754c"
executor: "@claude-opus"
reviewer: "@antigravity"
status: completed
issued: 2026-07-24
verdict: pass
verdict_date: 2026-07-24
---

# Phiếu Review: CT-023 — Tích hợp OCR vào review layer — review toolchain architecture

- Dự án: control-tower (`/home/lupca/projects/control-tower`)
- Task gốc: `projects/control-tower/tasks/CT-023-ocr-review-toolchain.md`
- Result-ref: `0d0754c`
- Executor: @claude-opus
- Ngày phát phiếu: 2026-07-24

## Acceptance Criteria cần verify

- [ ] `review-order/SKILL.md` Step 6: section "Gợi ý công cụ" được thay bằng "Review Toolchain" trỏ về `.claude/review-toolchain.md` của repo đích
- [ ] `dispatch/SKILL.md` Step 5: reviewer prompt (khi có `--review`) hướng dẫn reviewer đọc `.claude/review-toolchain.md` rồi chạy pipeline, fallback `/code-review` nếu file không tồn tại
- [ ] `pm/SKILL.md`: thêm optional step sau graph queries — nếu repo có `ocr` CLI, chạy `ocr scan --path <files>` và ghi kết quả vào `## Plan` dưới section `## Pre-scan findings (OCR)`
- [ ] `knowledge/guides/review-toolchain.md` tồn tại: template + hướng dẫn tạo `.claude/review-toolchain.md` cho repo mới. Toolchain chỉ chứa review tools (OCR, linters) — KHÔNG chứa test commands (tests đã có trong review sheet `## Test gợi ý`)
- [ ] Không thay đổi task lifecycle, gates, hay bất kỳ rule nào trong AGENTS.md — chỉ thay đổi skill implementation

## Definition of Done (AGENTS.md mục 3)

- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: (meta-project, no tests — markdown files only)
- [ ] Không regression (các skill khác vẫn hoạt động đúng)
- [ ] Reviewer khác executor (bạn đang review, hãy xác nhận bạn ≠ @claude-opus)

## Test gợi ý chạy trong repo code

```bash
grep -c "review-toolchain" .claude/skills/review-order/SKILL.md   # → ≥1
grep -c "review-toolchain" .claude/skills/dispatch/SKILL.md       # → ≥1
grep -c "ocr scan" .claude/skills/pm/SKILL.md                     # → ≥1
test -f knowledge/guides/review-toolchain.md                       # → exit 0
grep -c "Gợi ý công cụ" .claude/skills/review-order/SKILL.md     # → 0
```

## Câu hỏi rủi ro

(Graph n/a — meta-project, no code graph. Review dựa trên đọc diff trực tiếp.)

- Reviewer prompt mới trong `dispatch/SKILL.md` có đủ rõ ràng để reviewer AI hiểu cần làm gì không?
- `review-toolchain.md` guide có đủ cụ thể để onboard repo mới không?
- OCR pre-scan step 8.5 trong `task-creation.md` có xử lý đúng khi `ocr` không có trên system không (skip silently)?
- Có thay đổi nào vô tình ảnh hưởng executor prompt (non-review dispatch) không?

## Review Toolchain

Chạy review theo repo's toolchain:
  cat .claude/review-toolchain.md
Nếu file không tồn tại → dùng /code-review mặc định.
Chạy tất cả tools trong pipeline, aggregate kết quả,
rồi verify từng AC item.

## Trả kết quả

Sau khi review xong, báo lại cho control-tower bằng lệnh:
`/verdict CT-023 <pass|changes> --reviewer @<tên bạn> --commit 0d0754c [--notes "..."]`
