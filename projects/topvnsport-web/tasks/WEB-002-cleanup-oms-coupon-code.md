---
id: WEB-002
title: "Xóa code OMS coupon thừa từ WEB-001 lần 1"
status: done
priority: low
risk: normal
deadline: null
executor: "@gpt-5.6-luna"
dispatched: 2026-07-22
in_review: 2026-07-22
done: 2026-07-22
reviewer: "@claude-opus"
result_ref: "topvnsport@main (commit 3380533)"
depends_on: []
predicted_success: high
prediction_factors:
  blast_radius: low
  hub_nodes_hit: 0
  bridge_nodes_hit: 0
  missing_tests: false
  historical_similarity: null
files:
  - OMS/backend/models.py (xóa Promotion, PromotionUsage classes; xóa Order.discount_amount, Order.promotion_code)
  - OMS/backend/schemas/promotion.py (xóa toàn bộ file)
  - OMS/backend/schemas/__init__.py (xóa promotion imports)
  - OMS/backend/main.py (xóa promotion endpoints)
  - web/src/components/CartModal.tsx (xóa coupon input section)
  - e2e_tests/tests/test_promotions.py (xóa toàn bộ file - test OMS coupon)
flows: []
tests:
  - OMS/backend/test_main.py (verify không regression)
  - e2e_tests/tests/test_full_flow.py (verify checkout vẫn hoạt động)
created: 2026-07-22
updated: 2026-07-22
---

# WEB-002: Xóa code OMS coupon thừa từ WEB-001 lần 1

> Dự án: [[projects/topvnsport-web/topvnsport-web]]

## Bối cảnh

WEB-001 lần 1, executor @antigravity-3.6 đã implement **order-level coupon system trong OMS** thay vì product-level promotion trong PMI như AC yêu cầu. Code này:
- Nằm sai hệ thống (OMS thay vì PMI)
- Sai loại (order-level coupon thay vì product-level promotion)
- Không thuộc scope của WEB-001

WEB-001 đã được implement lại đúng trong PMI và pass review. Code OMS coupon là rác cần dọn.

## Tiêu chí nghiệm thu (AC)

### OMS Backend
- [x] Xóa `Promotion` class trong `OMS/backend/models.py` (line 57-73)
- [x] Xóa `PromotionUsage` class trong `OMS/backend/models.py` (line 76-84)
- [x] Xóa `discount_amount` và `promotion_code` fields trong `Order` class (`OMS/backend/models.py`)
- [x] Xóa file `OMS/backend/schemas/promotion.py`
- [x] Xóa promotion imports trong `OMS/backend/schemas/__init__.py`
- [x] Xóa promotion endpoints trong `OMS/backend/main.py`

### Web Frontend
- [x] Xóa coupon input section trong `web/src/components/CartModal.tsx`

### E2E Tests
- [x] Xóa file `e2e_tests/tests/test_promotions.py` (file này test OMS coupon, không phải PMI promotion)

### Verification
- [x] `OMS/backend/test_main.py` pass (không regression)
- [x] `e2e_tests/tests/test_full_flow.py` pass (checkout vẫn hoạt động)
- [x] `e2e_tests/tests/test_promotion_full_flow.py` pass (PMI promotion vẫn OK)

## Plan

### Step 1: OMS Backend Models
1. Mở `OMS/backend/models.py`
2. Xóa class `Promotion` (line 57-73)
3. Xóa class `PromotionUsage` (line 76-84)
4. Trong class `Order`, xóa fields `discount_amount` và `promotion_code`
5. Giữ nguyên `updated_at` (đã được restore trong WEB-001 fix)

### Step 2: OMS Backend Schemas
1. Xóa file `OMS/backend/schemas/promotion.py`
2. Mở `OMS/backend/schemas/__init__.py`, xóa imports liên quan đến promotion

### Step 3: OMS Backend Main
1. Mở `OMS/backend/main.py`
2. Tìm và xóa tất cả endpoints liên quan đến `/promotions` hoặc `/apply-promotion`
3. Xóa imports của promotion schemas/models nếu có

### Step 4: Web Frontend
1. Mở `web/src/components/CartModal.tsx`
2. Tìm và xóa phần UI nhập coupon code (input + button apply)
3. Xóa state/logic xử lý coupon

### Step 5: E2E Tests
1. Xóa file `e2e_tests/tests/test_promotions.py` (test OMS coupon)
2. **KHÔNG XÓA** `e2e_tests/tests/test_promotion_full_flow.py` (test PMI)

### Step 6: Verify
1. Chạy `OMS/backend/test_main.py` — verify không regression
2. Chạy `e2e_tests/tests/test_full_flow.py` — verify checkout OK
3. Chạy `e2e_tests/tests/test_promotion_full_flow.py` — verify PMI promotion OK

## Sub-tasks

- [x] 1. Xóa Promotion, PromotionUsage classes trong OMS models.py
- [x] 2. Xóa Order.discount_amount, Order.promotion_code
- [x] 3. Xóa OMS/backend/schemas/promotion.py
- [x] 4. Cleanup OMS/backend/schemas/__init__.py
- [x] 5. Xóa promotion endpoints trong OMS/backend/main.py
- [x] 6. Xóa coupon UI trong CartModal.tsx
- [x] 7. Xóa e2e_tests/tests/test_promotions.py
- [x] 8. Verify tests pass

## Notes

- **KHÔNG XÓA** bất cứ gì trong `PMI/` — đó là promotion module đúng
- **KHÔNG XÓA** `e2e_tests/tests/test_promotion_full_flow.py` — đó test PMI promotion
- Nếu có migration file cho OMS promotion tables, cần tạo migration đảo ngược (hoặc đánh dấu skip nếu tables chưa được tạo trên prod)
