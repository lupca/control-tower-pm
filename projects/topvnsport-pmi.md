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

### 1.3. Phân hệ Authentication & Infrastructure (đã hoàn thành)

> Các task dưới đây được reconcile từ git history — đã implement trước khi control-tower tracking.

- [x] Triển khai Identity Service SSO tập trung 📅 2026-07-14 ⏫
    🔗 Identity/, Gateway/, PMI/backend/utils/auth.py, OMS/backend/utils/auth.py, WMS/backend/utils/auth.py
    ✅ AC:
       - [x] Backend FastAPI cho auth, staff, roles endpoints
       - [x] Frontend Next.js 14 (login, dashboard, CRUD pages)
       - [x] Nginx Gateway với auth_request centralized authentication
       - [x] PMI/OMS/WMS backend đọc X-User-* headers từ gateway
    🧪 Test: Identity/backend/tests/, PMI/backend/tests/test_auth*.py
    Commit: `0d22c38`

- [x] Migrate PMI sang Identity Service authentication 📅 2026-07-14 ⏫
    🔗 PMI/backend/utils/auth.py, PMI/web/src/utils/apiClient.ts
    ✅ AC:
       - [x] PMI sử dụng Identity Service thay vì local login
       - [x] Xóa login page legacy, dùng AuthGuard
    🧪 Test: PMI/backend/tests/test_auth*.py
    Commit: `e5461a5`, `3d6ee6d`

- [x] Hoàn thành API Gateway migration & centralize authentication 📅 2026-07-15 ⏫
    🔗 Gateway/, OMS/backend/, OMS/web/, WMS/backend/, WMS/web/
    ✅ AC:
       - [x] API Gateway hoạt động cho tất cả services
       - [x] OMS/WMS frontend & backend auth hoạt động qua gateway
    🧪 Test: E2E auth tests
    Commit: `b279b90`

- [x] Deploy Identity Service lên CD pipeline 📅 2026-07-15 ⏫
    🔗 .github/workflows/, docker-compose*.yml
    ✅ AC:
       - [x] Identity Service có trong CI/CD pipeline
    Commit: `91dfb05`

### 1.4. Phân hệ Product & Inventory (đã hoàn thành)

- [x] Refactor Product Form UX 📅 2026-07-14 🔼
    🔗 PMI/web/src/components/ProductForm.tsx, PMI/web/src/pages/products/
    ✅ AC:
       - [x] Cải thiện UX theo plan đã duyệt
       - [x] Fix race condition category/family trong ProductForm
    🧪 Test: PMI/web/src/__tests__/
    Commit: `7e820ae`, `475d4c`

- [x] Implement Cost/Tax sync flow giữa PMI và WMS 📅 2026-07-15 🔼
    🔗 PMI/backend/api/, WMS/backend/api/
    ✅ AC:
       - [x] Cost và tax data đồng bộ giữa PMI ↔ WMS
    Commit: `cf886a5`

- [x] Di chuyển Stock Management từ PMI sang WMS 📅 2026-07-21 ⏫ ⚠️high-risk
    🔗 WMS/backend/api/public.py, PMI/web/src/utils/, PMI/backend/models.py, PMI/backend/alembic/
    🌀 Luồng ảnh hưởng: Product listing, Inventory lookup, Export CSV
    ✅ AC:
       - [x] WMS có GET /public/stock endpoint cho real-time inventory
       - [x] PMI Frontend fetch stock từ WMS và merge vào product data
       - [x] Xóa stock column khỏi product_variants (PMI)
       - [x] Xóa stock field khỏi tất cả APIs, forms, exports (PMI)
    🧪 Test: WMS 25 tests (4 new public stock), PMI Backend 121, PMI Frontend 122, E2E 18 (7 new stock flow)
    Migration: `c9a2d4b80123_remove_stock_column.py`
    Commit: `d14f956`

---

## 2. QUY TẮC PHÊ DUYỆT RIÊNG CHO PHÂN HỆ (Project Gates)
- Mọi thay đổi liên quan đến cấu trúc DB (schema Pydantic trong `PMI/backend/schemas/`, model trong `PMI/backend/models.py`) bắt buộc phải có sự xác nhận của User bằng văn bản/chat trước khi executor (ngoài hệ) chạy lệnh `alembic revision --autogenerate` / `alembic upgrade head`.
- Các task hoàn thành phải pass qua 100% test case trong file test tương ứng — reviewer độc lập xác nhận qua `/verdict pass` (`AGENTS.md` mục 3, 4) mới được đánh dấu `- [x]`.
- Test chạy trong Docker theo đúng CLAUDE.md của `topvnsport`: `docker compose -f PMI/docker-compose.yml exec api pytest ...` — do executor và reviewer tự chạy, không phải control-tower.
