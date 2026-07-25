---
id: WEB-006
task_path: projects/topvnsport-web/tasks/WEB-006-verify-all-products-discount-e2e.md
project: topvnsport-web
result_ref: "4b73e54"
executor: "@antigravity-3.6-high"
reviewer: "@antigravity"
status: passed
issued: 2026-07-25
verdict: pass
verdict_date: 2026-07-25
---

# Phiếu Review: WEB-006 — Verify end-to-end giảm giá "tất cả sản phẩm" trên storefront (VÒNG 2 — chỉ sửa test)

- Dự án: TopVNSport - Web (`/home/lupca/projects/topvnsport`)
- Task gốc: `projects/topvnsport-web/tasks/WEB-006-verify-all-products-discount-e2e.md`
- Result-ref: `4b73e54` (vòng 2, sau vòng 1 `d275f34`)
- Executor: @antigravity-3.6-high (khác executor vòng 1 `@claude-sonnet-medium`)
- Ngày phát phiếu: 2026-07-25

## Bối cảnh vòng 2
Vòng 1 (`@gpt-5.6-sol`): **CHANGES** — nhưng KHÔNG phải bug sản phẩm. Reviewer tự tay verify qua browser thật xác nhận AC1/AC2/AC3 đều hoạt động đúng trong production. Lý do reject DUY NHẤT: e2e test mới `test_tier1_f6_06_storefront_all_products_scope_e2e` có docstring tuyên bố test `ProductCard`/quick-add-to-cart (`buildDefaultCartItem`) nhưng code thực tế lại test Header search dropdown + product-detail add-to-cart (`buildConfiguredCartItem`) — 2 finding HIGH (test không cover đúng path đã khai) + 1 finding LOW (`wait_until` polling không check đúng điều kiện).

**Executor báo cáo đã sửa**: test giờ điều hướng `/catalog`, locate đúng `#product-card-{id}`, assert badge/giá trên chính `ProductCard`, click nút quick-add-to-cart trên card, verify cart drawer có giá giảm. Giữ riêng bước product-detail cho AC2. Sửa `wait_until` để check đúng `has_active_promotion is True` + `computed_price == 1000000.0`. Full suite: **83/83 pass** (kể cả `test_tier2_f4_b05_preview_promotion_empty_scope` mà vòng 1 ghi nhận là pre-existing fail — giờ pass, có thể do dev-DB state thay đổi giữa các lần chạy, không cần điều tra thêm nếu không regression).

## Acceptance Criteria cần verify (vòng 2 — chỉ tập trung AC4)

- [ ] **AC1/AC2/AC3**: đã PASS ở vòng 1 (verify bằng browser thật bởi reviewer), không cần re-verify sâu — chỉ xác nhận không có thay đổi code sản phẩm nào ở commit này (diffstat: chỉ `e2e_tests/tests/test_promotion_full_flow.py`).
- [ ] **AC4 (trọng tâm vòng 2)**: Đọc lại test đã sửa — xác nhận:
  1. Test thật sự điều hướng `/catalog` (hoặc home) và tương tác với `ProductCard` (không phải Header search).
  2. Assert badge/sale-price/original-price được đọc từ chính `ProductCard`, không phải từ nơi khác.
  3. Click đúng nút quick-add-to-cart TRÊN CARD (gọi `buildDefaultCartItem`), không phải nút trên product-detail.
  4. Cart drawer sau đó show đúng giá giảm.
  5. Bước product-detail (AC2) vẫn còn giữ riêng, không bị xoá.
  6. `wait_until` giờ check đúng `has_active_promotion is True and computed_price == 1000000.0`, không chỉ return dict đầu tiên.
- [ ] **AC5**: Diff CHỈ đổi file test, không đụng `web/src/**` hay `PMI/backend/**`.

## Definition of Done
- [ ] AC4 pass thật sự (đọc code, không chỉ tin báo cáo — đây là task đã reject 1 lần đúng vì tin báo cáo docstring mà không đọc kỹ code)
- [ ] Full suite `test_promotion_full_flow.py` xanh (executor báo 83/83)
- [ ] Reviewer khác executor (`@antigravity` ≠ `@antigravity-3.6-high`)

## Test gợi ý chạy trong repo code

```bash
cd /home/lupca/projects/topvnsport
pytest e2e_tests/tests/test_promotion_full_flow.py -v
```

## Review Toolchain
```
cat .claude/review-toolchain.md
```

## Trả kết quả

```
/verdict WEB-006 <pass|changes> --reviewer @<tên bạn> --commit 4b73e54 [--notes "..."]
```
