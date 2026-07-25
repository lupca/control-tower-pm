---
id: WEB-012
title: "Xóa dead code fallback trong findOrCreateCustomer"
status: done
priority: medium
risk: normal
deadline: null
executor: "@antigravity-3.6-high"
reviewer: "@antigravity"
result_ref: "c1eca2b"
depends_on: [OMS-015]
files:
  - web/src/services/sport-api/index.ts
  - web/src/services/sport-api/omsHelpers.ts
flows: [getOrCreateManualChannelId, getOrCreateStorefrontChannelId]
tests: []
dispatched: 2026-07-25
in_review: 2026-07-25
predicted_success: high
prediction_factors:
  score: 0.8
  deductions:
    - "no existing tests for index.ts: -0.1"
    - "simple cleanup, low risk: -0.0"
    - "depends_on OMS-015 (must deploy first): -0.1"
created: 2026-07-25
updated: 2026-07-25
---

# WEB-012: Xóa dead code fallback trong findOrCreateCustomer

> Dự án: [[projects/topvnsport-web/topvnsport-web]]

## Tiêu chí nghiệm thu (AC)

- [x] AC1: Xóa fallback GET trong `findOrCreateCustomer` (lines 294-296 hiện tại) — code này không bao giờ thành công vì `GET /customers` yêu cầu staff auth.
- [x] AC2: Xóa function `findExistingCustomerIdByPhone` trong `omsHelpers.ts` nếu không còn caller nào sau khi cleanup.
- [x] AC3: Unit test cho `findOrCreateCustomer`: mock POST trả 200 với customer → return id thành công.
- [x] AC4: Unit test cho `findOrCreateCustomer`: mock POST trả 409 với customer → return id thành công.
- [x] AC5: Unit test cho `findOrCreateCustomer`: mock POST trả 500 → throw error với message rõ ràng.
- [x] AC6: Không break flow checkout storefront — đặt đơn mới vẫn hoạt động.

## Verification

- `pnpm test` trong `web/` → tất cả test pass
- `grep -n "findExistingCustomerIdByPhone" web/src/` → không còn caller (hoặc chỉ còn trong test)
- Manual test: checkout trên storefront với phone mới → đơn hàng tạo thành công

## Plan

**Approach:** Remove dead code paths that call staff-only endpoint, add proper test coverage.

### 1. Clean up `findOrCreateCustomer` (`web/src/services/sport-api/index.ts`)

**Before:**
```typescript
async function findOrCreateCustomer(customer: OmsCustomerInput): Promise<number> {
  const existingCustomerId = await findExistingCustomerIdByPhone(customer.phone);  // REMOVE - always null (401)
  if (existingCustomerId !== null) {                                                // REMOVE
    return existingCustomerId;                                                      // REMOVE
  }                                                                                 // REMOVE

  const createResponse = await fetch(`${OMS_API_URL}/customers`, { ... });

  if (createResponse.ok || createResponse.status === 409) {
    const created = (await createResponse.json()) as OmsCustomer;
    if (created && typeof created.id === 'number') {
      return created.id;
    }
  }

  const fallbackCustomerId = await findExistingCustomerIdByPhone(customer.phone);  // REMOVE - always null (401)
  if (fallbackCustomerId !== null) {                                               // REMOVE
    return fallbackCustomerId;                                                     // REMOVE
  }                                                                                // REMOVE

  const errorText = await createResponse.text();
  throw new Error(`Failed to create customer: ${errorText}`);
}
```

**After:**
```typescript
async function findOrCreateCustomer(customer: OmsCustomerInput): Promise<number> {
  const createResponse = await fetch(`${OMS_API_URL}/customers`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(customer)
  });

  if (createResponse.ok || createResponse.status === 409) {
    const created = (await createResponse.json()) as OmsCustomer;
    if (created && typeof created.id === 'number') {
      return created.id;
    }
  }

  const errorText = await createResponse.text();
  throw new Error(`Failed to create customer: ${errorText}`);
}
```

### 2. Remove `findExistingCustomerIdByPhone` from `omsHelpers.ts`

- Check for other callers: `grep -rn "findExistingCustomerIdByPhone" web/src/`
- If no other callers, delete the function (lines 8-24)
- Remove from exports

### 3. Create test file `web/src/services/sport-api/__tests__/findOrCreateCustomer.test.ts`

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('findOrCreateCustomer', () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  it('returns customer id when POST returns 200', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({ id: 123, name: 'Test', phone: '0123456789' })
    });
    // ... assert returns 123
  });

  it('returns customer id when POST returns 409 (conflict)', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 409,
      json: async () => ({ id: 456, name: 'Existing', phone: '0123456789' })
    });
    // ... assert returns 456
  });

  it('throws error when POST returns 500', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      text: async () => 'Internal Server Error'
    });
    // ... assert throws with message
  });

  it('throws error when POST returns 400 without customer data', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
      text: async () => '{"detail":"Bad request"}'
    });
    // ... assert throws
  });
});
```

## Sub-tasks

- [ ] Xóa lines 294-296 trong `findOrCreateCustomer` (`web/src/services/sport-api/index.ts`)
- [ ] Xóa lines 276-279 (first call to `findExistingCustomerIdByPhone`) — không cần vì GET /customers 401
- [ ] Kiểm tra và xóa `findExistingCustomerIdByPhone` trong `omsHelpers.ts` nếu không còn caller
- [ ] Tạo test file `web/src/services/sport-api/__tests__/index.test.ts` với test cases cho `findOrCreateCustomer`

## Notes

**Context:** `findExistingCustomerIdByPhone` gọi `GET /customers?search=<phone>` — endpoint này yêu cầu staff auth (trả 401 cho public). Vì storefront là public user, cả lần gọi đầu (line 276) và fallback (line 294) đều return null.

**Sau OMS-015:** Backend POST /customers trả 200/409 với customer data khi phone đã tồn tại → không cần fallback GET.

**Dependency:** Task này phụ thuộc OMS-015 đã deploy. Nếu deploy WEB-012 trước OMS-015, checkout cho khách cũ vẫn fail (POST vẫn trả 400).
