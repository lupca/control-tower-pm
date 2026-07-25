---
id: PMI-012
title: "Endpoint /public/products & /public/products/{slug} chưa trả giá đã áp dụng khuyến mãi"
status: done
priority: urgent
risk: high
created: 2026-07-25
executor: "@gpt-5.6-luna-high"
reviewer: "@claude-opus"
result_ref: "3f29743"
depends_on: []
files:
  - PMI/backend/routers/public.py
flows: [get_public_products, get_public_product]
tests:
  - PMI/backend/tests/test_public.py
dispatched: 2026-07-25
in_review: 2026-07-25
predicted_success: medium
prediction_factors:
  score: 0.5
  deductions:
    - "blast_radius: 142 files impacted (2-hop), >15 (-0.5 cumulative)"
created: 2026-07-25
updated: 2026-07-25
---

# PMI-012: Endpoint `/public/products` & `/public/products/{slug}` chưa trả giá đã áp dụng khuyến mãi

> Dự án: [[projects/topvnsport-pmi/topvnsport-pmi]]

## Bối cảnh — ROOT CAUSE THẬT SỰ của báo cáo gốc

User báo cáo ban đầu: đã tạo khuyến mãi giảm 20% cho tất cả sản phẩm nhưng trang bán hàng (`/product/<slug>`) vẫn không hiển thị giảm giá. `PMI-011` đã fix đúng 1 bug thật (backend promotion-matching logic), `WEB-005` đã fix đúng chỗ frontend đọc field `computedPrice`/`hasActivePromotion` — nhưng **cả 2 fix đều KHÔNG có tác dụng với trang thật**, vì đã verify trực tiếp bằng browser (2026-07-25):

1. Trang `http://localhost:13103/product/vot-lining-e2e-otp-test-925dcbf1` vẫn chỉ hiện giá gốc `1.250.000đ`, không có giá gạch ngang/badge giảm giá.
2. Network trace xác nhận storefront gọi `GET http://localhost:18100/public/products?limit=100` để lấy dữ liệu sản phẩm (KHÔNG gọi `/api/computed-prices/bulk` hay bất kỳ endpoint promotion nào).
3. Response thật của `/public/products` cho sản phẩm này:
   ```json
   "variants":[{"id":7391,"product_id":7413,"tier_1_option":null,"tier_2_option":null,
                "sku_code":"SKU-E2E-OTP-LINING-925dcbf1","price":1250000.0,
                "barcode":null,"default_cost_price":null,"default_tax_rate":null}]
   ```
   Không có `computed_price`/`has_active_promotion`/`original_price`/`percentage_discount` — các field mà `ProductDetailPage`/`ProductCard` (đã fix ở WEB-005) cần để hiển thị giảm giá.

**Kết luận**: `get_public_products`/`get_public_product` (`PMI/backend/routers/public.py`) là route thật sự storefront dùng để lấy giá — route này CHƯA BAO GIỜ tích hợp với hệ thống promotion (`promotion_service.py`) mà PMI-011 vừa fix. Đã có sẵn hàm `compute_product_prices` (L114-121) được gọi bởi cả `get_public_products` và `get_public_product`, nhưng theo OCR pre-scan, hàm này chỉ dùng để tính `min_price`/`max_price` phục vụ filter theo khoảng giá — KHÔNG gắn `computed_price`/`has_active_promotion` vào response từng variant. `PublicVariantResponse`/`PublicProductResponse` schema cũng không khai báo các field này.

## Tiêu chí nghiệm thu (AC)
- [ ] **AC1**: `GET /public/products` trả về mỗi variant kèm `computed_price`, `has_active_promotion`, `original_price` (nếu có promotion active) — dùng logic tính giá đã có sẵn trong `promotion_service.py` (không viết lại logic tính discount).
- [ ] **AC2**: `GET /public/products/{slug}` (hoặc route chi tiết tương đương `get_public_product`) trả cùng các field trên cho toàn bộ variant của sản phẩm.
- [ ] **AC3**: Verify TRỰC TIẾP qua browser: mở `http://localhost:13103/product/vot-lining-e2e-otp-test-925dcbf1` (hoặc sản phẩm bất kỳ có promotion active) sau khi fix — phải thấy giá gạch ngang + badge giảm giá, KHÔNG chỉ verify qua unit test.
- [ ] **AC4**: Không phá vỡ filter theo `min_price`/`max_price` hiện có (đang dùng `compute_product_prices` để filter) — 100% test trong `tests:` vẫn xanh.
- [ ] **AC5**: Không regression hiệu năng nghiêm trọng — nếu tích hợp promotion cho toàn bộ list (limit=100) gây N+1 query rõ rệt, phải dùng cách tính hàng loạt (`get_bulk_computed_prices`/`recompute_variant_prices` kiểu batch), không gọi tính giá riêng lẻ từng variant trong loop.

