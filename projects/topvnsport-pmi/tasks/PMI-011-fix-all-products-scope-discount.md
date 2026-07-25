---
id: PMI-011
title: "Fix khuyến mãi scope 'tất cả sản phẩm' (giảm 20%) không được áp dụng"
status: done
priority: high
risk: high
created: 2026-07-24
executor: "@antigravity-3.6-high"
reviewer: "@antigravity"
result_ref: "2f7d238"
depends_on: []
files:
  - PMI/backend/services/promotion_service.py
flows: [create_promotion, update_promotion, activate_promotion, get_bulk_prices, preview_promotion]
tests:
  - PMI/backend/tests/unit/test_promotions_compute.py
  - PMI/backend/tests/unit/test_promotions_scope_stress.py
  - PMI/backend/tests/unit/test_tier5_adversarial_backend.py
dispatched: 2026-07-25
in_review: 2026-07-25
predicted_success: low
prediction_factors:
  score: 0.3
  deductions:
    - "blast_radius: 104 files impacted, >15 (-0.5 cumulative)"
    - "hits hub/bridge node: calculate_discount (hub+bridge), eval_variant_promotion_match (hub) (-0.2)"
created: 2026-07-24
updated: 2026-07-25
rejections: 2
---

# PMI-011: Fix khuyến mãi scope "tất cả sản phẩm" (giảm 20%) không được áp dụng

> Dự án: [[projects/topvnsport-pmi/topvnsport-pmi]]

## Bối cảnh
User báo cáo: đã tạo khuyến mãi giảm 20% cho toàn bộ sản phẩm nhưng web bán hàng (storefront) vẫn không hiển thị/áp dụng giảm giá. Task này liên quan đến `WEB-005` (đã fix hiển thị giá trên `ProductDetailPage`) nhưng khác gốc rễ: nghi ngờ nằm ở logic backend PMI đánh giá scope khuyến mãi (`matches_single_scope` / `eval_variant_promotion_match`) hoặc tính discount (`calculate_discount`), không phải lỗi hiển thị frontend.

## Tiêu chí nghiệm thu (AC)
- [x] **AC1**: Tạo promotion với scope = tất cả sản phẩm (ALL_PRODUCTS/không giới hạn category-product-variant), `percentage=20`, `status=active` → `eval_variant_promotion_match` trả về `True` cho MỌI variant hiện có.
- [x] **AC2**: `calculate_discount` trả về `computed_price` < `original_price` đúng 20% cho promotion trên (không trả `0`/`None`/NaN).
- [x] **AC3**: `get_bulk_computed_prices` (endpoint `/promotions/bulk-prices`) trả về `hasActivePromotion=true` + `computedPrice` đã giảm cho toàn bộ sản phẩm nằm trong scope.
- [x] **AC4**: Không phá vỡ các scope khác (category-specific, product-specific, variant-specific, exclusion rules) — 100% test hiện có trong `tests:` vẫn xanh. *(NLP `parse_promotion_intent` edge-case đã DESCOPE theo quyết định User — xem `## Quyết định phạm vi`)*
- [x] **AC5**: Root cause được xác định và ghi rõ trong `## Root Cause` bên dưới trước khi merge fix (không patch mù).

## Pre-scan findings (OCR)
`ocr scan --path PMI/backend/services/promotion_service.py` (2026-07-24) — 9 findings, liên quan trực tiếp AC:
- **[high][bug]** `build_category_ancestor_map` (L33-41): cycle detection có lỗ hổng — category tự tham chiếu chính nó hoặc cycle trực tiếp giữa 2 node có thể gây vòng lặp vô hạn. Nếu promotion scope dùng category "gốc"/"tất cả" trỏ vào 1 category bị lỗi cấu trúc này, `matches_single_scope` có thể không bao giờ trả về đúng.
- **[medium][maintainability]** `eval_variant_promotion_match` (L99-139): dùng nhiều `isinstance`/`getattr` để xử lý `Union[Promotion, dict, PromotionCreate]` — dễ silent-fail (vd `scopes` rỗng do sai type check) khiến promotion không match với bất kỳ variant nào.
- **[medium][bug]** `calculate_discount`: chuyển đổi số giữa `float`/`int`/`Decimal` nhiều lần — có thể gây sai lệch % giảm giá.
- **[medium][bug]** `get_variant_computed_price` (L411-415): nếu variant ID không phải số, trả `None` thay vì fallback — có thể khiến 1 số sản phẩm bị bỏ sót khỏi discount hàng loạt.

