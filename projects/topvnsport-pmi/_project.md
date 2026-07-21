---
project: topvnsport-pmi
full_name: "TopVNSport - PMI (Product Information Management)"
repo_root: /home/lupca/projects/topvnsport
task_prefix: PMI
next_task_id: 10
created: 2026-07-21
updated: 2026-07-21
---

# TopVNSport - PMI

Dự án này tập trung vào việc tích hợp các quy trình nghiệp vụ và tiêu chuẩn PMI vào hệ thống vận hành.

## Tiến độ
| Trạng thái | Số task |
|:---|---:|
| done | 8 |
| todo | 1 |
*(Cập nhật bởi `/report`)*

## Tasks
*(Cập nhật bởi `/report` — mỗi lần chạy sẽ regenerate lại toàn bộ danh sách này từ `tasks/*.md`)*
- [[PMI-001-variant-cost-tax]] — Thêm validation cost/tax cho variant (done)
- [[PMI-002-pdf-report]] — Thiết kế luồng xuất báo cáo doanh thu tuần sang PDF (todo)
- [[PMI-003-identity-sso]] — Triển khai Identity Service SSO tập trung (done)
- [[PMI-004-pmi-identity-migration]] — Migrate PMI sang Identity Service authentication (done)
- [[PMI-005-api-gateway-migration]] — Hoàn thành API Gateway migration & centralize authentication (done)
- [[PMI-006-identity-cd-pipeline]] — Deploy Identity Service lên CD pipeline (done)
- [[PMI-007-product-form-ux]] — Refactor Product Form UX (done)
- [[PMI-008-cost-tax-sync-wms]] — Implement Cost/Tax sync flow giữa PMI và WMS (done)
- [[PMI-009-stock-management-wms]] — Di chuyển Stock Management từ PMI sang WMS (done)

## Quy tắc phê duyệt riêng (Project Gates)
- Mọi thay đổi liên quan đến cấu trúc DB (schema Pydantic trong `PMI/backend/schemas/`, model trong `PMI/backend/models.py`) bắt buộc phải có sự xác nhận của User bằng văn bản/chat trước khi executor (ngoài hệ) chạy lệnh `alembic revision --autogenerate` / `alembic upgrade head`.
- Các task hoàn thành phải pass qua 100% test case trong file test tương ứng — reviewer độc lập xác nhận qua `/verdict pass` (`AGENTS.md` mục 3, 4) mới được đánh dấu `status: done`.
- Test chạy trong Docker theo đúng CLAUDE.md của `topvnsport`: `docker compose -f PMI/docker-compose.yml exec api pytest ...` — do executor và reviewer tự chạy, không phải control-tower.

## References (tài liệu trong repo code — chỉ tham chiếu, KHÔNG copy)
| Tài liệu | Path | Mô tả |
|:---|:---|:---|
| CLAUDE.md | `CLAUDE.md` | Dev conventions, test commands |
