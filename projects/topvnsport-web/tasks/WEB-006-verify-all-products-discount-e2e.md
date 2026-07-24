---
id: WEB-006
title: "Verify end-to-end: giảm giá scope 'tất cả sản phẩm' hiển thị đúng trên storefront"
status: todo
priority: high
risk: normal
created: 2026-07-24
executor: null
reviewer: null
result_ref: null
depends_on: [PMI-011]
files:
  - web/src/components/ProductCard.tsx
  - web/src/components/ProductDetailPage.tsx
  - web/src/hooks/useComputedPrice.ts
flows: [catalog-add-to-cart, home-add-to-cart]
tests:
  - web/src/__tests__/ProductCard.test.tsx
  - web/src/__tests__/useComputedPrice.test.ts
  - e2e_tests/tests/test_promotion_full_flow.py
dispatched: null
in_review: null
predicted_success: high
prediction_factors:
  score: 0.7
  deductions:
    - "hits hub/bridge node not applicable (verification task, no core logic change expected)"
created: 2026-07-24
updated: 2026-07-24
---

# WEB-006: Verify end-to-end giảm giá scope "tất cả sản phẩm" trên storefront

> Dự án: [[projects/topvnsport-web/topvnsport-web]]

## Bối cảnh
Phụ thuộc `PMI-011` (fix root cause backend: promotion scope "tất cả sản phẩm" không match/tính discount đúng). `WEB-005` đã fix hiển thị giá trên `ProductDetailPage` (bug hiển thị khác, đã qua review). Task này verify rằng SAU KHI PMI-011 merge, storefront thực sự hiển thị/áp dụng đúng giảm giá ở TẤT CẢ các nơi hiển thị giá — không chỉ trang chi tiết sản phẩm.

## Tiêu chí nghiệm thu (AC)
- [ ] **AC1**: Trang danh sách sản phẩm (`CatalogPage`/`HomePage` dùng `ProductCard`) hiển thị giá gạch ngang + badge giảm giá cho MỌI sản phẩm khi có promotion scope "tất cả sản phẩm" active.
- [ ] **AC2**: Trang chi tiết sản phẩm (`ProductDetailPage`, đã fix ở WEB-005) tiếp tục hiển thị đúng sau khi backend fix — không regression.
- [ ] **AC3**: Thêm vào giỏ hàng (`buildDefaultCartItem` trong `cartSlice.ts`) dùng đúng giá đã giảm, không phải giá gốc.
- [ ] **AC4**: Test `test_promotion_full_flow.py` (E2E) pass với case scope "tất cả sản phẩm".
- [ ] **AC5**: Nếu bất kỳ AC nào fail → không phải lỗi backend (đã cover ở PMI-011), phải mô tả cụ thể lỗi phía frontend còn sót lại.

## Verification
- `cd /home/lupca/projects/topvnsport/web && pnpm test -- --grep "ProductCard|computedPrice"` → 100% pass
- `cd /home/lupca/projects/topvnsport && pytest e2e_tests/tests/test_promotion_full_flow.py -v` → 100% pass
- Manual: sau khi PMI-011 active 1 promotion scope="tất cả sản phẩm" 20% → mở trang chủ, trang danh mục, trang chi tiết, thêm giỏ hàng → verify giá giảm nhất quán ở cả 4 nơi.

## Plan

1. **Chờ `PMI-011` đạt `status: done`** (verdict pass) trước khi bắt đầu — task này không có việc để làm nếu backend chưa fix xong scope-matching.
2. Chạy unit test hiện có: `ProductCard.test.tsx`, `useComputedPrice.test.ts` — xác nhận vẫn xanh (không đổi code ở bước này, chỉ chạy lại sau khi PMI-011 deploy để phát hiện regression nếu fix backend đổi shape response).
3. Chạy E2E `test_promotion_full_flow.py` với 1 promotion scope "tất cả sản phẩm" — nếu chưa có case này trong E2E, thêm 1 case mới (test-only change, không đổi component logic).
4. Manual QA theo 4 điểm ở `## Verification`: trang chủ, trang danh mục, trang chi tiết, giỏ hàng.
5. Nếu phát hiện lỗi frontend RIÊNG (không phải do backend chưa fix) — ví dụ `ProductCard`/`cartSlice.ts` không đọc đúng field `computedPrice`/`hasActivePromotion` từ response mới — ghi cụ thể vào `## Findings` và báo lại, KHÔNG tự mở rộng fix ngoài các file đã khai trong `files:`.

## Sub-tasks
- [ ] Chờ `PMI-011` merge/deploy trước khi bắt đầu verify (depends_on).
- [ ] Chạy manual QA theo Verification ở 4 vị trí hiển thị giá.
- [ ] Nếu phát hiện lỗi frontend riêng biệt, ghi cụ thể + không tự fix ngoài scope task này.
