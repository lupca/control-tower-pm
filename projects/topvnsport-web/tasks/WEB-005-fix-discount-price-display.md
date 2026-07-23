---
id: WEB-005
title: "Fix discount price display on product detail page"
status: in-review
priority: high
created: 2026-07-24
deadline: 2026-07-25
in_review: 2026-07-24
updated: 2026-07-24
executor: "@dev"
reviewer: null
result_ref: "055fe30"
tests:
  - "web/src/__tests__/ProductCard.test.tsx"
  - "web/src/__tests__/useComputedPrice.test.ts"
  - "web/src/__tests__/productMappers.test.ts"
  - "e2e_tests/tests/test_promotion_full_flow.py"
files:
  - "web/src/components/ProductDetailPage.tsx"
  - "web/src/components/product-detail/ProductPurchaseSection.tsx"
  - "web/src/types.ts"
related:
  - "web/src/components/ProductCard.tsx"
  - "web/src/hooks/useComputedPrice.ts"
  - "PMI/backend/services/promotion_service.py"
tags: [bug, promotion, frontend]
risk: medium
predicted_success: 0.85
---

# WEB-005: Fix discount price display on product detail page

## Problem
Trang chi tiết sản phẩm (`ProductDetailPage`) fix cứng việc hiển thị giảm giá dựa trên `product.salePrice` (giá sale tĩnh). Khi áp dụng mã giảm giá động (promotion code), API trả về `computedPrice`, `originalPrice`, `hasActivePromotion`, `percentageDiscount` — nhưng frontend bỏ qua các trường này, dẫn đến giao diện không hiển thị badge "TIẾT KIỆM X%" và giá gốc gạch ngang.

## Root Cause
- `ProductDetailPage.tsx`: Logic tính `displayBasePrice` chỉ dùng `product.salePrice`, không check `computedPrice`.
- `ProductPurchaseSection.tsx`: Props interface không có `hasDiscount`/`discountPercent`; điều kiện render badge dựa trên `product.salePrice` thay vì props.

## Solution Implemented
1. **ProductDetailPage.tsx** (lines 80-95):
   - Ưu tiên `matchedVariant?.computedPrice ?? product.computedPrice` cho giá hiển thị.
   - Tính `hasDiscount` từ `hasActivePromotion` flag HOẶC so sánh giá.
   - Fallback tính `discountPercent` khi API không trả về.
   - Truyền `hasDiscount` + `discountPercent` xuống child component.

2. **ProductPurchaseSection.tsx**:
   - Thêm `hasDiscount: boolean` và `discountPercent: number` vào Props interface.
   - Replace `product.salePrice` conditions → `hasDiscount` prop.

## Acceptance Criteria

- [ ] **AC1**: Sản phẩm có mã giảm giá active → hiển thị giá gốc gạch ngang + badge "TIẾT KIỆM X%".
- [ ] **AC2**: Sản phẩm KHÔNG có promotion → không hiển thị badge, chỉ hiển thị giá bán.
- [ ] **AC3**: Variant-level promotion: chọn variant khác nhau → giá + badge cập nhật tương ứng.
- [ ] **AC4**: Kết hợp stringing price: `displayOriginalPrice + stringPrice` phải gạch ngang đúng.
- [ ] **AC5**: Consistency: logic tương đương `ProductCard.tsx` (đang hoạt động đúng).

## Test Plan

### Unit Tests (existing)
```bash
cd /home/lupca/projects/topvnsport/web
pnpm test -- --grep "computedPrice|discount|promotion"
```

### Manual Verification
1. Tạo promotion cho sản phẩm X trong PMI → lưu.
2. Mở `/products/{slug}` trên web → verify badge + giá gạch ngang.
3. Chọn variant khác (nếu có) → verify giá update.
4. Xóa promotion → refresh → verify badge biến mất.

### E2E (optional)
```bash
cd /home/lupca/projects/topvnsport
pytest e2e_tests/tests/test_promotion_full_flow.py -k "product_detail"
```

## Risk Assessment
- **Regression risk**: Medium — `ProductPurchaseSection` được dùng bởi 1 parent (`ProductDetailPage`), nhưng logic giá ảnh hưởng UX mua hàng.
- **Blast radius**: 697 nodes (2-hop), nhưng chỉ 2 files thực sự thay đổi logic render.
- **Mitigation**: Run existing tests + manual QA trên staging trước khi merge.

## Audit Log
- 2026-07-24: Task created from inbox item #6, fix implemented by @dev (uncommitted).
