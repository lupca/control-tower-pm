---
id: WEB-005
task_path: projects/topvnsport-web/tasks/WEB-005-fix-discount-price-display.md
project: topvnsport-web
result_ref: "055fe30"
executor: "@dev"
reviewer: null
status: pending
issued: 2026-07-24
verdict: null
verdict_date: null
---

# Phiếu Review: WEB-005 — Fix discount price display on product detail page

- Dự án: TopVNSport - Web (`/home/lupca/projects/topvnsport`)
- Task gốc: `projects/topvnsport-web/tasks/WEB-005-fix-discount-price-display.md`
- Result-ref: `055fe30`
- Executor: @dev
- Ngày phát phiếu: 2026-07-24

## Acceptance Criteria cần verify

- [ ] **AC1**: Sản phẩm có mã giảm giá active → hiển thị giá gốc gạch ngang + badge "TIẾT KIỆM X%".
- [ ] **AC2**: Sản phẩm KHÔNG có promotion → không hiển thị badge, chỉ hiển thị giá bán.
- [ ] **AC3**: Variant-level promotion: chọn variant khác nhau → giá + badge cập nhật tương ứng.
- [ ] **AC4**: Kết hợp stringing price: `displayOriginalPrice + stringPrice` phải gạch ngang đúng.
- [ ] **AC5**: Consistency: logic tương đương `ProductCard.tsx` (đang hoạt động đúng).

## Definition of Done (AGENTS.md mục 3)

- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%:
  - `web/src/__tests__/ProductCard.test.tsx`
  - `web/src/__tests__/useComputedPrice.test.ts`
  - `web/src/__tests__/productMappers.test.ts`
  - `e2e_tests/tests/test_promotion_full_flow.py`
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (bạn đang review, hãy xác nhận bạn ≠ @dev)

## Test gợi ý chạy trong repo code

```bash
# Unit tests (web)
cd /home/lupca/projects/topvnsport/web
npm test -- --run

# E2E (optional)
cd /home/lupca/projects/topvnsport
pytest e2e_tests/tests/test_promotion_full_flow.py -v
```

## Manual QA Steps

1. Tạo promotion cho sản phẩm X trong PMI → lưu.
2. Mở `/products/{slug}` trên web → verify badge "TIẾT KIỆM X%" + giá gốc gạch ngang.
3. Chọn variant khác (nếu có) → verify giá + badge cập nhật.
4. Xóa promotion → refresh → verify badge biến mất.

## Câu hỏi rủi ro (từ code-review-graph, tĩnh)

### Affected Flows (criticality ~0.69)
- **App flow** (48 nodes, 28 files): `ProductDetailRoute` → `ProductDetailPage` → `ProductPurchaseSection`
- Flow đi qua checkout (`CartModal`, `OtpModal`) — verify không break checkout flow.

### Risk Questions
| Priority | Question |
|:---|:---|
| high | `test_full_flow` là bridge node quan trọng — chạy E2E để đảm bảo không regression |
| high | `test_storefront_otp_checkout_flow` — verify OTP checkout vẫn hoạt động |
| medium | `ProductPurchaseSection` có 2 props mới (`hasDiscount`, `discountPercent`) — verify backward compat với parent |

## Gợi ý công cụ

Repo code đích có sẵn skill `/code-review` — khuyến khích dùng để đọc diff + chạy test một cách có cấu trúc.

## Trả kết quả

Sau khi review xong, báo lại cho control-tower bằng lệnh:

```
/verdict WEB-005 <pass|changes> --reviewer @<tên bạn> --commit 055fe30 [--notes "..."]
```
