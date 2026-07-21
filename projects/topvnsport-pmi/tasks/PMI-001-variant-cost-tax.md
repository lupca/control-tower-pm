---
id: PMI-001
title: "Thêm validation cost/tax cho variant"
status: done
priority: high
risk: normal
deadline: 2026-08-01
executor: null
reviewer: null
result_ref: null
depends_on: []
files:
  - PMI/backend/schemas/tier_variation.py
  - PMI/backend/alembic/versions/5a451ed7aa00_add_cost_tax_to_variants.py
flows: []
tests:
  - PMI/backend/tests/test_variant_cost_tax.py
  - PMI/backend/tests/test_product_api_cost_tax.py
dispatched: null
in_review: null
created: 2026-07-14
updated: 2026-07-21
---

# PMI-001: Thêm validation cost/tax cho variant

> Dự án: [[projects/topvnsport-pmi/topvnsport-pmi]]

## Tiêu chí nghiệm thu (AC)
- [x] Schema validation trong `PMI/backend/schemas/tier_variation.py` — `default_cost_price: Field(ge=0)`, `default_tax_rate: Field(ge=0, le=100)` đã có sẵn (dòng 26-27).
- [x] Migration DB tương ứng: `PMI/backend/alembic/versions/5a451ed7aa00_add_cost_tax_to_variants.py`.
- [x] Test coverage: `test_cost_price_must_be_non_negative`, `test_tax_rate_must_be_0_to_100` (test_variant_cost_tax.py) và `test_create_product_with_cost_tax`, `test_update_variant_cost_tax` (test_product_api_cost_tax.py) đã tồn tại.

## Ghi chú
Task này được chép từ file nháp gốc với path generic (`schema.py`, `test_product.py`). Khi chạy `semantic_search_nodes_tool`/CLI `search` để xác nhận path thật, phát hiện tính năng **đã được implement từ trước** (có migration + test đầy đủ) — không phải task còn tồn đọng. Đây chính là giá trị của việc luôn xác minh qua graph trước khi tin file nháp/ghi chú thô: task tưởng "cần làm" hóa ra đã "đã làm". Đánh dấu `done` theo Project Gate (đã pass 100% test liên quan). Nếu có yêu cầu mở rộng thêm (vd tax rate theo từng khu vực), hãy dùng `/pm` để tạo task mới thay vì mở lại task này.

## Plan
*(không cần — tính năng đã tồn tại sẵn trong code)*

## Sub-tasks
- [x] Schema validation trong `PMI/backend/schemas/tier_variation.py`
- [x] Migration DB tương ứng
- [x] Test coverage
