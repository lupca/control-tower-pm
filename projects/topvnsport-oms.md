# DỰ ÁN: TOPVNSPORT - OMS (Order Management System)

`repo_root`: `/home/lupca/projects/topvnsport` (xem PROJECT REGISTRY trong `index.md`, thư mục con `OMS/`)

Dự án này quản lý đơn hàng và hoàn tất đơn (fulfillment) cho hệ thống Top VNSport.

---

## 1. DANH SÁCH TASK HIỆN TẠI (Backlog & Sprint)

Chưa có task nào được sinh chi tiết qua `/pm`. Xem `inbox.md` mục 1 (xuất hóa đơn VAT tự động) — chạy `/ingest` hoặc `/pm --project topvnsport-oms <mô tả>` để sinh task với path thật từ `code-review-graph`.

---

## 2. QUY TẮC PHÊ DUYỆT RIÊNG CHO PHÂN HỆ (Project Gates)
- Mọi thay đổi liên quan đến cấu trúc DB hoặc luồng thanh toán/hóa đơn bắt buộc phải có sự xác nhận của User trước khi executor (ngoài hệ) chạy migrate hoặc đụng tới logic tiền.
- Các task hoàn thành phải pass qua 100% test case trong file test tương ứng — reviewer độc lập xác nhận qua `/verdict pass` (`AGENTS.md` mục 3, 4) mới được đánh dấu `- [x]`.
- Test chạy trong Docker: `docker compose -f OMS/docker-compose.yml exec api pytest ...` — do executor và reviewer tự chạy, không phải control-tower.
