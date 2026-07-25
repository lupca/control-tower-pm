# HÒM THƯ YÊU CẦU CHỜ PHÂN LOẠI (inbox.md)

Nơi lưu trữ các ghi chú thô, ý tưởng, hoặc feedback từ User. Gõ `/ingest` để Agent tự động phân loại những yêu cầu này thành các task chi tiết trong thư mục `projects/`.

---

## OCR SCAN FINDINGS — 2026-07-25 (NEW only, đã loại bỏ findings trùng với tasks)

### PMI Backend (2 NEW)

1. **ALLOWED_SERVICE_KEYS crash at import** (`PMI/backend/routers/audit.py:17-18`) — HIGH
   - `os.environ["ALLOWED_SERVICE_KEYS"]` raise KeyError nếu không set
   - Variable định nghĩa nhưng không dùng

2. **alembic.ini empty sqlalchemy.url** (`PMI/backend/alembic.ini:5`) — HIGH
   - Config trống, migration sẽ fail

### OMS Backend (4 NEW)

3. **Config update unrestricted keys** (`OMS/backend/routers/config.py:62-73`) — HIGH
   - Cho phép modify bất kỳ config key nào (kể cả database_url)

4. **ZaloConfigOut expose secrets** (`OMS/backend/schemas/auth.py:14-19`) — HIGH (security)
   - API response chứa `zalo_secret_key`, `zalo_access_token`, `zalo_refresh_token`

5. **Mutable default arguments** (`OMS/backend/schemas/order.py:63-70`) — HIGH (bug)
   - `items: List[OrderItemOut] = []` — shared state across instances

6. **Concurrency: config update** (`OMS/backend/routers/config.py:55-74`) — MEDIUM
   - Lost updates khi concurrent PUT

### WMS Backend (2 NEW)

7. **Mutable default arguments `= []`** (`WMS/backend/schemas.py`) — HIGH
   - InboundItemCreate.items, PickListItemCreate.pick_list_items, etc.

8. **seed.py resource leak + partial transaction** (`WMS/backend/seed.py`) — HIGH
   - db.close() không được gọi nếu exception
   - Commit sau mỗi insert → partial seeded state

### Web Frontend (4 NEW)

9. **omsHelpers: HTTP error returns null** (`web/src/services/sport-api/omsHelpers.ts:14-16`) — HIGH
   - Trả `null` thay vì throw → caller không phân biệt được "not found" vs "API fail"

10. **popupService emit() không catch exception** (`web/src/components/ui/popupService.ts:81-84`) — HIGH
    - Listener throw → crash app hoặc reject promise

11. **HomePage Redux selectors undefined** (`web/src/features/home/HomePage.tsx:145-157`) — HIGH
    - `products`, `blogs`, `categories` có thể undefined → crash khi gọi `.filter()`

12. **imageByVisualOption ignores tier2** (`ProductDetailPage.tsx:135-157`) — MEDIUM (bug)
    - Early return sau tier1 → tier2 media không bao giờ được xử lý

---

## Ý TƯỞNG & YÊU CẦU MỚI:

1. *Ghi chú (2026-07-21):* Sửa lỗi variant không load được hình ảnh khi kích thước file ảnh quá lớn (lỗi nén ảnh phía frontend). Cái này ưu tiên cao, ảnh hưởng trực tiếp tới chuyển đổi bán hàng.

