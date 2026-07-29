---
id: OMS-017
title: "Chuyển SePay config vào Database"
status: done
completed: 2026-07-28
result_ref: 935005adbc50021abe5cf9e248890754268dc5e2
created: 2026-07-28
dispatched: 2026-07-28
updated: 2026-07-28
deadline: 2026-08-05
risk: medium
predicted_success: high
prediction_factors:
  score: 0.8
  deductions:
    - "touches existing sepay adapter: -0.1"
    - "requires frontend + backend: -0.1"
confidence_interval: [0.65, 0.90]
files:
  - OMS/backend/services/config_service.py
  - OMS/backend/services/sepay_service.py
  - OMS/backend/routers/payments.py
  - OMS/backend/routers/config.py
  - OMS/backend/adapters/payments/sepay.py
  - OMS/backend/routers/webhooks.py
  - OMS/frontend/src/app/settings/payment/page.tsx
  - OMS/frontend/src/components/settings/SepayConfigForm.tsx
  - OMS/frontend/src/services/configApi.ts
tests:
  - OMS/backend/tests/test_config_service.py
  - OMS/backend/tests/test_sepay_config_api.py
  - OMS/frontend/__tests__/SepayConfigForm.test.tsx
flows:
  - sepay-payment
  - admin-config
executor: "@gemini-3.6-flash"
reviewer: "@gemini-3.1-pro-high"
---

# OMS-017: Chuyển SePay config vào Database

> Dự án: [[projects/topvnsport-oms/topvnsport-oms]]

## Mục tiêu

Lưu SePay credentials vào bảng `system_configs` (đã có sẵn, encrypted) thay vì env vars. Cho phép quản lý qua Admin UI.

## Acceptance Criteria

- [ ] Helper function `get_config()` và `get_sepay_config()` trong `services/config_service.py`
- [ ] `SepayService` và `SePayAdapter` sử dụng config từ DB với fallback env vars
- [ ] API endpoints: GET/PUT `/api/config/sepay`, POST `/api/config/sepay/test`
- [ ] Admin UI trang `/settings/payment` với form quản lý SePay config
- [ ] Secret key được mask khi GET, encrypted khi lưu
- [ ] Unit tests cho config service và API endpoints
- [ ] Frontend tests cho SepayConfigForm

## Config keys cần thêm

| Key | Encrypted | Default |
|-----|-----------|---------|
| `sepay_merchant_id` | ✅ | - |
| `sepay_secret_key` | ✅ | - |
| `sepay_checkout_url` | ❌ | https://pay.sepay.vn/v1/checkout/init |
| `web_base_url` | ❌ | https://topvnsport.vn |

## Plan

### Task 1: Tạo helper function lấy config

```python
# services/config_service.py
import os
from sqlalchemy.orm import Session
import models

def get_config(db: Session, key: str, default: str = "") -> str:
    """Lấy config từ DB, fallback về env var"""
    config = db.query(models.SystemConfig).filter(
        models.SystemConfig.config_key == key
    ).first()
    if config and config.config_value:
        return config.config_value
    return os.getenv(key.upper(), default)

def get_sepay_config(db: Session) -> dict:
    return {
        "merchant_id": get_config(db, "sepay_merchant_id"),
        "secret_key": get_config(db, "sepay_secret_key"),
        "checkout_url": get_config(db, "sepay_checkout_url", "https://pay.sepay.vn/v1/checkout/init"),
        "web_base_url": get_config(db, "web_base_url", "https://topvnsport.vn"),
    }
```

### Task 2: Update SepayService

```python
# services/sepay_service.py
class SepayService:
    def __init__(self, db: Session):
        config = get_sepay_config(db)
        self.merchant_id = config["merchant_id"]
        self.secret_key = config["secret_key"]
        self.checkout_url = config["checkout_url"]
        self.web_base_url = config["web_base_url"]
```

### Task 3: Update payments router

```python
# routers/payments.py
@router.post("/checkout")
def create_checkout(req: CheckoutRequest, db: Session = Depends(get_db)):
    sepay = SepayService(db)  # Pass db để lấy config
    ...
```

### Task 4: Update SePayAdapter trong webhooks

```python
# adapters/payments/sepay.py
class SePayAdapter(PaymentProvider):
    def __init__(self, db: Session = None):
        if db:
            config = get_sepay_config(db)
            self.merchant_id = config["merchant_id"]
            self.secret_key = config["secret_key"]
        else:
            # Fallback env vars
            self.merchant_id = os.getenv("SEPAY_MERCHANT_ID", "")
            self.secret_key = os.getenv("SEPAY_SECRET_KEY", "")
```

