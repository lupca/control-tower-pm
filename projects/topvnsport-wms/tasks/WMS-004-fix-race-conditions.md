---
id: WMS-004
title: "Fix race conditions: receive scan, pick scan + row locking"
status: done
priority: high
risk: high
deadline: null
executor: "@antigravity-3.6-high"
reviewer: "@antigravity"
result_ref: "01ebdd7092f7a76bf5c8a20fdc1cefe2be5e3756"
depends_on: []
files:
  - WMS/backend/routers/inbound.py
  - WMS/backend/routers/fulfillment.py
flows: [receive, pick]
tests:
  - WMS/backend/tests/
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
rejections: 2
---

# WMS-004: Fix race conditions: receive scan, pick scan + row locking

> Dự án: [[projects/topvnsport-wms/topvnsport-wms]]

## Tiêu chí nghiệm thu (AC)

- [x] Receive scan có `with_for_update()` khi update `received_qty`
- [x] Pick scan có `with_for_update()` khi update `picked_qty`
- [x] Concurrent receive test: 10 operators scan cùng barcode → total = 10
- [x] Concurrent pick test: 10 pickers cùng order → correct total

## Verification

```python
# Test concurrent receive
results = await asyncio.gather(*[receive_scan(qty=1) for _ in range(10)])
shipment = get_shipment(1)
assert shipment.items[0].received_qty == 10  # Not less due to race
```

## Plan

1. **`WMS/backend/routers/inbound.py`**:
   - In `receive_scan_inbound_shipment`: Add `.with_for_update()` to the query for `models.InboundItem`.
   - Call `db.flush()` immediately after updating `received_qty` to persist the change within the transaction before returning.
2. **`WMS/backend/routers/fulfillment.py`**:
   - In `scan_pick_fulfillment_order`: Add `.with_for_update()` to the query for `models.PickListItem`.
   - Call `db.flush()` immediately after updating `picked_qty` to persist the lock and value.

## Sub-tasks

- [x] Add `with_for_update()` trong receive scan query
- [x] Add `with_for_update()` trong pick scan query
- [x] Add `db.flush()` sau update để persist ngay
- [x] Add concurrency tests

## Reference

- Debt file: `docs/TopVNSport - TODO & Technical Debt/wms/01_race_conditions.md`

## Findings từ reviewer
- [ ] DoD FAIL — test không 100% xanh: tests/test_concurrency.py::test_async_concurrent_receive_scan bị lỗi 'async def functions are not natively supported' vì pytest-asyncio không có trong WMS/backend/requirements.txt. Kết quả suite WMS/backend: 33 passed / 1 failed. Fix: thêm pytest-asyncio vào WMS/backend/requirements.txt — reviewer đã verify, cài xong thì cả 3 test concurrency đều PASS
- [ ] Test concurrency chạy trên SQLite (tests/conftest.py hardcode sqlite) — SQLAlchemy bỏ qua FOR UPDATE trên SQLite nên 2 test này KHÔNG thực sự verify row locking, chúng pass nhờ atomic UPDATE expression. Reviewer đã tự verify trên Postgres thật với 20 request đồng thời: received_qty=20 và picked_qty=20 đúng, trong khi code trước fix chỉ đạt 3/20 và 4/20. Đề nghị cho test concurrency chạy trên Postgres để thực sự cover row locking
- [ ] Minor — inbound.py:115 đặt db.refresh(item) SAU db.commit() nên mở transaction mới, received_qty trong response có thể đã bao gồm commit của request đồng thời khác. Dữ liệu lưu vẫn đúng, chỉ payload phản hồi lệch. Cân nhắc refresh trước commit như fulfillment.py:182

## Findings từ reviewer
- [ ] BLOCKER (mới, do chính commit 30b619a gây ra) — tests/conftest.py giờ lấy DATABASE_URL của môi trường (trong container wms-api = postgresql://postgres:postgres@wms-db:5432/wms_db, chạy từ host = localhost:15435/wms_db) rồi fixture gọi Base.metadata.drop_all() ở teardown, nên chạy đúng lệnh test của review sheet sẽ XÓA SẠCH toàn bộ bảng của DB dev wms_db. Reviewer đo trực tiếp: 10 bảng trước khi chạy pytest -> 0 bảng sau khi chạy. DB dev đã bị wipe sẵn từ lần chạy test của executor, GET /public/stock trả 500 với lỗi relation inventories does not exist. Fix: dùng DB test riêng (testcontainers hoặc TEST_DATABASE_URL trỏ tới database throwaway tự tạo/tự xóa), tuyệt đối không drop_all lên DB dùng chung, và fail-fast nếu URL test trùng DATABASE_URL của app
- [ ] conftest.get_database_url() im lặng fallback về SQLite khi không kết nối được Postgres. Reviewer verify với TEST_DATABASE_URL=sqlite: 3 test concurrency vẫn pass trong khi SQLAlchemy bỏ qua FOR UPDATE, tức coverage row-locking mất hoàn toàn mà suite vẫn xanh — đúng lỗ hổng mà finding vòng trước yêu cầu bịt. Nên skip/fail rõ ràng thay vì fallback âm thầm
- [ ] Finding minor vòng trước (đưa db.refresh(item) lên trước db.commit()) thực chất là no-op — SessionLocal trong database.py để expire_on_commit=True nên sau db.commit() mọi attribute bị expire, việc đọc item.received_qty trong return dict phát sinh SELECT mới ở transaction mới. Reviewer đo được đúng 1 SELECT sau commit. Muốn payload phản ánh giá trị đã lock thì phải đặt expire_on_commit=False hoặc gán ra biến local trước commit, áp dụng cho cả fulfillment.py:182
- [ ] Môi trường test không tái lập được nếu không rebuild — service trong WMS/docker-compose.yml tên là wms-api chứ không phải api (lệnh trong review sheet sai tên), và container đang chạy bị stale (thiếu pytest-asyncio, thiếu cả file test_concurrency.py) cho tới khi build lại image sau khi sửa requirements.txt. Ngoài ra job wms-backend trong .github/workflows/ci.yml chỉ chạy py_compile main.py chứ không chạy pytest nên CI không bảo vệ được các test này
