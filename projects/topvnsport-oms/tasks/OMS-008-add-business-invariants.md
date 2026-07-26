---
id: OMS-008
title: "Add business invariants: block deletion với active orders, partial cancel handling"
status: done
priority: high
risk: normal
deadline: null
executor: "@antigravity"
reviewer: "@claude-opus-5"
result_ref: "7f17d6bba3e9f99dbda0525b02870482de1bb02a"
depends_on: []
files:
  - OMS/backend/routers/customers.py
  - OMS/backend/routers/channels.py
  - OMS/backend/routers/orders.py
flows: [customer-delete, order-cancel]
tests:
  - OMS/backend/test_main.py
dispatched: 2026-07-26
in_review: 2026-07-26
predicted_success: high
prediction_factors:
  score: 0.8
deductions:
  - "business_logic: -0.2"
created: 2026-07-25
updated: 2026-07-26
rejections: 3
---

# OMS-008: Add business invariants: block deletion với active orders, partial cancel handling

> Dự án: [[projects/topvnsport-oms/topvnsport-oms]]

## Tiêu chí nghiệm thu (AC)

- [x] Delete customer với active orders → 409 Conflict
- [x] Delete channel với active orders → 409 Conflict
- [x] Partial WMS cancellation → CANCELLATION_PENDING status + error log
- [x] Soft delete thay vì hard delete cho customers

## Verification

- Create customer → create order → delete customer → 409
- Cancel order với 2 fulfillments, 1 fails → status = CANCELLATION_PENDING
- Customer bị delete → `is_deleted=True`, không xóa khỏi DB

## Plan

1. **Database Schema & Migrations**:
   - Update `Customer` SQLAlchemy model (likely in `OMS/backend/models.py`) to add `is_deleted` (Boolean, default False) and `deleted_at` (DateTime, nullable).
   - Generate an Alembic migration script to add these columns.
2. **`OMS/backend/routers/customers.py`**:
   - In the delete endpoint, query if the customer has active orders (`status != 'CANCELLED'`). If yes, return HTTP 409.
   - If no active orders, perform a soft delete by setting `is_deleted=True` and `deleted_at=func.now()` instead of `db.delete(customer)`.
   - Update list/get endpoints to filter out `is_deleted == True`.
3. **`OMS/backend/routers/channels.py`**:
   - In the delete endpoint, check for active orders using this channel. Return HTTP 409 if any exist.
4. **`OMS/backend/routers/orders.py`**:
   - When canceling an order and calling WMS to cancel fulfillments, collect WMS responses. If some fulfillments fail to cancel, set order status to `CANCELLATION_PENDING` and log the error.

## Sub-tasks

- [x] Add active orders check trước khi delete customer
- [x] Add active orders check trước khi delete channel
- [x] Implement partial cancellation handling với error collection
- [x] Add soft delete columns (is_deleted, deleted_at) cho Customer model
- [x] Add tests cho business invariants

## Reference

- Debt file: `docs/TopVNSport - TODO & Technical Debt/oms/02_business_logic_bugs.md`

## Findings từ reviewer
- [x] BLOCKER — migration 0004 dùng server_default=sa.text("0") cho cột Boolean, sinh ra "ALTER TABLE customers ADD COLUMN is_deleted BOOLEAN DEFAULT 0 NOT NULL" và fail trên PostgreSQL (psycopg2.errors.DatatypeMismatch: column "is_deleted" is of type boolean but default expression is of type integer). Hệ quả: oms_backend crash-loop khi khởi động, alembic_version đứng ở 0003_config_value_text, hai cột is_deleted/deleted_at không được tạo, toàn bộ OMS-008 không chạy được trên DB production. Fix: sa.text("false") hoặc sa.false() (đã verify accepted trên Postgres 15). Bổ sung: Boolean là dạng cần cast tường minh, DEFAULT 0 chỉ hợp lệ trên SQLite
- [x] Test gap — 50 test pass nhưng toàn bộ router test chạy SQLite nên không bắt được lỗi. Test Postgres duy nhất (test_upgrade_head_repairs_existing_postgres_schema_without_data_loss) pass giả vì Base.metadata.create_all() đã tạo sẵn is_deleted khiến guard idempotency bỏ qua add_column. Cần thêm case upgrade 0003 → 0004 trên Postgres với bảng customers chưa có cột
- [x] Soft-delete leak — create_order (OMS/backend/routers/orders.py:48) và update_order (OMS/backend/routers/orders.py:242) query models.Customer mà không filter is_deleted, nên vẫn tạo/gán được order mới cho customer đã soft-delete, phá đúng invariant vừa thêm ở AC1
- [x] Ngữ nghĩa "active order" quá rộng — điều kiện status != "CANCELLED" ở cả customers.py và channels.py coi order COMPLETED là active, nên customer/channel chỉ còn đơn đã hoàn tất sẽ không bao giờ xóa được, lệch với ý "active orders" trong AC
- [x] CustomerOut (OMS/backend/schemas/common.py) expose is_deleted/deleted_at ra response API công khai, nên bỏ khỏi schema public

