---
project: topvnsport-web
full_name: "TopVNSport - Web (Frontend Application)"
repo_root: /home/lupca/projects/topvnsport
task_prefix: WEB
next_task_id: 15
created: 2026-07-22
updated: 2026-07-24
---

# TopVNSport - Web

Dự án quản lý frontend application (Vue/React) của hệ thống TopVNSport.

## Tiến độ
| Trạng thái | Số task |
|:---|---:|
| done | 7 |
| in-review | 1 |
| todo | 4 |
*(Cập nhật bởi `/report`)*

## Tasks
*(Cập nhật bởi `/report` — mỗi lần chạy sẽ regenerate lại toàn bộ danh sách này từ `tasks/*.md`)*
- [[WEB-001-promotion-module]] — Implement Promotion Module cho Marketing Team (done)
- [[WEB-002-cleanup-oms-coupon-code]] — Xóa code OMS coupon thừa từ WEB-001 lần 1 (done)
- [[WEB-003-fix-vitest-dependency-conflict]] — Fix vitest dependency version conflict in Web Storefront (done)
- [[WEB-004-research-cors-stock-api-prod-failure]] — Research: CORS block + stock API vẫn fail trên production (done)
- [[WEB-005-fix-discount-price-display]] — Fix discount price display on product detail page (in-review)
- [[WEB-006-verify-all-products-discount-e2e]] — Verify end-to-end: giảm giá scope 'tất cả sản phẩm' hiển thị đúng trên storefront (done)
- [[WEB-007-audit-technical-debt-docs]] — Audit Technical Debt documentation - xác nhận nợ kỹ thuật còn hiệu lực (done)
- [[WEB-008-cart-reliability]] — Cart reliability: localStorage persistence + quantity update + nanoid (todo)
- [[WEB-009-app-state-error-handling]] — App state: error handling + OTP token sessionStorage + checkout validation (todo)
- [[WEB-010-web-performance]] — Performance: remove simulated latency + code splitting (todo)
- [[WEB-011-fix-duplicate-cors-headers-gateway]] — Storefront không lấy được data PMI: header CORS bị NHÂN ĐÔI (gateway + app cùng thêm) → browser chặn (done)
- [[WEB-012-remove-dead-fallback-findorcreate]] — Xóa dead code fallback trong findOrCreateCustomer (todo)
- [[WEB-013-split-web-repo-gateway-cleanup]] — Split web to separate repo + gateway cleanup + CI/CD for new repo (done)
- [[WEB-014-remove-docker-files]] — Remove Docker files from standalone web repo (todo)

## Quy tắc phê duyệt riêng (Project Gates)
- Mọi thay đổi liên quan đến routing, state management hoặc API integration cần có test coverage.
- UI changes phải được test trên ít nhất 2 trình duyệt (Chrome, Firefox).
- Các task hoàn thành phải pass qua 100% test case — reviewer độc lập xác nhận qua `/verdict pass` (`AGENTS.md` mục 3, 4) mới được đánh dấu `status: done`.

## References (tài liệu trong repo code — chỉ tham chiếu, KHÔNG copy)
| Tài liệu | Path | Mô tả |
|:---|:---|:---|
| CLAUDE.md | `CLAUDE.md` | Dev conventions, test commands |
| package.json | `web/package.json` | Dependencies, scripts |
