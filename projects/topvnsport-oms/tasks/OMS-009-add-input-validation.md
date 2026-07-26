---
id: OMS-009
title: "Add input validation (schema constraints)"
status: dispatched
priority: high
risk: normal
deadline: null
executor: "@antigravity-3.6-high"
reviewer: null
result_ref: c99fae89121913355ed28f5202aed5e437f0ffb7
depends_on: []
files:
  - OMS/backend/schemas/order.py
  - OMS/backend/schemas/common.py
flows: [order-create]
tests:
  - OMS/backend/test_main.py
dispatched: 2026-07-26
in_review: null
predicted_success: high
prediction_factors:
  score: 0.85
  deductions:
    - "schema_change: -0.15"
created: 2026-07-25
updated: 2026-07-26
rejections: 1
---

# OMS-009: Add input validation (schema constraints)

> Dự án: [[projects/topvnsport-oms/topvnsport-oms]]

## Tiêu chí nghiệm thu (AC)

- [x] `quantity` field có constraint `ge=1, le=9999`
- [x] `shipping_fee` có constraint `ge=0`
- [x] `phone` có regex validation cho VN format
- [x] `items` list có `min_items=1`
- [x] Invalid input trả về 422 với field-level errors

## Verification

```bash
# Test invalid quantity
curl -X POST /api/orders -d '{"items": [{"quantity": 0}]}'
# → 422: quantity must be >= 1

# Test invalid phone
curl -X POST /api/orders -d '{"customer_phone": "invalid"}'
# → 422: phone format invalid
```

## Plan

1. **`OMS/backend/schemas/order.py` & `OMS/backend/schemas/common.py`**:
   - Import `Field`, and `field_validator` from `pydantic`.
   - Add `Field(ge=1, le=9999)` to `quantity` inside `OrderItemInput`.
   - Add `Field(ge=0)` to `shipping_fee` inside `OrderCreateInput`.
   - Add `Field(min_items=1)` to `items` list inside `OrderCreateInput`.
   - Add a regex validator for the `phone` field using Pydantic's `pattern` argument or a custom validator (e.g., VN format `^(0|\+84)[3|5|7|8|9][0-9]{8}$`).
2. **Testing**:
   - Verify `OMS/backend/test_main.py` properly triggers HTTP 422 when invalid data is sent for these fields.

## Sub-tasks

- [x] Add Field constraints cho OrderItemInput
- [x] Add phone regex validator
- [x] Add shipping_fee constraint
- [x] Add items list min_items constraint
- [x] Add validation tests

## Reference

- Debt file: `docs/TopVNSport - TODO & Technical Debt/oms/02_business_logic_bugs.md`

## Findings từ reviewer
- [x] BLOCKING regression (out-of-scope file OMS/backend/schemas/auth.py): adding pattern=PHONE_REGEX to SendOtpRequest.phone_number and VerifyOtpRequest.phone_number breaks the storefront OTP flow. The handler in OMS/backend/routers/otp.py already calls utils.phone_helper.normalize_phone(), which is documented to strip spaces and hyphens, so those formats used to work. Verified against the rebuilt oms_backend container: POST /api/sms/send-otp with '0912345678 ' (trailing space), '091 234 5678' and '091-234-5678' now all return 422, while previously all three normalized to 84912345678 and returned 200. web/src/components/CartModal.tsx:71 calls sportApi.sendOtp(phone) with the RAW untrimmed input while line 86 uses phone.trim() for customer creation, and the input is a free-text type=tel field with no client-side normalization, so a single trailing space blocks checkout at the OTP step. Fix: either normalize before validating (field_validator with mode=before calling normalize_phone) or drop the pattern from auth.py and keep relying on normalize_phone. Please add a regression test for spaced/untrimmed phone input in OMS/backend/tests/test_otp.py. MINOR (non-blocking): PHONE_REGEX is duplicated verbatim in OMS/backend/schemas/common.py and OMS/backend/schemas/auth.py while OMS/backend/utils/phone_helper.py already owns phone handling — consider a single shared constant next to phone_helper. NOTE for the reviewer trail: all 5 AC verified green on POST /orders AND PUT /orders/{id} (quantity ge=1 and le=9999, shipping_fee ge=0, items min_length=1, VN phone regex, all returning 422 with field-level Vietnamese errors), OMS/backend/test_main.py 30 passed (3 consecutive runs), OMS/backend/tests/ 24 passed 1 skipped, no violating rows in oms_db. The OTP regression is the only blocker.