## Findings từ reviewer
- [ ] BLOCKER — delete_channel (OMS/backend/routers/channels.py:118) xóa mềm kênh bằng is_active=False, đồng thời list_channels/retrieve_channel/update_channel (dòng 41, 66, 77, 102) đều filter is_active==True. is_active là field nghiệp vụ đã có sẵn và được expose trên UI admin (OMS/frontend/src/app/(desktop)/channels/page.tsx:397-401, checkbox 'Kích hoạt hoạt động kênh này'), nên khi admin bỏ tick để tạm ngừng một kênh thì kênh lập tức biến mất khỏi list, GET trả 404 và PUT cũng trả 404 — không thể kích hoạt lại qua API, chỉ sửa trực tiếp DB mới cứu được. Kênh tạo mới với is_active=false cũng biến mất ngay sau khi tạo (201 rồi 404). Badge 'Ngừng hoạt động' (page.tsx:199-203) trở thành dead UI. Đã verify live trên API :18101. Lỗi này nằm ngoài scope AC4 (chỉ yêu cầu soft delete cho customers) và mới phát sinh ở afeecf1 — nếu thực sự cần soft delete kênh thì phải thêm cột is_deleted riêng như Customer chứ không overload is_active. Chưa có test nào cover đường reactivate nên 54 test xanh vẫn lọt lỗi này
- [ ] Minor — status CANCELLATION_PENDING chưa được khai báo ở frontend: union Order['status'] (OMS/frontend/src/utils/api.ts:61), getStatusBadgeClass và ORDER_STATUS_STEPS (OMS/frontend/src/app/(desktop)/orders/page.tsx:47-75), nên đơn ở trạng thái này hiển thị badge xám mặc định và không sáng bước nào trên stepper
- [ ] Minor — ALLOWED_TRANSITIONS (OMS/backend/routers/orders.py:26-28) cho phép set CANCELLATION_PENDING thủ công qua endpoint update status mà không có lần gọi WMS nào, nên trạng thái này có thể bị đặt sai ngữ cảnh

## Findings từ reviewer
- [ ] BLOCKER — Regression bảo mật ngoài scope: create_channel/retrieve_channel/update_channel/delete_channel (OMS/backend/routers/channels.py:21,97,108,133) bị hạ từ get_current_user xuống get_optional_user trong d4b39a2, nên cả 4 endpoint gọi được KHÔNG cần credential. Reviewer verify bằng TestClient không override get_current_user: POST=201, GET=200, PUT=200 (đổi được name thành 'hacked'), DELETE=204 (set is_deleted=True) — khách vô danh sửa/xóa được kênh bán. Đối chứng: customers.py giữ get_current_user nên GET/DELETE /customers/{id} trả 401 đúng. Thay đổi này KHÔNG cần thiết để test xanh vì tests/conftest.py:66 đã override get_current_user sẵn, chỉ cần revert 4 dòng về get_current_user. Chưa có test nào cover auth nên 57 test xanh vẫn lọt
- [ ] Minor — ChannelOut (OMS/backend/schemas/common.py:47-48) expose is_deleted/deleted_at ra response API công khai, đi ngược đúng finding đã accepted ở vòng trước (2 field này đã được bỏ khỏi CustomerOut). Nên bỏ khỏi schema public cho nhất quán
- [ ] Minor — nhánh resurrect-on-create trong create_channel (channels.py:23-37 và 49-64) chưa có test nào cover và bị lặp code ở 2 chỗ. Reviewer verify: POST lại code đã soft-delete trả HTTP 200 trong khi route khai báo status_code=201 (lệch OpenAPI), tái dùng đúng id cũ nên order lịch sử của kênh đã xóa bị gắn ngầm sang kênh mới, đồng thời ghi đè name/is_active không cảnh báo
- [ ] Test gap — test_upgrade_head_repairs_existing_postgres_schema_without_data_loss (OMS/backend/tests/test_migrations.py:40) chưa cover channels: Base.metadata.create_all() đã tạo sẵn is_deleted/deleted_at nên guard idempotency bỏ qua add_column, lặp lại đúng pattern pass-giả đã bị flag cho 0004 ở vòng trước. Cần thêm DROP COLUMN channels.is_deleted/deleted_at rồi assert sau upgrade. Test này cũng skip mặc định vì thiếu OMS_TEST_POSTGRES_URL trong env container/CI. Reviewer đã tự verify riêng: migration 0005 chạy sạch trên Postgres 15, sa.false() đúng, backfill row cũ về false, idempotent, không mất dữ liệu
