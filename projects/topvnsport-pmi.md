# DỰ ÁN: TOPVNSPORT - PMI (Product Information Management)

`repo_root`: `/home/lupca/projects/topvnsport` (xem PROJECT REGISTRY trong `index.md`)

Dự án này tập trung vào việc tích hợp các quy trình nghiệp vụ và tiêu chuẩn PMI vào hệ thống vận hành.

---

## 1. DANH SÁCH TASK HIỆN TẠI (Backlog & Sprint)

### 1.1. Phân hệ Validation & Schema

> Path dưới đây đã được đối chiếu trực tiếp với repo thật (`PMI/backend/`) — không phải path đoán mò.

- [ ] Thêm validation cost/tax cho variant 📅 2026-08-01 ⏫
    - [ ] Cập nhật schema validation trong `PMI/backend/schemas/tier_variation.py` 🔗 PMI/backend/schemas/tier_variation.py [Rủi ro rò rỉ dữ liệu hoặc lỗi kiểu dữ liệu]
    - [ ] Cập nhật schema variant liên quan trong `PMI/backend/schemas/product.py` 🔗 PMI/backend/schemas/product.py
    - [ ] Viết logic kiểm tra tỷ giá và thuế trong `PMI/backend/services/product_service.py` 🔗 PMI/backend/services/product_service.py [Tầm ảnh hưởng: Cao]
    - [ ] Kiểm tra router `PMI/backend/routers/products.py` có cần cập nhật request/response schema không 🔗 PMI/backend/routers/products.py
    - [ ] Chạy và bổ sung test case trong `PMI/backend/tests/test_variant_cost_tax.py` 🔗 PMI/backend/tests/test_variant_cost_tax.py [Mức độ bao phủ kiểm thử: 100%]
    - [ ] Chạy và bổ sung test case trong `PMI/backend/tests/test_product_api_cost_tax.py` 🔗 PMI/backend/tests/test_product_api_cost_tax.py

### 1.2. Phân hệ Báo cáo tự động (Reporting Automation)
- [ ] Thiết kế luồng xuất báo cáo doanh thu tuần sang định dạng PDF 📅 2026-08-10 🔼
    - [ ] Tạo template báo cáo bằng thư viện fpdf2 🔗 reporting_service.py *(path chưa xác nhận qua graph — chạy `/pm` để tra lại trước khi bắt đầu)*
    - [ ] Viết API lấy dữ liệu tổng hợp tuần 🔗 report_api.py *(path chưa xác nhận qua graph — chạy `/pm` để tra lại trước khi bắt đầu)*

---

## 2. QUY TẮC PHÊ DUYỆT RIÊNG CHO PHÂN HỆ (Project Gates)
- Mọi thay đổi liên quan đến cấu trúc DB (schema Pydantic trong `PMI/backend/schemas/`, model trong `PMI/backend/models.py`) bắt buộc phải có sự xác nhận của User bằng văn bản/chat trước khi Subagent chạy lệnh `alembic revision --autogenerate` / `alembic upgrade head`.
- Các task hoàn thành phải pass qua 100% test case trong file test tương ứng mới được đánh dấu `- [x]`.
- Test chạy trong Docker theo đúng CLAUDE.md của `topvnsport`: `docker compose -f PMI/docker-compose.yml exec api pytest ...`.
