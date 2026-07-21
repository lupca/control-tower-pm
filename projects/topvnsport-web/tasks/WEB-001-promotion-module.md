---
id: WEB-001
title: "Implement Promotion Module cho Marketing Team"
status: changes-requested
priority: high
risk: normal
deadline: null
executor: "@antigravity-3.6"
reviewer: null
result_ref: "topvnsport@main (commit 80875eca6dd8)"
depends_on: []
files:
  - PMI/backend/models.py (them bang promotions, promotion_scope, promotion_computed_prices, promotion_usage_log)
  - PMI/backend/schemas/promotion.py (moi)
  - PMI/backend/routers/promotions.py (moi)
  - PMI/backend/services/promotion_service.py (moi)
  - PMI/frontend/src/app/promotions/ (moi - list, create, edit pages)
  - web/src/services/sport-api/productMappers.ts
  - web/src/hooks/useComputedPrice.ts (moi)
  - web/src/components/ProductCard.tsx
flows:
  - getStringOptions
  - getProducts
  - update_product
  - create_product
tests:
  - PMI/backend/tests/test_promotions_crud.py (moi)
  - PMI/backend/tests/test_promotions_lifecycle.py (moi)
  - PMI/backend/tests/test_promotions_compute.py (moi)
  - PMI/backend/tests/test_promotions_scope.py (moi)
  - PMI/backend/tests/test_promotions_scheduler.py (moi)
  - PMI/frontend/src/__tests__/promotions/PromotionList.test.tsx (moi)
  - PMI/frontend/src/__tests__/promotions/PromotionForm.test.tsx (moi)
  - web/src/__tests__/hooks/useComputedPrice.test.ts (moi)
  - web/src/__tests__/components/ProductCard.test.tsx (cap nhat)
  - e2e_tests/tests/test_promotion_full_flow.py (moi)
dispatched: 2026-07-22
in_review: 2026-07-22
created: 2026-07-22
updated: 2026-07-22
changes_requested: 2026-07-22
---

# WEB-001: Implement Promotion Module cho Marketing Team

> Dự án: [[projects/topvnsport-web/topvnsport-web]]

## Tiêu chí nghiệm thu (AC)

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

## Plan

### Phase 1: Backend Database & Models

1. **Migration file** `PMI/backend/alembic/versions/xxxx_add_promotion_tables.py`:
   - Tạo bảng `promotions` (id, code, name, description, intent, ai_reasoning, discount_type, discount_value, conditions, start_at, end_at, status, priority, is_stackable, created_by, updated_by, created_at, updated_at)
   - Tạo bảng `promotion_scope` (id, promotion_id, scope_type, scope_value, exclude_type, exclude_value)
   - Tạo bảng `promotion_computed_prices` (id, promotion_id, variant_id, original_price, discount_amount, final_price, computed_at)
   - Tạo bảng `promotion_usage_log` (id, promotion_id, order_id, variant_id, quantity, discount_applied, used_at)
   - Indexes cho query thường dùng

2. **Models** thêm vào `PMI/backend/models.py`:
   - Class `Promotion`, `PromotionScope`, `PromotionComputedPrice`, `PromotionUsageLog`

3. **Schemas** tạo `PMI/backend/schemas/promotion.py`:
   - `PromotionCreate`, `PromotionUpdate`, `PromotionResponse`
   - `PromotionScopeCreate`, `PromotionScopeResponse`
   - `ComputedPriceResponse`, `BulkComputedPriceResponse`

### Phase 2: Backend Business Logic

4. **Service** tạo `PMI/backend/services/promotion_service.py`:
   - `compute_final_price(variant, active_promotions)` — logic tính giá
   - `variant_in_scope(variant, promotion)` — check scope rules
   - `get_active_promotions_for_variant(variant_id)` — query active promos
   - `compute_and_cache_prices(promotion_id)` — populate `promotion_computed_prices`

5. **Scheduler** tạo `PMI/backend/services/promotion_scheduler.py`:
   - `update_promotion_statuses()` — cron job: scheduled→active, active→ended
   - Integrate vào `lifespan` hoặc separate worker

### Phase 3: Backend APIs

6. **Router** tạo `PMI/backend/routers/promotions.py`:
   - `POST /api/promotions` — create
   - `GET /api/promotions` — list (filter: status, date range)
   - `GET /api/promotions/{id}` — detail
   - `PATCH /api/promotions/{id}` — update
   - `DELETE /api/promotions/{id}` — soft delete
   - `POST /api/promotions/{id}/activate` — draft→active/scheduled
   - `POST /api/promotions/{id}/pause` — active→paused
   - `POST /api/promotions/{id}/resume` — paused→active
   - `POST /api/promotions/{id}/end` — →ended
   - `POST /api/promotions/{id}/preview` — preview affected variants
   - `POST /api/promotions/{id}/compute` — trigger compute & cache

7. **Computed Price API** thêm vào router:
   - `GET /api/variants/{id}/computed-price`
   - `GET /api/computed-prices/bulk?variant_ids=1,2,3`

8. **Register router** trong `PMI/backend/main.py`

### Phase 4: Backend Tests

9. **Unit tests** tạo trong `PMI/backend/tests/`:
   - `test_promotions_crud.py` — CRUD operations
   - `test_promotions_lifecycle.py` — state transitions
   - `test_promotions_compute.py` — price calculation logic
   - `test_promotions_scope.py` — scope filtering
   - `test_promotions_scheduler.py` — auto status updates

### Phase 5: Frontend PMI

