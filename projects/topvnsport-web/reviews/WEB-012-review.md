---
id: WEB-012
task_path: projects/topvnsport-web/tasks/WEB-012-remove-dead-fallback-findorcreate.md
project: topvnsport-web
result_ref: c1eca2b
executor: @antigravity-3.6-high
reviewer: "@antigravity"
status: passed
issued: 2026-07-25
verdict: pass
verdict_date: 2026-07-25
---

# Phiếu Review: WEB-012 — Xóa dead code fallback trong findOrCreateCustomer

- Dự án: topvnsport-web (`/home/lupca/projects/topvnsport`)
- Task gốc: `projects/topvnsport-web/tasks/WEB-012-remove-dead-fallback-findorcreate.md`
- Result-ref: c1eca2b
- Executor: @antigravity-3.6-high
- Reviewer: @antigravity
- Ngày phát phiếu: 2026-07-25

## Acceptance Criteria cần verify
## Tiêu chí nghiệm thu (AC)

- [ ] AC1: Xóa fallback GET trong `findOrCreateCustomer` (lines 294-296 hiện tại) — code này không bao giờ thành công vì `GET /customers` yêu cầu staff auth.
- [ ] AC2: Xóa function `findExistingCustomerIdByPhone` trong `omsHelpers.ts` nếu không còn caller nào sau khi cleanup.
- [ ] AC3: Unit test cho `findOrCreateCustomer`: mock POST trả 200 với customer → return id thành công.
- [ ] AC4: Unit test cho `findOrCreateCustomer`: mock POST trả 409 với customer → return id thành công.
- [ ] AC5: Unit test cho `findOrCreateCustomer`: mock POST trả 500 → throw error với message rõ ràng.
- [ ] AC6: Không break flow checkout storefront — đặt đơn mới vẫn hoạt động.

## Definition of Done (AGENTS.md mục 3)
- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: (none recorded)
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (xác nhận reviewer @antigravity ≠ executor @antigravity-3.6-high)

## Test gợi ý chạy trong repo code
- *(none recorded in task frontmatter)*

## Câu hỏi rủi ro (từ code-review-graph, tĩnh — không thay thế việc tự đọc diff)
- *(LLM/coordinator bổ sung từ graph nếu có; script không đọc diff và không gọi graph.)*

## Review Toolchain
Chạy theo toolchain của repo đích; preflight các tool đã đăng ký trước khi review.

## Trả kết quả
`/verdict WEB-012 <pass|changes> --reviewer @antigravity [--commit <hash>] [--notes "..."]`
