---
project: topvnsport-oms
full_name: "TopVNSport - OMS (Order Management System)"
repo_root: /home/lupca/projects/topvnsport
task_prefix: OMS
next_task_id: 1
created: 2026-07-21
updated: 2026-07-21
---

# TopVNSport - OMS

Dự án này quản lý đơn hàng và hoàn tất đơn (fulfillment) cho hệ thống Top VNSport.

## Tiến độ
| Trạng thái | Số task |
|:---|---:|
| done | 0 |
| todo | 0 |
*(Cập nhật bởi `/report`)*

Chưa có task nào được sinh chi tiết qua `/pm`. Xem `inbox.md` mục 1 (xuất hóa đơn VAT tự động) — chạy `/ingest` hoặc `/pm --project topvnsport-oms <mô tả>` để sinh task với path thật từ `code-review-graph`.

## Tasks
*(Cập nhật bởi `/report` — mỗi lần chạy sẽ regenerate lại toàn bộ danh sách này từ `tasks/*.md`)*
*(chưa có task nào)*

## Quy tắc phê duyệt riêng (Project Gates)
- Mọi thay đổi liên quan đến cấu trúc DB hoặc luồng thanh toán/hóa đơn bắt buộc phải có sự xác nhận của User trước khi executor (ngoài hệ) chạy migrate hoặc đụng tới logic tiền.
- Các task hoàn thành phải pass qua 100% test case trong file test tương ứng — reviewer độc lập xác nhận qua `/verdict pass` (`AGENTS.md` mục 3, 4) mới được đánh dấu `status: done`.
- Test chạy trong Docker: `docker compose -f OMS/docker-compose.yml exec api pytest ...` — do executor và reviewer tự chạy, không phải control-tower.

## References (tài liệu trong repo code — chỉ tham chiếu, KHÔNG copy)
| Tài liệu | Path | Mô tả |
|:---|:---|:---|
| CLAUDE.md | `CLAUDE.md` | Dev conventions, test commands |