### Task 5: Seed initial config (optional)

```python
# Trong startup hoặc migration
configs = [
    ("sepay_merchant_id", "SePay Merchant ID"),
    ("sepay_secret_key", "SePay Secret Key"),
    ("sepay_checkout_url", "SePay Checkout URL"),
    ("web_base_url", "Web Base URL"),
]
for key, desc in configs:
    if not db.query(SystemConfig).filter_by(config_key=key).first():
        db.add(SystemConfig(config_key=key, description=desc))
```

### Task 6: Admin UI (OMS Frontend)

**File: OMS/frontend/src/app/settings/payment/page.tsx**

```tsx
// Form quản lý SePay config
- Input: Merchant ID
- Input: Secret Key (masked)
- Input: Checkout URL
- Input: Web Base URL
- Button: Lưu
- Button: Test Connection (gọi API verify)
```

**File: OMS/frontend/src/services/configApi.ts**

```typescript
// API calls
getSepayConfig(): Promise<SepayConfig>
updateSepayConfig(config: SepayConfig): Promise<void>
testSepayConnection(): Promise<{success: boolean, message: string}>
```

**Files cần tạo/sửa Frontend:**

| File | Action |
|------|--------|
| OMS/frontend/src/app/settings/payment/page.tsx | Create |
| OMS/frontend/src/components/settings/SepayConfigForm.tsx | Create |
| OMS/frontend/src/services/configApi.ts | Modify (thêm sepay methods) |
| OMS/frontend/src/app/settings/layout.tsx | Modify (thêm menu Payment) |

### Task 7: API Endpoints cho config

**File: OMS/backend/routers/config.py**

```python
@router.get("/sepay")
def get_sepay_config(db: Session = Depends(get_db)):
    """Lấy SePay config (mask secret key)"""

@router.put("/sepay")
def update_sepay_config(payload: SepayConfigUpdate, db: Session = Depends(get_db)):
    """Cập nhật SePay config"""

@router.post("/sepay/test")
def test_sepay_connection(db: Session = Depends(get_db)):
    """Test kết nối SePay bằng cách gọi API health check"""
```

### Task 8: Test Specs

**File: OMS/backend/tests/test_config_service.py**

```python
def test_get_config_from_db():
    """Config trong DB được ưu tiên"""

def test_get_config_fallback_env():
    """Fallback về env var khi DB không có"""

def test_get_sepay_config_returns_all_fields():
    """Trả về đủ 4 fields"""
```

**File: OMS/backend/tests/test_sepay_config_api.py**

```python
def test_get_sepay_config_masks_secret():
    """Secret key được mask khi GET"""

def test_update_sepay_config():
    """Update thành công"""

def test_update_sepay_config_encrypts_secret():
    """Secret key được encrypt khi lưu"""

def test_test_sepay_connection_success():
    """Test connection trả về success"""

def test_test_sepay_connection_invalid_credentials():
    """Test connection với credentials sai"""
```

**File: OMS/frontend/__tests__/SepayConfigForm.test.tsx**

```typescript
it('loads current config on mount')
it('masks secret key in display')
it('shows full secret key when clicking reveal')
it('validates required fields')
it('calls API on save')
it('shows success toast after save')
it('shows error when test connection fails')
```

## Summary Files

| File | Action | Type |
|------|--------|------|
| services/config_service.py | Create | Backend |
| services/sepay_service.py | Modify | Backend |
| routers/payments.py | Modify | Backend |
| routers/config.py | Modify | Backend |
| adapters/payments/sepay.py | Modify | Backend |
| routers/webhooks.py | Modify | Backend |
| tests/test_config_service.py | Create | Backend |
| tests/test_sepay_config_api.py | Create | Backend |
| frontend/src/app/settings/payment/page.tsx | Create | Frontend |
| frontend/src/components/settings/SepayConfigForm.tsx | Create | Frontend |
| frontend/src/services/configApi.ts | Modify | Frontend |
| frontend/src/app/settings/layout.tsx | Modify | Frontend |
| frontend/__tests__/SepayConfigForm.test.tsx | Create | Frontend |

## Effort Estimate

| Task | Effort |
|------|--------|
| Task 1-5 (Backend service + endpoints) | 3h |
| Task 6 (Frontend UI) | 3h |
| Task 7 (API endpoints) | 1h |
| Task 8 (Tests) | 1h |
| **Total** | **8h** |
