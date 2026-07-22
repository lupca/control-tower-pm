# Phiếu Review: WEB-002 — Xóa code OMS coupon thừa từ WEB-001 lần 1

- Dự án: topvnsport-web (`/home/lupca/projects/topvnsport`)
- Task gốc: `projects/topvnsport-web/tasks/WEB-002-cleanup-oms-coupon-code.md`
- Result-ref: `topvnsport@main (commit 3380533)`
- Executor: @gpt-5.6-luna
- Ngày phát phiếu: 2026-07-22

## Acceptance Criteria cần verify

### OMS Backend
- [ ] Xóa `Promotion` class trong `OMS/backend/models.py`
- [ ] Xóa `PromotionUsage` class trong `OMS/backend/models.py`
- [ ] Xóa `discount_amount` và `promotion_code` fields trong `Order` class
- [ ] Xóa file `OMS/backend/schemas/promotion.py`
- [ ] Xóa promotion imports trong `OMS/backend/schemas/__init__.py`
- [ ] Xóa promotion endpoints trong `OMS/backend/main.py`

### Web Frontend
- [ ] Xóa coupon input section trong `web/src/components/CartModal.tsx`

### E2E Tests
- [ ] Xóa file `e2e_tests/tests/test_promotions.py`

### Verification
- [ ] `OMS/backend/test_main.py` pass (không regression)
- [ ] `e2e_tests/tests/test_full_flow.py` pass (checkout vẫn hoạt động)
- [ ] `e2e_tests/tests/test_promotion_full_flow.py` pass (PMI promotion vẫn OK)

## Definition of Done (AGENTS.md mục 3)

- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%:
  - `OMS/backend/test_main.py`
  - `e2e_tests/tests/test_full_flow.py`
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (bạn đang review, hãy xác nhận bạn ≠ @gpt-5.6-luna)

## Lưu ý quan trọng

### KHÔNG được xóa (kiểm tra vẫn còn):
- `PMI/backend/routers/promotions.py` — promotion module đúng
- `PMI/backend/schemas/promotion.py` — schemas của PMI
- `PMI/backend/services/promotion_service.py` — service của PMI
- `PMI/frontend/src/app/promotions/` — UI promotion của PMI
- `e2e_tests/tests/test_promotion_full_flow.py` — test PMI promotion

### Backend test failures đã biết (KHÔNG phải do WEB-002):
Executor báo 7 backend tests fail do thiếu auth token (401 Unauthorized) — đây là issue của test cũ, không phải regression từ cleanup này.

## Test gợi ý chạy trong repo code

```bash
# Frontend lint + tests
cd web && npm run lint && npm run test

# Backend tests (OMS)
docker compose -f OMS/docker-compose.yml exec api pytest OMS/backend/test_main.py -v

# E2E tests
cd e2e_tests && pytest tests/test_full_flow.py tests/test_promotion_full_flow.py -v
```

## Câu hỏi rủi ro

### Low Priority (cleanup task)
1. **Verify không xóa nhầm PMI code**: Confirm `PMI/backend/routers/promotions.py` và các file PMI promotion khác vẫn tồn tại.
2. **Verify CartModal vẫn hoạt động**: Checkout flow không bị break sau khi xóa coupon UI.

## Gợi ý công cụ

Repo code đích có sẵn skill `/code-review` — khuyến khích dùng để đọc diff + chạy test một cách có cấu trúc.

## Trả kết quả

Sau khi review xong, báo lại cho control-tower bằng lệnh:

```
/verdict WEB-002 <pass|changes> --reviewer @<tên bạn> --commit 3380533 [--notes "..."]
```
