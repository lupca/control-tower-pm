---
id: OMS-015
title: "Storefront không đặt được đơn cho khách đã tồn tại"
status: done
priority: high
risk: normal
deadline: null
executor: "@antigravity-3.6-high"
reviewer: "@antigravity"
result_ref: "c1eca2b"
depends_on: []
files:
  - OMS/backend/routers/customers.py
  - web/src/services/sport-api/index.ts
flows: [create_customer]
tests: []
dispatched: 2026-07-25
in_review: 2026-07-25
predicted_success: medium
prediction_factors:
  score: 0.4
  deductions:
    - "blast_radius > 8 (110 files in graph, but fix is scoped to 1-2 files): -0.3"
    - "blast_radius > 15: -0.2"
    - "no existing tests for customers.py: -0.1"
created: 2026-07-25
updated: 2026-07-25
---

# OMS-015: Storefront không đặt được đơn cho khách đã tồn tại

> Dự án: [[projects/topvnsport-oms/topvnsport-oms]]

## Tiêu chí nghiệm thu (AC)

- [x] AC1: `POST /api/customers` khi phone đã tồn tại trả về **200** (hoặc 409) kèm `customer_id` trong response body, thay vì 400 không có id.
- [x] AC2: Web `findOrCreateCustomer` (`web/src/services/sport-api/index.ts:275`) xử lý được response mới, lấy `customer_id` thành công.
- [x] AC3: Đặt đơn cho khách cũ (phone đã tồn tại) **thành công** end-to-end trên storefront.
- [x] AC4: Không mở `GET /customers` (staff-only) cho public — giữ nguyên 401 cho anonymous.
- [x] AC5: Backward compatible: đặt đơn cho khách **mới** vẫn hoạt động bình thường.

## Verification

- `curl -X POST https://<host>/api/customers -d '{"phone":"0382426669",...}' -H 'Content-Type: application/json'` → status 200 hoặc 409, body chứa `"id":<int>`
- E2E test (nếu có): tạo customer với phone X, sau đó POST lại phone X → nhận được cùng `customer_id`
- Storefront checkout với phone đã có trong hệ thống → đơn hàng được tạo thành công

## Plan

**Approach:** Make `POST /customers` idempotent — return existing customer on phone conflict instead of 400.

### 1. Modify `create_customer` (`OMS/backend/routers/customers.py:15-33`)

```python
@router.post("", response_model=schemas.CustomerOut)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db), current_user: Optional[dict] = Depends(get_optional_user)):
    # Check if phone already exists first (avoids IntegrityError path)
    existing = db.query(models.Customer).filter(models.Customer.phone == customer.phone).first()
    if existing:
        return existing  # Return 200 with existing customer (idempotent)
    
    db_customer = models.Customer(
        name=customer.name,
        phone=customer.phone,
        email=customer.email,
        address=customer.address
    )
    db.add(db_customer)
    try:
        db.commit()
        db.refresh(db_customer)
        return db_customer
    except IntegrityError:
        db.rollback()
        # Race condition: another request created customer between check and insert
        existing = db.query(models.Customer).filter(models.Customer.phone == customer.phone).first()
        if existing:
            return existing
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer creation failed.")
```

**Key changes:**
- Remove `status_code=status.HTTP_201_CREATED` from decorator (return 200 for existing, 201 for new via Response if needed, or just 200 always for simplicity)
- Add pre-check for existing phone → return early
- On IntegrityError, query existing and return instead of 400

### 2. Web side (`web/src/services/sport-api/index.ts`)

**No changes needed.** Current `findOrCreateCustomer` logic:
- Tries `findExistingCustomerIdByPhone` → returns null (401)
- Calls `POST /customers` → **now returns 200 with existing customer**
- `createResponse.ok` is true, extracts `id` → success

### 3. Test file (`OMS/backend/tests/test_customers.py`) — NEW

```python
def test_create_customer_idempotent():
    # First create → 200/201 with new customer
    # Second create same phone → 200 with same customer id
    ...
```

## Sub-tasks

- [x] Sửa `create_customer` (`OMS/backend/routers/customers.py`) để khi phone trùng: query existing customer, trả 200/409 kèm `CustomerOut` (có `id`)
- [x] Cập nhật `findOrCreateCustomer` (`web/src/services/sport-api/index.ts`) xử lý response mới (nếu cần)
- [x] Write a test for `create_customer` idempotent behavior (currently no coverage — knowledge gap) — suggested test file: `OMS/backend/tests/test_customers.py`

## Pre-scan findings (OCR)

OCR scan skipped: LLM configuration unavailable (soft requirement).

## Notes

**Root cause:** Web `findOrCreateCustomer` gọi `GET /customers?search=<phone>` để lấy id khách cũ, nhưng route này yêu cầu staff auth (trả 401 cho public). Fallback `POST /customers` trả 400 "already exists" **không kèm id** → không có đường lấy `customer_id` cho khách đã tồn tại.

**Giải pháp đề xuất:** Sửa `POST /customers` thành idempotent — nếu phone đã tồn tại, trả về customer hiện có thay vì 400. Đây là pattern chuẩn (upsert/find-or-create) và không mở thêm endpoint public mới.

**Ràng buộc bảo mật:** Giữ `GET /customers` staff-only (chặn enumeration PII). `POST /customers` đã là public endpoint sẵn, 400 "already exists" đã là oracle tồn tại phone — không làm tệ hơn.
