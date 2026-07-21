---
project: topvnsport-wms
full_name: "TopVNSport - WMS (Warehouse Management System)"
repo_root: /home/lupca/projects/topvnsport
task_prefix: WMS
next_task_id: 2
created: 2026-07-21
updated: 2026-07-21
---

# TopVNSport - WMS

Dự án quản lý kho hàng (Warehouse Management System) cho hệ thống TopVNSport — bao gồm quản lý tồn kho, nhập/xuất kho, vị trí ô kệ, barcode mappings.

## Tiến độ
| Trạng thái | Số task |
|:---|---:|
| done | 0 |
| todo | 1 |
*(Cập nhật bởi `/report`)*

## Tasks
*(Cập nhật bởi `/report` — mỗi lần chạy sẽ regenerate lại toàn bộ danh sách này từ `tasks/*.md`)*
- [[WMS-001-table-stt-pagination]] — Nâng cấp DataTable: thêm cột STT và pagination cho toàn bộ WMS (in-review)

## Quy tắc phê duyệt riêng (Project Gates)
- Mọi thay đổi liên quan đến cấu trúc DB (schema Pydantic trong `WMS/backend/schemas.py`, model trong `WMS/backend/models.py`) bắt buộc phải có sự xác nhận của User trước khi executor chạy lệnh `alembic revision --autogenerate` / `alembic upgrade head`.
- Các task hoàn thành phải pass qua 100% test case trong file test tương ứng — reviewer độc lập xác nhận qua `/verdict pass` mới được đánh dấu `status: done`.
- Test chạy trong Docker: `docker compose -f WMS/docker-compose.yml exec api pytest ...` — do executor và reviewer tự chạy, không phải control-tower.

## References (tài liệu trong repo code — chỉ tham chiếu, KHÔNG copy)
| Tài liệu | Path | Mô tả |
|:---|:---|:---|
| CLAUDE.md | `CLAUDE.md` | Dev conventions, test commands |