## Pre-scan findings (OCR)
`ocr scan --path PMI/backend/routers/public.py` (2026-07-25) — 5 findings:
- **[high][performance]** N+1 query trong tính category display name (L438-449, và 1 finding tương tự khác) — không liên quan trực tiếp AC, ghi nhận nhưng không bắt buộc fix trong task này.
- **[medium][maintainability]** "Price calculation is performed twice - once in `compute_product_prices` and again in post-filtering" — xác nhận đúng: `compute_product_prices` tồn tại nhưng dùng cho mục đích khác (filter), không phải để expose promotion price. Executor cần đọc kỹ hàm này trước khi sửa, tái sử dụng thay vì viết hàm tính giá thứ 2.
- **[medium][security]** Page limit validation không chặn integer overflow — ngoài phạm vi.
- **[medium][performance]** Category lookup fetch lại toàn bộ categories thay vì dùng dữ liệu đã preload — ngoài phạm vi, chỉ ghi nhận.

## Verification
- `cd /home/lupca/projects/topvnsport && docker compose -f PMI/docker-compose.yml exec -e BYPASS_TESTCONTAINERS=true api pytest tests/test_public.py -v` → phải pass, có thêm test case cho computed_price/has_active_promotion.
- **Bắt buộc thêm**: verify qua browser thật (không chỉ pytest) theo AC3 — đây là bug đã sống sót qua 2 task trước chỉ vì không ai verify bằng browser thật.

## Plan

1. **Đọc lại `get_bulk_computed_prices(db, variant_ids)`** trong `PMI/backend/services/promotion_service.py` (đã tồn tại, dùng bởi endpoint `/api/computed-prices/bulk` mà PMI-011 vừa fix) — hàm này nhận list variant_ids, trả dict keyed theo variant id với `computed_price`/`original_price`/`has_active_promotion`/`percentage_discount`. Đây chính là hàm cần tái sử dụng, KHÔNG viết lại logic tính discount.
2. **Trong `get_public_products`** (L159-314): sau khi query xong danh sách product+variant (đã có sẵn), gom toàn bộ `variant.id` trong page hiện tại thành 1 list, gọi `get_bulk_computed_prices(db, variant_ids)` **1 lần duy nhất** (không loop từng variant — tránh N+1, đúng AC5), rồi merge kết quả vào `PublicVariantResponse` khi serialize.
3. **Trong `get_public_product`** (L318-410, lấy chi tiết 1 sản phẩm): tương tự, gom variant_ids của sản phẩm đó, gọi `get_bulk_computed_prices` 1 lần.
4. **Cập nhật `PublicVariantResponse`** (L41-51): thêm field `computed_price: Optional[float]`, `has_active_promotion: bool = False`, `original_price: Optional[float]`, `percentage_discount: Optional[float]` — optional/default để không phá vỡ contract hiện có cho client khác (nếu có).
5. **`compute_product_prices`** (L114-121, dùng để tính min/max cho filter): giữ nguyên, không động vào — đây là logic khác (lọc theo khoảng giá), không phải nguồn cấp `computed_price` cho response.
6. Viết test mới trong `test_public.py`: tạo 1 promotion active scope "tất cả sản phẩm", gọi `GET /public/products` và `GET /public/products/{slug}` → assert `computed_price`/`has_active_promotion` đúng cho sản phẩm test.
7. **Bắt buộc**: sau khi test pass, verify lại bằng browser thật tại `http://localhost:13103/product/vot-lining-e2e-otp-test-925dcbf1` (hoặc sản phẩm có promotion tương đương) — chụp lại kết quả xác nhận giá gạch ngang/badge hiển thị đúng. Đây là AC3, không được coi task xong chỉ vì unit test xanh (bài học từ PMI-011/WEB-005 đã "pass" nhưng không giải quyết triệu chứng gốc).

## Sub-tasks
- [ ] Đọc `compute_product_prices` + `PublicVariantResponse`/`PublicProductResponse` để xác định điểm nối với `promotion_service.get_bulk_computed_prices`/`get_variant_computed_price`.
- [ ] Thêm field `computed_price`/`has_active_promotion`/`original_price` vào schema + populate trong `get_public_products` và `get_public_product`, dùng batch computation (tránh N+1).
- [ ] Viết/bổ sung test trong `test_public.py` cho case có promotion active.
- [ ] Verify qua browser thật tại trang storefront (AC3) — không được bỏ qua bước này.