10. **Menu** cập nhật `PMI/frontend/src/components/layout/Sidebar.tsx`:
    - Thêm link "Khuyến mãi" icon Tag/Percent

11. **List page** tạo `PMI/frontend/src/app/promotions/page.tsx`:
    - Table với columns: code, name, type, value, status, dates, actions
    - Filter by status, search by code/name
    - Status badges (active=green, scheduled=yellow, ended=gray)

12. **Create/Edit form** tạo `PMI/frontend/src/app/promotions/new/page.tsx` và `[id]/edit/page.tsx`:
    - Step 1: Basic info (code, name, description)
    - Step 2: Discount type & value
    - Step 3: Scope (all/brand/category/product) + exclusions
    - Step 4: Schedule (start_at, end_at)
    - Preview button → show affected variants count

13. **Detail page** tạo `PMI/frontend/src/app/promotions/[id]/page.tsx`:
    - Stats: affected variants, total potential discount
    - Lifecycle buttons
    - Usage log table

14. **Frontend tests** tạo trong `PMI/frontend/src/__tests__/promotions/`:
    - `PromotionList.test.tsx`
    - `PromotionForm.test.tsx`

### Phase 6: Frontend Web

15. **Hook** tạo `web/src/hooks/useComputedPrice.ts`:
    - Fetch `/api/variants/{id}/computed-price`
    - Return `{ hasPromotion, originalPrice, finalPrice, discountAmount, promotion }`

16. **Mapper** cập nhật `web/src/services/sport-api/productMappers.ts`:
    - Thêm logic gọi computed price API
    - Set `salePrice` từ API response thay vì `minPrice`

17. **ProductCard** cập nhật `web/src/components/ProductCard.tsx`:
    - Hiển thị giá gốc gạch ngang khi có promotion
    - Badge hiển thị % giảm
    - Test cases mới

18. **Web tests** tạo/cập nhật:
    - `web/src/__tests__/hooks/useComputedPrice.test.ts`
    - `web/src/__tests__/components/ProductCard.test.tsx` (thêm promotion cases)

### Phase 7: E2E Tests

19. **E2E** tạo `e2e_tests/tests/test_promotion_full_flow.py`:
    - Create promotion → activate → verify price on web
    - End promotion → verify price reverts

## Sub-tasks

- [ ] 1. Migration: tạo 4 bảng promotion
- [ ] 2. Models: thêm Promotion classes vào models.py
- [ ] 3. Schemas: tạo promotion.py với CRUD schemas
- [ ] 4. Service: tạo promotion_service.py với compute logic
- [ ] 5. Scheduler: tạo promotion_scheduler.py
- [ ] 6. Router: tạo promotions.py với CRUD + lifecycle APIs
- [ ] 7. Computed Price API: thêm endpoints
- [ ] 8. Backend tests: 5 test files
- [ ] 9. PMI Sidebar: thêm menu Promotions
- [ ] 10. PMI List page
- [ ] 11. PMI Create/Edit form
- [ ] 12. PMI Detail page
- [ ] 13. PMI Frontend tests
- [ ] 14. Web hook useComputedPrice
- [ ] 15. Web productMappers update
- [ ] 16. Web ProductCard update
- [ ] 17. Web tests
- [ ] 18. E2E test full flow

## Notes

- **Scope:** Chỉ áp dụng cho web (topvnsport.vn). Sàn TMĐT (Shopee, TikTok) có hệ thống giảm giá riêng.
- **User:** Marketing team quản lý, sau này sẽ là AI-agent.
- **Design doc:** `knowledge/research/discount-promotion-architecture.md`
- **Không phải MVP phân phase** — implement hoàn chỉnh một lần.

## Findings từ reviewer (@claude-opus, 2026-07-22)

**Verdict: `changes`** — Fundamental scope mismatch.

### Critical Issues

- [ ] **Wrong commit referenced**: result-ref `80875ec` là "feat(pmi): add product description formatting script" — không phải Promotion Module. Commit OMS work đang uncommitted.
- [ ] **Implementation in wrong system**: AC yêu cầu backend trong PMI, nhưng implementation nằm trong OMS.
- [ ] **Scope mismatch (Product-level vs Order-level)**: AC yêu cầu product-level promotion system (giá hiển thị trên ProductCard), nhưng implementation là order-level coupon system (giảm giá tại checkout).

### Missing AC Items (13+)

- [ ] **Backend PMI**: 4 bảng (chỉ có 2), Lifecycle APIs (/activate, /pause, /resume, /end), Preview API, Computed Price APIs, fixed_price discount type, auto-scheduler (cron), priority handling
- [ ] **Frontend PMI**: Toàn bộ Marketing Team UI (menu, list, create form, preview modal, detail page, lifecycle buttons)
- [ ] **Frontend Web**: useComputedPrice hook, productMappers.ts integration, ProductCard sale price display
- [ ] **AI-Agent Ready**: intent, ai_reasoning, created_by fields; /api/promotions/parse-intent endpoint

### Test Coverage Issues

- [ ] Tests đặt sai path (OMS thay vì PMI): AC yêu cầu `PMI/backend/tests/test_promotions_crud.py`, hiện tại là `e2e_tests/tests/test_promotions.py` (test OMS APIs)

### Next Steps cho Executor

1. Commit OMS coupon work riêng (nó hoạt động đúng, chỉ khác scope)
2. Clarify với stakeholder: Order-level coupons có đúng ý định không, hay vẫn cần PMI product-level pricing?
3. Nếu PMI scope được confirm, implement đúng như AC (có thể là task riêng)
