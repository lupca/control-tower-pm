# Phiếu Review: WEB-001 — Implement Promotion Module cho Marketing Team

- Dự án: topvnsport-web (`/home/lupca/projects/topvnsport`)
- Task gốc: `projects/topvnsport-web/tasks/WEB-001-promotion-module.md`
- Result-ref: `topvnsport@main (commit 80875eca6dd8351a25661fe03d8ad3895bb13dbe)`
- Executor: @antigravity-3.6
- Ngày phát phiếu: 2026-07-22

## Acceptance Criteria cần verify

### Backend (PMI)
- [ ] Database migrations tạo 4 bảng mới: `promotions`, `promotion_scope`, `promotion_computed_prices`, `promotion_usage_log`
- [ ] Pydantic schemas cho Promotion CRUD (PromotionCreate, PromotionUpdate, PromotionResponse, ComputedPriceResponse)
- [ ] API CRUD `/api/promotions` (POST, GET, PATCH, DELETE)
- [ ] API Lifecycle `/api/promotions/{id}/activate`, `/pause`, `/resume`, `/end`
- [ ] API Preview `/api/promotions/{id}/preview` trả về danh sách variants bị ảnh hưởng
- [ ] API Computed Price `/api/variants/{id}/computed-price` và `/api/computed-prices/bulk`
- [ ] Compute engine tính giá đúng cho 3 loại: percentage, fixed_amount, fixed_price
- [ ] Compute engine áp dụng max_discount constraint khi có
- [ ] Auto-scheduler (cron): scheduled→active khi start_at <= now, active→ended khi end_at < now
- [ ] Priority: khi nhiều promo cùng target, chọn promo có priority cao nhất

### Frontend PMI (cho Marketing Team)
- [ ] Menu "Promotions" trong sidebar
- [ ] Promotion List page với filter theo status, search theo code/name
- [ ] Promotion Create form (wizard hoặc single page) với 4 bước: info, discount type, scope, schedule
- [ ] Promotion Preview modal hiển thị số variants bị ảnh hưởng trước khi activate
- [ ] Promotion Detail page với stats (affected variants, total discount)
- [ ] Lifecycle buttons: Activate, Pause, Resume, End

### Frontend Web (topvnsport.vn)
- [ ] Hook `useComputedPrice(variantId)` gọi API lấy giá sau giảm
- [ ] `productMappers.ts` sử dụng computed price từ API thay vì placeholder
- [ ] `ProductCard.tsx` hiển thị giá gốc (gạch ngang) + giá khuyến mãi + badge % giảm
- [ ] Chỉ hiển thị sale price khi có promotion active

### Testing (KHÔNG manual test)
- [ ] Backend unit tests: coverage >= 85% cho module promotions
- [ ] Frontend unit tests PMI: coverage >= 80% cho PromotionList, PromotionForm
- [ ] Frontend unit tests Web: coverage >= 85% cho useComputedPrice, productMappers
- [ ] E2E test: tạo promo → activate → verify giá hiển thị đúng trên web
- [ ] E2E test: promo expired → verify giá trở về bình thường
- [ ] CI block merge nếu tests fail

### AI-Agent Ready (tương lai)
- [ ] Promotion schema có fields: `intent` (text), `ai_reasoning` (JSONB), `created_by` (string)
- [ ] API `/api/promotions/parse-intent` nhận natural language, trả về structured promotion draft

## Definition of Done (AGENTS.md mục 3)

- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%:
  - `PMI/backend/tests/test_promotions_crud.py`
  - `PMI/backend/tests/test_promotions_lifecycle.py`
  - `PMI/backend/tests/test_promotions_compute.py`
  - `PMI/backend/tests/test_promotions_scope.py`
  - `PMI/backend/tests/test_promotions_scheduler.py`
  - `PMI/frontend/src/__tests__/promotions/PromotionList.test.tsx`
  - `PMI/frontend/src/__tests__/promotions/PromotionForm.test.tsx`
  - `web/src/__tests__/hooks/useComputedPrice.test.ts`
  - `web/src/__tests__/components/ProductCard.test.tsx`
  - `e2e_tests/tests/test_promotion_full_flow.py`
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (bạn đang review, hãy xác nhận bạn ≠ @antigravity-3.6)

## Test gợi ý chạy trong repo code

```bash
# Backend unit tests (PMI)
docker compose -f PMI/docker-compose.yml exec api pytest PMI/backend/tests/test_promotions*.py -v

# Backend coverage check
docker compose -f PMI/docker-compose.yml exec api pytest PMI/backend/tests/test_promotions*.py --cov=PMI/backend --cov-fail-under=85

# Frontend unit tests (PMI)
cd PMI/frontend && npm run test -- --run src/__tests__/promotions/

# Frontend unit tests (Web)
cd web && npm run test -- --run src/__tests__/hooks/useComputedPrice.test.ts src/__tests__/components/ProductCard.test.tsx

# E2E tests
docker compose up -d
cd e2e_tests && pytest tests/test_promotion_full_flow.py -v
```

## Câu hỏi rủi ro (từ code-review-graph, tĩnh — không thay thế việc bạn tự đọc diff)

### High Priority
1. **Hub node 'upgrade' (migration)**: Migration file có 204 connections nhưng không có test trực tiếp. Kiểm tra migration mới cho promotions có đúng format và rollback được không.

### Medium Priority
2. **Untested hotspot**: `OrdersPageContent` có 195 connections nhưng không test. Nếu promotion module tích hợp với OMS, cần verify không break flow này.

### Lưu ý cho task này
- Task này thêm module MỚI (không sửa code cũ nhiều), nên risk thấp hơn so với refactor.
- Cần đặc biệt chú ý: migration có thể rollback không, và E2E test cover full flow.

## Gợi ý công cụ

Repo code đích có thể có sẵn skill `/code-review` (hoặc tương đương) — khuyến khích dùng để đọc diff + chạy test một cách có cấu trúc.

## Trả kết quả

Sau khi review xong, báo lại cho control-tower bằng lệnh:

```
/verdict WEB-001 <pass|changes> --reviewer @<tên bạn> --commit 80875eca6dd8 [--notes "..."]
```
