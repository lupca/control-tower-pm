# DỰ ÁN: TOPVNSPORT - PMI (Product Information Management)

`repo_root`: `/home/lupca/projects/topvnsport` (xem PROJECT REGISTRY trong `index.md`)

Dự án này tập trung vào việc tích hợp các quy trình nghiệp vụ và tiêu chuẩn PMI vào hệ thống vận hành.

---

## 1. DANH SÁCH TASK HIỆN TẠI (Backlog & Sprint)

### 1.1. Phân hệ Validation & Schema

> Path dưới đây đã được đối chiếu trực tiếp với repo thật (`PMI/backend/`) — không phải path đoán mò.

- [x] Thêm validation cost/tax cho variant 📅 2026-08-01 ⏫ *(Phát hiện đã tồn tại trong code — xem ghi chú bên dưới)*
    - [x] Schema validation trong `PMI/backend/schemas/tier_variation.py` 🔗 PMI/backend/schemas/tier_variation.py — `default_cost_price: Field(ge=0)`, `default_tax_rate: Field(ge=0, le=100)` đã có sẵn (dòng 26-27).
    - [x] Migration DB tương ứng: `PMI/backend/alembic/versions/5a451ed7aa00_add_cost_tax_to_variants.py`.
    - [x] Test coverage: `PMI/backend/tests/test_variant_cost_tax.py` (`test_cost_price_must_be_non_negative`, `test_tax_rate_must_be_0_to_100`) và `PMI/backend/tests/test_product_api_cost_tax.py` (`test_create_product_with_cost_tax`, `test_update_variant_cost_tax`) đã tồn tại.

> **Ghi chú:** Task này được chép từ file nháp gốc với path generic (`schema.py`, `test_product.py`). Khi chạy `semantic_search_nodes_tool`/CLI `search` để xác nhận path thật, phát hiện tính năng **đã được implement từ trước** (có migration + test đầy đủ) — không phải task còn tồn đọng. Đây chính là giá trị của việc luôn xác minh qua graph trước khi tin file nháp/ghi chú thô: task tưởng "cần làm" hóa ra đã "đã làm". Đánh dấu `- [x]` theo Project Gate mục 2 (đã pass 100% test liên quan). Nếu có yêu cầu mở rộng thêm (vd tax rate theo từng khu vực), hãy dùng `/pm` để tạo task mới thay vì mở lại task này.

### 1.2. Phân hệ Báo cáo tự động (Reporting Automation)
- [ ] Thiết kế luồng xuất báo cáo doanh thu tuần sang định dạng PDF 📅 2026-08-10 🔼
    - [ ] Tạo template báo cáo bằng thư viện fpdf2 🔗 reporting_service.py *(path chưa xác nhận qua graph — chạy `/pm` để tra lại trước khi bắt đầu)*
    - [ ] Viết API lấy dữ liệu tổng hợp tuần 🔗 report_api.py *(path chưa xác nhận qua graph — chạy `/pm` để tra lại trước khi bắt đầu)*

---

## 2. QUY TẮC PHÊ DUYỆT RIÊNG CHO PHÂN HỆ (Project Gates)
- Mọi thay đổi liên quan đến cấu trúc DB (schema Pydantic trong `PMI/backend/schemas/`, model trong `PMI/backend/models.py`) bắt buộc phải có sự xác nhận của User bằng văn bản/chat trước khi Subagent chạy lệnh `alembic revision --autogenerate` / `alembic upgrade head`.
- Các task hoàn thành phải pass qua 100% test case trong file test tương ứng mới được đánh dấu `- [x]`.
- Test chạy trong Docker theo đúng CLAUDE.md của `topvnsport`: `docker compose -f PMI/docker-compose.yml exec api pytest ...`.
