---
id: PMI-011
task_path: projects/topvnsport-pmi/tasks/PMI-011-fix-all-products-scope-discount.md
project: topvnsport-pmi
result_ref: "2f7d238"
executor: "@antigravity-3.6-high"
reviewer: "@antigravity"
status: pass
issued: 2026-07-25
verdict: pass
verdict_date: 2026-07-25
---

# Phiếu Review: PMI-011 — Fix khuyến mãi scope "tất cả sản phẩm" (giảm 20%) không được áp dụng (VÒNG 3 — SCOPE ĐÃ THU HẸP)

- Dự án: TopVNSport - PMI (`/home/lupca/projects/topvnsport`)
- Task gốc: `projects/topvnsport-pmi/tasks/PMI-011-fix-all-products-scope-discount.md`
- Result-ref: `2f7d238` (vòng 3, sau vòng 1 `6b54a76` và vòng 2 `a7e9472`)
- Executor: @antigravity-3.6-high (giữ nguyên executor vòng 2, User chấp nhận rủi ro cho cơ hội tự sửa)
- Reviewer: @antigravity (đổi khỏi @gpt-5.6-sol theo rotation rule — task đã reject 2 lần)
- Ngày phát phiếu: 2026-07-25

## ⚠️ QUAN TRỌNG — Phạm vi đã thu hẹp theo quyết định User (2026-07-25)

**KHÔNG chấm điểm/yêu cầu fix phần NLP `parse_promotion_intent`.** User đã quyết định descope finding HIGH của vòng 2 (regression: prompt có cả product ID + từ "biến thể" → parse sai thành `VARIANT:101` bịa thay vì `PRODUCT:20`). Lý do User: "Cái mục tự động tạo phiếu giảm giá thì kệ nó đi. Cái đó chủ yếu là người nhập mà quan tâm làm gì." → Đây KHÔNG phải regression cần fix, review KHÔNG được reject vì lý do này.

**Việc bắt buộc duy nhất còn lại của vòng 3**: `GET /promotions/bulk-prices` (và các alias) trước đây trả `405 Method Not Allowed` (chỉ có POST) → Executor báo đã thêm GET method cho cả 3 route (`/promotions/bulk-prices`, `/api/promotions/bulk-prices`, `/api/computed-prices/bulk`) + reorder static routes lên trước route `/api/promotions/{id}` (tránh FastAPI match nhầm thành path param) + cho phép `variant_ids` truyền qua query param khi dùng GET.

## Acceptance Criteria cần verify (đã cập nhật cho vòng 3)

- [x] **AC1**: Tạo promotion scope "tất cả sản phẩm" qua API thật với `ALL_PRODUCTS` → `201`, match 100% variant. *(đã PASS vòng 2, verify không regression)*
- [x] **AC2**: `calculate_discount` tính đúng 20%. *(đã PASS vòng 1+2, verify không regression)*
- [x] **AC3**: `GET /promotions/bulk-prices` (và 2 alias khác) trả `200` (không còn `405`/`404`), response đúng `computedPrice` đã giảm cho >=5 variant.
- [x] **AC4**: Không regression scope khác (category/product/variant specific) — **KHÔNG bao gồm** NLP intent-parser edge case đã descope. 100% test trong `tests:` xanh.
- [x] **AC5**: Fix vòng 3 tối giản, không động vào `parse_promotion_intent` hay logic scope-matching đã fix ở vòng 1/2 (verify bằng diff `a7e9472..2f7d238` chỉ đổi routing, không đổi `promotion_service.py`).

## Definition of Done (AGENTS.md mục 3)
- [x] Toàn bộ AC pass (theo phạm vi đã thu hẹp — KHÔNG tính NLP parser)
- [x] Test liên quan xanh 100%: `test_promotions_compute.py`, `test_promotions_scope_stress.py`, `test_tier5_adversarial_backend.py`
- [x] Không regression — executor báo 104/104 unit pass, reviewer tự chạy lại xác nhận
- [x] Reviewer khác executor (xác nhận `@antigravity` ≠ `@antigravity-3.6-high`)

## Test gợi ý chạy trong repo code

```bash
cd /home/lupca/projects/topvnsport
docker compose -f PMI/docker-compose.yml exec -e BYPASS_TESTCONTAINERS=true api pytest tests/unit/test_promotions_compute.py tests/unit/test_promotions_scope_stress.py tests/unit/test_tier5_adversarial_backend.py -v
docker compose -f PMI/docker-compose.yml exec -e BYPASS_TESTCONTAINERS=true api pytest tests/unit/ -v
```

## Manual QA Steps

1. `GET /promotions/bulk-prices?variant_ids=<id1>,<id2>` (và `/api/promotions/bulk-prices`, `/api/computed-prices/bulk`) → phải `200`, không `404`/`405`.
2. Xác nhận route reorder không làm `GET /api/promotions/{id}` (lấy 1 promotion theo ID thật) bị match nhầm hay lỗi — test cả 2 loại request cùng lúc.
3. Diff `git diff a7e9472..2f7d238` → xác nhận CHỈ đổi `routers/promotions.py` + test file, KHÔNG đổi `services/promotion_service.py` (đúng cam kết không động NLP parser/scope logic).
4. Chạy lại đúng 3 case reproduction NLP của vòng 2 (`"Giảm 10% cho biến thể của sản phẩm 20"` v.v.) chỉ để XÁC NHẬN HIỆN TRẠNG (không phải gate) — nếu vẫn sai thì đó là hành vi đã biết, đã descope, KHÔNG chặn merge.

## Review Toolchain
```
cat .claude/review-toolchain.md
```
Preflight theo `knowledge/tools/tool-registry.md`. `/code-review` baseline chạy cùng các tool khác.

## Trả kết quả

```
/verdict PMI-011 <pass|changes> --reviewer @<tên bạn> --commit 2f7d238 [--notes "..."]
```
