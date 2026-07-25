---
project: topvnsport-pmi
full_name: "TopVNSport - PMI (Product Information Management)"
repo_root: /home/lupca/projects/topvnsport
task_prefix: PMI
next_task_id: 24
created: 2026-07-21
updated: 2026-07-21
---

# TopVNSport - PMI

Dự án này tập trung vào việc tích hợp các quy trình nghiệp vụ và tiêu chuẩn PMI vào hệ thống vận hành.

## Tiến độ
| Trạng thái | Số task |
|:---|---:|
| done | 11 |
| dispatched | 1 |
| todo | 11 |
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
- [[PMI-010-fix-promotionlist-type-error]] — Fix TypeScript type error in PromotionList renderStatusBadge (done)
- [[PMI-011-fix-all-products-scope-discount]] — Fix khuyến mãi scope 'tất cả sản phẩm' (giảm 20%) không được áp dụng (done)
- [[PMI-012-public-products-promotion-price]] — Endpoint /public/products & /public/products/{slug} chưa trả giá đã áp dụng khuyến mãi (done)
- [[PMI-013-remove-hardcoded-secrets]] — Remove hardcoded secrets từ docker-compose.prod.yml (todo)
- [[PMI-014-remove-db-ports-add-https]] — Remove DB port exposure + Add HTTPS/TLS production (todo)
- [[PMI-015-implement-route-rbac]] — Implement route-level RBAC authorization cho PMI (todo)
- [[PMI-016-extract-shared-packages]] — Extract shared packages - giảm code duplication 4x (todo)
- [[PMI-017-fix-layer-violations]] — Fix HTTP exceptions trong service layer (todo)
- [[PMI-018-standardize-api-clients]] — Standardize API clients across frontends (todo)
- [[PMI-019-fix-n-plus-one-queries]] — Fix N+1 queries + transaction boundaries (todo)
- [[PMI-020-add-error-boundaries]] — Add React Error Boundaries cho all frontends (todo)
- [[PMI-021-infrastructure-improvements]] — Infrastructure: health checks, limits, cache, resilience (todo)
- [[PMI-022-dead-code-removal]] — Dead code removal (~1,400 lines across all services) (todo)
- [[PMI-023-rds-s3-migration]] — Migrate PMI + Identity to RDS and replace MinIO with S3 (dispatched)

## Quy tắc phê duyệt riêng (Project Gates)
- Mọi thay đổi liên quan đến cấu trúc DB (schema Pydantic trong `PMI/backend/schemas/`, model trong `PMI/backend/models.py`) bắt buộc phải có sự xác nhận của User bằng văn bản/chat trước khi executor (ngoài hệ) chạy lệnh `alembic revision --autogenerate` / `alembic upgrade head`.
- Các task hoàn thành phải pass qua 100% test case trong file test tương ứng — reviewer độc lập xác nhận qua `/verdict pass` (`AGENTS.md` mục 3, 4) mới được đánh dấu `status: done`.
- Test chạy trong Docker theo đúng CLAUDE.md của `topvnsport`: `docker compose -f PMI/docker-compose.yml exec api pytest ...` — do executor và reviewer tự chạy, không phải control-tower.

## References (tài liệu trong repo code — chỉ tham chiếu, KHÔNG copy)
| Tài liệu | Path | Mô tả |
|:---|:---|:---|
| CLAUDE.md | `CLAUDE.md` | Dev conventions, test commands |
