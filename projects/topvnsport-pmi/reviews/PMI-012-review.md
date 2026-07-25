---
id: PMI-012
task_path: projects/topvnsport-pmi/tasks/PMI-012-public-products-promotion-price.md
project: topvnsport-pmi
result_ref: "3f29743"
executor: "@gpt-5.6-luna-high"
reviewer: "@claude-opus"
status: done
issued: 2026-07-25
verdict: pass
verdict_date: 2026-07-25
---

# Phiếu Review: PMI-012 — Endpoint `/public/products` chưa trả giá đã áp dụng khuyến mãi

- Dự án: TopVNSport - PMI (`/home/lupca/projects/topvnsport`)
- Task gốc: `projects/topvnsport-pmi/tasks/PMI-012-public-products-promotion-price.md`
- Result-ref: `3f29743`
- Executor: @gpt-5.6-luna-high
- Ngày phát phiếu: 2026-07-25

## Bối cảnh — đây là ROOT CAUSE THẬT của báo cáo gốc User
`PMI-011` (fix backend promotion-matching) và `WEB-005` (fix frontend display) đều đã pass/done, nhưng verify trực tiếp qua browser cho thấy trang storefront VẪN không hiện giảm giá — vì `/public/products` (endpoint thật storefront gọi) chưa từng tích hợp với hệ thống promotion. PMI-012 sửa đúng chỗ này.

**Control-tower đã tự verify độc lập bằng browser THẬT (claude-in-chrome) sau khi commit `3f29743`, tại đúng URL user báo cáo ban đầu**: `http://localhost:13103/product/vot-lining-e2e-otp-test-925dcbf1` → xác nhận trang hiện `1.000.000đ`, gạch ngang `1.250.000đ`, badge `TIẾT KIỆM 20%`. Đây là bằng chứng thật (không phải lời khai executor) — nhưng reviewer vẫn phải tự verify lại AC + đọc diff, không dựa hoàn toàn vào ghi chú này.

## Acceptance Criteria cần verify

- [x] **AC1**: `GET /public/products` trả về mỗi variant kèm `computed_price`, `has_active_promotion`, `original_price` khi có promotion active — dùng lại `get_bulk_computed_prices` (không viết lại discount logic).
- [x] **AC2**: `GET /public/products/{slug}` trả cùng field cho toàn bộ variant của 1 sản phẩm.
- [x] **AC3**: Verify qua browser thật — control-tower đã làm 1 lần (xem trên), reviewer verify lại độc lập.
- [x] **AC4**: Không phá vỡ filter `min_price`/`max_price` (dùng `compute_product_prices`, không được động vào) — 100% test trong `tests:` xanh.
- [x] **AC5**: Không N+1 — `get_bulk_computed_prices` phải được gọi ĐÚNG 1 LẦN mỗi request (list và detail), không loop theo từng variant.

## Điểm cần soi kỹ (từ code-review-graph, đã rebuild ở commit `3f29743`)
- Graph báo cáo xuất hiện 2 hàm MỚI không có trong plan gốc: `get_public_variant_prices`, `get_public_promotion_fields` (có thể là helper do executor tự refactor thêm) — graph flag cả 2 là **untested hotspot**, cùng với `get_bulk_prices`, `PublicVariantResponse`, `get_public_products`. Đọc diff kỹ xem 2 hàm mới này có đúng như AC5 mô tả (gọi batch 1 lần) hay có che giấu 1 vòng lặp gọi lẻ tẻ.
- Diffstat: `PMI/backend/routers/public.py` (+30/-2), `PMI/backend/tests/test_public.py` (+81) — khá gọn, đúng tinh thần "chỉ enrich response, không viết lại logic".

## Definition of Done (AGENTS.md mục 3)
- [x] Toàn bộ AC pass
- [x] Test liên quan xanh 100%: `PMI/backend/tests/test_public.py` (4/4 passed)
- [x] Không regression — full suite 226/226 pass (reviewer verified)
- [x] Reviewer khác executor (xác nhận `@claude-opus` ≠ `@gpt-5.6-luna-high`)

## Test gợi ý chạy trong repo code

```bash
cd /home/lupca/projects/topvnsport
docker compose -f PMI/docker-compose.yml exec -e BYPASS_TESTCONTAINERS=true api pytest tests/test_public.py -v
docker compose -f PMI/docker-compose.yml exec -e BYPASS_TESTCONTAINERS=true api pytest -v
```

## Manual QA Steps

1. Mở `http://localhost:13103/product/vot-lining-e2e-otp-test-925dcbf1` → xác nhận giá gạch ngang + badge (đã verify 1 lần, verify lại).
2. Mở trang danh mục/trang chủ (`ProductCard`) → kiểm tra sản phẩm có promotion có hiện badge giảm giá trong list view không (executor test chủ yếu qua API + 1 trang chi tiết, chưa chắc đã check list view qua browser).
3. Đọc diff `git diff 2f7d238..3f29743 -- PMI/backend/routers/public.py` → xác nhận `get_bulk_computed_prices` chỉ gọi 1 lần/request (không trong loop).
4. Verify filter `min_price`/`max_price` vẫn hoạt động đúng (AC4) — không bị ảnh hưởng bởi field mới thêm vào response.

## Review Toolchain
```
cat .claude/review-toolchain.md
```
Preflight theo `knowledge/tools/tool-registry.md`. `/code-review` baseline chạy cùng các tool khác.

## Trả kết quả

```
/verdict PMI-012 <pass|changes> --reviewer @<tên bạn> --commit 3f29743 [--notes "..."]
```
