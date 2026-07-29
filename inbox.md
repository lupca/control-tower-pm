# HÒM THƯ YÊU CẦU CHỜ PHÂN LOẠI (inbox.md)

Nơi lưu trữ các ghi chú thô, ý tưởng, hoặc feedback từ User. Gõ `/ingest` để Agent tự động phân loại những yêu cầu này thành các task chi tiết trong thư mục `projects/`.

> **Dọn ngày 2026-07-28**: Xóa các mục đã hoàn thành (Bug 500 Zalo, FERNET_KEY, WEB-011, OMS-015, IaC findings). IaC sử dụng existing SGs đã config trong AWS, không dùng Terraform defaults. Secrets đã chuyển sang GitHub secrets với `${VAR:?}` fail-fast.

---

## OCR SCAN FINDINGS — 2026-07-25 (chưa có task, còn mở)

### PMI Backend

1. **ALLOWED_SERVICE_KEYS crash at import** (`PMI/backend/routers/audit.py:18`) — HIGH
   - `os.environ["ALLOWED_SERVICE_KEYS"]` raise KeyError nếu không set
   - Variable định nghĩa nhưng không dùng

### OMS Backend

2. **ZaloConfigOut expose secrets** (`OMS/backend/schemas/auth.py`) — HIGH (security)
   - API response chứa `zalo_secret_key`, `zalo_access_token`, `zalo_refresh_token`
   - Cần mask như đã làm với SePay config (OMS-017)

3. **Mutable default arguments** (`OMS/backend/schemas/order.py:73-74`) — HIGH (bug)
   - `items: List[OrderItemOut] = []`, `fulfillment_orders: List[FulfillmentOrderOut] = []`
   - Shared state across instances

### WMS Backend

4. **Mutable default arguments `= []`** (`WMS/backend/schemas.py`) — HIGH
   - `InboundItemCreate.items`, `PickListItemCreate.pick_list_items`, etc. (5+ occurrences)

5. **seed.py resource leak + partial transaction** (`WMS/backend/seed.py`) — HIGH
   - `db.close()` chỉ gọi ở cuối, không có try/finally
   - Commit sau mỗi insert → partial seeded state nếu crash giữa chừng

### Web Frontend

6. **omsHelpers: HTTP error returns empty array** (`web/src/services/sport-api/omsHelpers.ts:10-12`) — MEDIUM
   - `if (!response.ok) return []` — caller không phân biệt được "no channels" vs "API fail"

7. **HomePage Redux selectors no null check** (`web/src/features/home/HomePage.tsx:17-19`) — HIGH
   - `products`, `blogs`, `categories` dùng trực tiếp, crash nếu undefined
   - Line 181: `blogs.slice(0, 3).map(...)` crash khi blogs undefined

---

## Ý TƯỞNG & YÊU CẦU MỚI

1. *Ghi chú (2026-07-21):* Sửa lỗi variant không load được hình ảnh khi kích thước file ảnh quá lớn (lỗi nén ảnh phía frontend). Ưu tiên cao, ảnh hưởng trực tiếp tới chuyển đổi bán hàng.

2. *Ghi chú hệ thống (2026-07-25):* **Process ngoài hệ tự ghi state không hợp lệ vào task file** — 3 lần trong 1 phiên. Đã xử lý bằng thêm câu "report verdict as text, do NOT write status/verdict into the task frontmatter" vào prompt spawn.

3. *Lỗ hổng CI (2026-07-25):* job `wms-backend` trong `.github/workflows/ci.yml` chỉ chạy `python -m py_compile main.py`, **không chạy pytest** — toàn bộ test backend WMS chưa từng chạy trên CI. Chưa mở task.

4. *Vận hành CI/CD (2026-07-25):* ĐỪNG `gh run rerun` một Deploy run — bị kẹt `queued` vĩnh viễn. Cách đúng: `gh run rerun <CI_RUN_ID>` hoặc push commit mới.

5. *Nợ kỹ thuật — PMI CORS wildcard (2026-07-25):* `PMI/backend/main.py:54` dùng `allow_origins=["*"]` + `allow_credentials=True`. Nên siết về danh sách origin tường minh.

6. *INTERNAL_SERVICE_TOKEN fallback (2026-07-25):* `PMI/docker-compose.prod.yml` có fallback `${INTERNAL_SERVICE_TOKEN:-oms_wms_internal_api_key_secret_2026}`. Nếu GitHub secret đã set thì OK, nếu chưa thì dùng placeholder yếu.

---

## Ý TƯỞNG & YÊU CẦU KHÁC (không phải topvnsport)

1. *MPT-001 (money-printer-turbo):* video sinh ra nhưng KHÔNG có tiếng. Task đang `dispatched`. Cần mở task mới điều tra `final-1.mp4` mất track audio.

---

## ✅ ĐÃ HOÀN THÀNH (archive)

> Các mục dưới đây đã xử lý xong, giữ lại để tham khảo. Xóa định kỳ.

- **Bug 500 Zalo OA**: Fixed via OMS-006 → OMS-010 → OMS-011 → OMS-013. Deploy `#30153397265` thành công.
- **FERNET_KEY invalid**: Fixed, GitHub secret đã set đúng format.
- **JWT_SECRET_KEY hardcoded**: Code fix done (OMS-011), tất cả service đọc từ `${JWT_SECRET_KEY:?}`. Rotation optional.
- **WEB-011 CORS duplicate**: Fixed (`fe0ac70`), storefront lấy được data PMI.
- **OMS-015 storefront existing customer**: Fixed (`c1eca2b`), khách cũ đặt được đơn.
- **DEVOPS IaC Phase 1**: Done. RDS Aurora `topvnsport-db` (private), S3, Terraform state. Old cluster deleted.
- **IaC Security (SSH/RDS/EBS)**: N/A — prod dùng existing SGs đã config trong AWS (`sg-0051b179f57a7ad15`, `sg-05043d7ea0114b259`), không dùng Terraform module defaults. RDS cluster mới resolve private IP only.
