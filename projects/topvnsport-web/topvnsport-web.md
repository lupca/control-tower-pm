---
project: topvnsport-web
full_name: "TopVNSport - Web (Frontend Application)"
repo_root: /home/lupca/projects/topvnsport
task_prefix: WEB
next_task_id: 6
created: 2026-07-22
updated: 2026-07-24
---

# TopVNSport - Web

Dự án quản lý frontend application (Vue/React) của hệ thống TopVNSport.

## Tiến độ
| Trạng thái | Số task |
|:---|---:|
| done | 4 |
| in-review | 1 |
*(Cập nhật bởi `/report`)*

## Tasks
*(Cập nhật bởi `/report` — mỗi lần chạy sẽ regenerate lại toàn bộ danh sách này từ `tasks/*.md`)*
- [[WEB-001-promotion-module]] — Implement Promotion Module cho Marketing Team (done)
- [[WEB-002-cleanup-oms-coupon-code]] — Xóa code OMS coupon thừa từ WEB-001 lần 1 (done)
- [[WEB-003-fix-vitest-dependency-conflict]] — Fix vitest dependency version conflict in Web Storefront (done)
- [[WEB-004-research-cors-stock-api-prod-failure]] — Research: CORS block + stock API vẫn fail trên production (todo)
- [[WEB-005-fix-discount-price-display]] — Fix discount price display on product detail page (in-review)

## Quy tắc phê duyệt riêng (Project Gates)
- Mọi thay đổi liên quan đến routing, state management hoặc API integration cần có test coverage.
- UI changes phải được test trên ít nhất 2 trình duyệt (Chrome, Firefox).
- Các task hoàn thành phải pass qua 100% test case — reviewer độc lập xác nhận qua `/verdict pass` (`AGENTS.md` mục 3, 4) mới được đánh dấu `status: done`.

## References (tài liệu trong repo code — chỉ tham chiếu, KHÔNG copy)
| Tài liệu | Path | Mô tả |
|:---|:---|:---|
| CLAUDE.md | `CLAUDE.md` | Dev conventions, test commands |
| package.json | `web/package.json` | Dependencies, scripts |
