---
id: OMS-015
task_path: projects/topvnsport-oms/tasks/OMS-015-fix-storefront-existing-customer-order.md
project: topvnsport-oms
result_ref: c1eca2b
executor: @antigravity-3.6-high
reviewer: "@antigravity"
status: passed
issued: 2026-07-25
verdict: pass
verdict_date: 2026-07-25
---

# Phiếu Review: OMS-015 — Storefront không đặt được đơn cho khách đã tồn tại

- Dự án: topvnsport-oms (`/home/lupca/projects/topvnsport`)
- Task gốc: `projects/topvnsport-oms/tasks/OMS-015-fix-storefront-existing-customer-order.md`
- Result-ref: c1eca2b
- Executor: @antigravity-3.6-high
- Reviewer: @antigravity
- Ngày phát phiếu: 2026-07-25

## Acceptance Criteria cần verify
## Tiêu chí nghiệm thu (AC)

- [x] AC1: `POST /api/customers` khi phone đã tồn tại trả về **200** (hoặc 409) kèm `customer_id` trong response body, thay vì 400 không có id.
- [x] AC2: Web `findOrCreateCustomer` (`web/src/services/sport-api/index.ts:275`) xử lý được response mới, lấy `customer_id` thành công.
- [x] AC3: Đặt đơn cho khách cũ (phone đã tồn tại) **thành công** end-to-end trên storefront.
- [x] AC4: Không mở `GET /customers` (staff-only) cho public — giữ nguyên 401 cho anonymous.
- [x] AC5: Backward compatible: đặt đơn cho khách **mới** vẫn hoạt động bình thường.

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
`/verdict OMS-015 <pass|changes> --reviewer @antigravity [--commit <hash>] [--notes "..."]`
