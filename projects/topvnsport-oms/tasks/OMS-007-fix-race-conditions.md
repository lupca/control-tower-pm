---
id: OMS-007
title: "Fix race conditions: order number, inventory allocation, OTP consumption"
status: done
priority: high
risk: high
deadline: null
executor: "@antigravity-3.6-high"
reviewer: "@claude-opus-5"
result_ref: "3924217f6a03c3b3f3ebfd78a1e3c417cd5c331b"
depends_on: []
files:
  - OMS/backend/routers/orders.py
  - OMS/backend/services/inventory_service.py
flows: [order-create, checkout]
tests:
  - OMS/backend/test_main.py
dispatched: 2026-07-26
in_review: 2026-07-26
predicted_success: medium
prediction_factors:
  score: 0.65
  deductions:
    - "risk_high: -0.2 (concurrency)"
    - "complex_logic: -0.15"
created: 2026-07-25
updated: 2026-07-26
---

# OMS-007: Fix race conditions: order number, inventory allocation, OTP consumption

> Dự án: [[projects/topvnsport-oms/topvnsport-oms]]

## Tiêu chí nghiệm thu (AC)

- [x] Order number generation sử dụng database sequence hoặc retry logic
- [x] OTP token consumption có `with_for_update()` row locking
- [x] Inventory allocation: reserve trong WMS trước khi confirm trong OMS
- [x] Concurrent order creation test passes (10 parallel requests → 10 unique order numbers)

## Verification

```python
# Test concurrent order creation
import asyncio
results = await asyncio.gather(*[create_order() for _ in range(10)])
order_numbers = [r["order_number"] for r in results]
assert len(set(order_numbers)) == 10  # All unique
```

- OTP test: 2 concurrent requests với same token → chỉ 1 succeed

## Plan

1. **`OMS/backend/routers/orders.py`**:
   - Update `create_order` OTP verification logic: Add `.with_for_update()` to the `otp_ver` query to lock the token row against concurrent consumption.
   - Refactor `order_number` generation: Instead of reading `count_today` unsafely, implement a retry loop that handles SQLAlchemy `IntegrityError` (UniqueViolation) to safely guarantee unique generation under concurrency, or introduce a daily sequence table with row locking.
2. **`OMS/backend/services/inventory_service.py`**:
   - Refactor `allocate_order_items`: Currently it only fetches an inventory snapshot. It needs to call a reserve endpoint or ensure that when `confirm_order` executes, the reservation in WMS uses atomic locks (which will be handled by WMS updates) and gracefully rolls back if allocation fails due to concurrent stock depletion.

## Sub-tasks

- [ ] Implement database sequence cho order number generation
- [ ] Add `with_for_update()` cho OTP token query
- [ ] Refactor inventory allocation: reserve-first pattern
- [ ] Add concurrency tests

## Reference

- Debt file: `docs/TopVNSport - TODO & Technical Debt/oms/02_business_logic_bugs.md`

## Causal Analysis
- **Root cause**: Check-then-act không nguyên tử: order_number sinh bằng COUNT(*) rồi INSERT, OTP đọc used_at rồi ghi, và confirm_order đặt status trước khi WMS reserve — tất cả không có khóa hàng hay ràng buộc nguyên tử bao quanh.
- **Mechanism**: Hai request đồng thời cùng đọc trạng thái cũ giữa lúc kiểm tra và lúc ghi: cùng COUNT ra một số thứ tự, cùng thấy used_at IS NULL, hoặc cùng chuyển DRAFT->CONFIRMED trước khi WMS trừ tồn, dẫn tới trùng order number, OTP bị dùng hai lần, và đơn được xác nhận vượt tồn kho.
- **Counterfactual**: Nếu mỗi chuỗi check-then-act được bọc bằng SELECT ... FOR UPDATE và/hoặc UPDATE có điều kiện dựa trên ràng buộc UNIQUE ngay từ đầu, hai request đồng thời sẽ bị tuần tự hóa ở tầng DB và lỗi đã không xảy ra.
- **Pattern**: [[race-condition]]
