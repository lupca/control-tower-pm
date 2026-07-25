---
id: WEB-006
title: "Verify end-to-end: giảm giá scope 'tất cả sản phẩm' hiển thị đúng trên storefront"
status: done
priority: high
risk: normal
created: 2026-07-24
executor: "@antigravity-3.6-high"
reviewer: "@antigravity"
result_ref: "4b73e54"
depends_on: [PMI-012]
files:
  - web/src/components/ProductCard.tsx
  - web/src/components/ProductDetailPage.tsx
  - web/src/hooks/useComputedPrice.ts
flows: [catalog-add-to-cart, home-add-to-cart]
tests:
  - web/src/__tests__/ProductCard.test.tsx
  - web/src/__tests__/useComputedPrice.test.ts
  - e2e_tests/tests/test_promotion_full_flow.py
dispatched: 2026-07-25
in_review: 2026-07-25
predicted_success: high
prediction_factors:
  score: 0.7
  deductions:
    - "hits hub/bridge node not applicable (verification task, no core logic change expected)"
created: 2026-07-24
updated: 2026-07-25
rejections: 1
---

# WEB-006: Verify end-to-end giảm giá scope "tất cả sản phẩm" trên storefront

> Dự án: [[projects/topvnsport-web/topvnsport-web]]

## Bối cảnh
Phụ thuộc `PMI-011` (fix root cause backend: promotion scope "tất cả sản phẩm" không match/tính discount đúng — done). `WEB-005` đã fix hiển thị giá trên `ProductDetailPage` (bug hiển thị khác, đã qua review).

**Cập nhật 2026-07-25**: Verify trực tiếp bằng browser sau khi PMI-011 done cho thấy PMI-011 + WEB-005 CHƯA ĐỦ — trang storefront vẫn không hiện giảm giá vì `GET /public/products` (endpoint thật storefront dùng để lấy giá) chưa từng tích hợp với hệ thống promotion. Root cause thật đã tách thành `PMI-012` (`depends_on` đã đổi từ `PMI-011` sang `PMI-012`). Task này verify SAU KHI PMI-012 merge, storefront thực sự hiển thị/áp dụng đúng giảm giá ở TẤT CẢ các nơi hiển thị giá — không chỉ trang chi tiết sản phẩm.

## Tiêu chí nghiệm thu (AC)
- [x] **AC1**: Trang danh sách sản phẩm (`CatalogPage`/`HomePage` dùng `ProductCard`) hiển thị giá gạch ngang + badge giảm giá cho MỌI sản phẩm khi có promotion scope "tất cả sản phẩm" active. *(Control-tower đã verify trực tiếp qua browser thật 2026-07-25 — trang chủ mục "Giờ Vàng Săn Deal" hiện đúng `-20%`, giá gạch ngang cho cả 4 sản phẩm test. Executor verify lại + thêm regression test.)*
- [x] **AC2**: Trang chi tiết sản phẩm (`ProductDetailPage`, đã fix ở WEB-005) tiếp tục hiển thị đúng sau khi backend fix — không regression. *(Control-tower đã verify qua browser thật tại `/product/vot-lining-e2e-otp-test-925dcbf1` — hiện đúng `1.000.000đ`/`1.250.000đ`/`TIẾT KIỆM 20%`.)*
- [x] **AC3**: Thêm vào giỏ hàng (`buildDefaultCartItem` trong `cartSlice.ts`) dùng đúng giá đã giảm, không phải giá gốc. *(CHƯA verify — việc chính còn lại của executor.)*
- [x] **AC4**: Test `test_promotion_full_flow.py` (E2E) pass với case scope "tất cả sản phẩm".
- [x] **AC5**: Nếu bất kỳ AC nào fail → không phải lỗi backend (đã cover ở PMI-011/PMI-012), phải mô tả cụ thể lỗi phía frontend còn sót lại.

## Verification
- `cd /home/lupca/projects/topvnsport/web && pnpm test -- --grep "ProductCard|computedPrice"` → 100% pass
- `cd /home/lupca/projects/topvnsport && pytest e2e_tests/tests/test_promotion_full_flow.py -v` → 100% pass
- Manual: sau khi PMI-011 active 1 promotion scope="tất cả sản phẩm" 20% → mở trang chủ, trang danh mục, trang chi tiết, thêm giỏ hàng → verify giá giảm nhất quán ở cả 4 nơi.

## Plan

**Cập nhật 2026-07-25 — scope thu hẹp**: `PMI-012` (root cause thật) đã done. Control-tower đã tự verify AC1+AC2 qua browser thật (trang chủ + trang chi tiết đều hiện đúng giảm giá). Việc còn lại của executor:

1. Verify lại AC1+AC2 độc lập (đừng chỉ tin ghi chú trên) — mở lại 2 trang, xác nhận vẫn đúng.
2. **AC3 (chưa ai verify)**: thêm sản phẩm có promotion active vào giỏ hàng → kiểm tra `buildDefaultCartItem`/`cartSlice.ts` có dùng đúng giá đã giảm hay vẫn dùng giá gốc `price`. Đây là chỗ có khả năng cao còn sót lỗi (cùng dạng bug với PMI-012: 1 chỗ khác trong hệ thống chưa đọc field `computed_price` mới).
3. Chạy unit test hiện có: `ProductCard.test.tsx`, `useComputedPrice.test.ts`.
4. Thêm 1 case mới vào `test_promotion_full_flow.py` (E2E) cho scope "tất cả sản phẩm" nếu chưa có — test-only change.
5. Nếu phát hiện lỗi frontend RIÊNG (vd cart không đọc đúng field mới) — ghi cụ thể vào `## Findings` và báo lại, KHÔNG tự mở rộng fix ngoài các file đã khai trong `files:` (nếu cần sửa `cartSlice.ts`, thêm file đó vào `files:` trước khi sửa — báo lại control-tower nếu cần mở rộng scope).

## Sub-tasks
- [ ] Chờ `PMI-011` merge/deploy trước khi bắt đầu verify (depends_on).
- [ ] Chạy manual QA theo Verification ở 4 vị trí hiển thị giá.
- [ ] Nếu phát hiện lỗi frontend riêng biệt, ghi cụ thể + không tự fix ngoài scope task này.

## Findings từ reviewer
- [ ] AC4 test-coverage gap: new e2e test test_tier1_f6_06_storefront_all_products_scope_e2e's docstring claims to cover ProductCard/quick-add-to-cart (buildDefaultCartItem) but the code actually exercises Header search dropdown + product-detail add-to-cart (buildConfiguredCartItem) instead - the claimed regression-coverage paths are not actually exercised
- [ ] minor: wait_until polling helper returns on first truthy dict instead of checking has_active_promotion/computed_price condition (low severity, not currently flaky). IMPORTANT: reviewer independently verified via hands-on browser testing that AC1/AC2/AC3 all work correctly in production (catalog ProductCard shows -20%/1.000.000đ/1.250.000đ struck-through, quick-add-to-cart drawer shows discounted price, product detail page correct) - no production bug, this is purely a test-coverage/test-quality gap in the new E2E test.