Executor nên kiểm tra kỹ 2 điểm đầu trước — khớp trực tiếp với triệu chứng "tạo giảm giá cho TẤT CẢ sản phẩm nhưng không hoạt động" (scope "tất cả" thường implement qua category gốc hoặc scope rỗng/wildcard).

## Verification
- `cd /home/lupca/projects/topvnsport && docker compose -f PMI/docker-compose.yml exec -e BYPASS_TESTCONTAINERS=true api pytest tests/unit/test_promotions_compute.py tests/unit/test_promotions_scope_stress.py tests/unit/test_tier5_adversarial_backend.py -v` → 100% pass (36/36 passed)
- `cd /home/lupca/projects/topvnsport && docker compose -f PMI/docker-compose.yml exec -e BYPASS_TESTCONTAINERS=true api pytest tests/unit/ -v` → 100% pass (101/101 passed)

## Root Cause
1. **Scope Rỗng (`scopes=[]`) Bị Loại Trừ Silently**: Trong `eval_variant_promotion_match` (`promotion_service.py`), câu lệnh `if not scopes: return False` khiến mọi promotion tạo ra không có danh sách scope giới hạn (scope = tất cả sản phẩm / unrestricted) đều bị đánh giá match = `False` cho 100% variant trong hệ thống.
2. **Khuyết Nhánh `ALL_PRODUCTS` trong Scope Matcher**: `matches_single_scope` chỉ kiểm tra `scope_type == "ALL"`. Khi payload truyền `ALL_PRODUCTS` hoặc alias tương tự, matcher trả về `False` do không khớp chính xác chuỗi `"ALL"`.
3. **Intent Parser Bị Match Nhầm Keyword**: Trong `parse_promotion_intent`, keyword `"sản phẩm"` được kiểm tra trước khi kiểm tra ý định "tất cả" / "toàn bộ" / "all products", dẫn đến prompt "giảm 20% cho tất cả sản phẩm" bị gán nhầm thành `ScopeType.PRODUCT` với target_id mặc định `"10"`.
4. **Router Endpoint Validation Strict**: Endpoint `POST /api/promotions` trong `routers/promotions.py` sử dụng `ScopeType(st_val.upper())` mà không xử lý alias `ALL_PRODUCTS` / `ALL_PRODUCT` chuyển sang `ScopeType.ALL`.

## Plan

**Giả thuyết chính (ưu tiên kiểm tra trước, dựa trên OCR pre-scan + đọc source `promotion_service.py`):**

`eval_variant_promotion_match` (L99-139) có đoạn:
```python
if hasattr(promo, "scopes"):
    scopes = promo.scopes or []
elif isinstance(promo, dict):
    scopes = promo.get("scopes", [])
else:
    scopes = []

if not scopes:
    return False   # <-- nghi vấn chính
```
Nếu UI/API biểu diễn "áp dụng cho tất cả sản phẩm" bằng cách **không tạo scope nào** (`scopes=[]`, tức "không giới hạn" = "áp dụng hết"), thì dòng `if not scopes: return False` sẽ khiến MỌI variant bị loại — đúng khớp triệu chứng "tạo giảm giá cho tất cả sản phẩm nhưng không hoạt động". Đây là silent-fail, không phải infinite loop, nên khớp hơn so với vấn đề cycle-detection ở `build_category_ancestor_map`.

