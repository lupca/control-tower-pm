---
project: topvnsport-wms
full_name: "TopVNSport - WMS (Warehouse Management System)"
repo_root: /home/lupca/projects/topvnsport
task_prefix: WMS
next_task_id: 7
created: 2026-07-21
updated: 2026-07-21
---

# TopVNSport - WMS

Dự án quản lý kho hàng (Warehouse Management System) cho hệ thống TopVNSport — bao gồm quản lý tồn kho, nhập/xuất kho, vị trí ô kệ, barcode mappings.

## Tiến độ
| Trạng thái | Số task |
|:---|---:|
| done | 3 |
| todo | 2 |
| completed | 1 |
*(Cập nhật bởi `/report`)*

## Tasks
*(Cập nhật bởi `/report` — mỗi lần chạy sẽ regenerate lại toàn bộ danh sách này từ `tasks/*.md`)*
- [[WMS-001-table-stt-pagination]] — Nâng cấp DataTable: thêm cột STT và pagination cho toàn bộ WMS (done)
- [[WMS-002-fix-414-stock-api-uri-too-large]] — Fix 414 Request-URI Too Large when fetching stock for many SKUs (done)
- [[WMS-003-fix-ci-docker-network-label-mismatch]] — Fix CI Docker Compose network label mismatch for oms_default (done)
- [[WMS-004-fix-race-conditions]] — Fix race conditions: receive scan, pick scan + row locking (todo)
- [[WMS-005-data-integrity-guards]] — Data integrity: over-pick/receive guards, ship status validation, OMS notification outbox (todo)
- [[WMS-006-rds-migration]] — Migrate WMS to RDS Aurora (completed)

## Quy tắc phê duyệt riêng (Project Gates)
- Mọi thay đổi liên quan đến cấu trúc DB (schema Pydantic trong `WMS/backend/schemas.py`, model trong `WMS/backend/models.py`) bắt buộc phải có sự xác nhận của User trước khi executor chạy lệnh `alembic revision --autogenerate` / `alembic upgrade head`.
- Các task hoàn thành phải pass qua 100% test case trong file test tương ứng — reviewer độc lập xác nhận qua `/verdict pass` mới được đánh dấu `status: done`.
- Test chạy trong Docker: `docker compose -f WMS/docker-compose.yml exec api pytest ...` — do executor và reviewer tự chạy, không phải control-tower.

## References (tài liệu trong repo code — chỉ tham chiếu, KHÔNG copy)
| Tài liệu | Path | Mô tả |
|:---|:---|:---|
| CLAUDE.md | `CLAUDE.md` | Dev conventions, test commands |