1. **Xác nhận biểu diễn scope "tất cả sản phẩm"**: đọc `PMI/backend/schemas/promotion.py::PromotionScopeSchema` + `PMI/frontend` (nơi tạo promotion) để xác nhận "tất cả sản phẩm" gửi lên API là `scopes=[]` hay 1 scope đặc biệt (vd `scope_type="ALL"`).
2. **Nếu xác nhận là case `scopes=[]`**: sửa `eval_variant_promotion_match` để coi `scopes=[]` (không có exclusion/inclusion nào) = match tất cả, thay vì `return False`. Cẩn thận: không phá vỡ logic Phase 1 Exclusion / Phase 2 Inclusion hiện có cho các promotion có scope cụ thể.
3. **Nếu giả thuyết 1 sai** (API có 1 scope type riêng cho "tất cả"): kiểm tra `matches_single_scope` (L49-96) xem có xử lý đúng type đó không (có thể case `ScopeType` thiếu nhánh cho "ALL").
4. **Kiểm tra phụ `calculate_discount`**: xác nhận % giảm giá tính đúng SAU KHI scope match đã fix (đổi kiểu số `float`/`Decimal` theo OCR finding — chỉ sửa nếu có bằng chứng cụ thể gây sai số, tránh refactor lan man ngoài scope).
5. Ghi root cause thật sự xác nhận được vào `## Root Cause` (bắt buộc theo AC5).
6. Bổ sung 1 test case mới trong `test_promotions_scope_stress.py` (hoặc `test_promotions_compute.py`) cho promotion `scopes=[]`/"tất cả sản phẩm" nếu chưa tồn tại case này.
7. Chạy toàn bộ `tests:` — xác nhận không regression các scope cụ thể khác (category/product/variant/exclusion).

**Ngoài phạm vi** (không sửa trong task này, chỉ ghi nhận nếu gặp): cycle-detection ở `build_category_ancestor_map`, global lock performance ở `recompute_variant_prices`, regex parsing ở `parse_promotion_intent` — đây là các OCR finding khác không liên quan trực tiếp đến triệu chứng đang báo cáo.

## Sub-tasks
- [x] Xác định root cause cụ thể (category cycle / type-check silent fail / discount calc) — ghi vào `## Root Cause`.
- [x] Fix function liên quan trong `promotion_service.py`.
- [x] Bổ sung test case cho scope "tất cả sản phẩm" nếu chưa có (kiểm tra `test_promotions_scope_stress.py`).
- [x] Chạy full test suite `tests:` — đảm bảo không regression các scope khác.

## Findings từ reviewer
- [x] ALL_PRODUCTS/ALL_PRODUCT are rejected by PromotionScopeSchema with 422 before the router alias branch can run
- [x] parse_promotion_intent widens mixed category/variant phrases to global ALL
- [x] empty scope and explicit ALL have inconsistent specificity 0 vs 1
- [x] AC3 names /promotions/bulk-prices but only /api/computed-prices/bulk exists
- [x] regression tests miss alias API paths, mixed-scope intent, and empty-vs-ALL tie-breaking

## Findings từ reviewer
- [ ] AC3 fails: GET /promotions/bulk-prices returns 405 (only POST registered)
- [x] ~~AC4 fails: product ID + variant keyword now parses as fabricated VARIANT:101 instead of PRODUCT:20 - new regression introduced by round-2 reordering~~ — **DESCOPED theo quyết định User (2026-07-25)**, xem `## Quyết định phạm vi (User, 2026-07-25)`.
- [ ] regression tests do not cover either failure — chỉ còn áp dụng cho GET route (AC3), không cần test cho case NLP đã descope.
- [x] unit 104/104 pass
- [x] both E2E failures remain external Access token invalid, not a PMI-011 regression

## Quyết định phạm vi (User, 2026-07-25)
- **`parse_promotion_intent` (tính năng NLP tự động tạo phiếu giảm giá từ câu tiếng Việt/Anh) bị loại khỏi phạm vi task này** theo quyết định trực tiếp của User: "Cái mục tự động tạo phiếu giảm giá thì kệ nó đi. Cái đó chủ yếu là người nhập mà quan tâm làm gì." → finding HIGH vòng 2 (regression `VARIANT:101` khi prompt có cả product ID + từ "biến thể") **KHÔNG cần fix trong PMI-011**. Không revert code đã đổi ở `a7e9472`, chỉ không tiếp tục đào sâu/fix thêm parser này.
- **Chỉ còn 1 việc bắt buộc phải fix**: AC3 — `GET /promotions/bulk-prices` trả `405` (thiếu đăng ký GET method, chỉ có POST).
- **Ưu tiên hàng đầu sau khi PMI-011 đóng**: `WEB-006` — xác nhận storefront (`/web`) thực sự HIỂN THỊ được thông tin giảm giá. Đây là mục tiêu gốc của toàn bộ yêu cầu ban đầu (user report), quan trọng hơn các edge-case NLP parser.
