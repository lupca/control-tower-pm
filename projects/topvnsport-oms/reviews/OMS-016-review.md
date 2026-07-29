---
task: OMS-016
title: "OMS Multi-channel Architecture Implementation"
reviewer: "@gemini-3.1-pro-high"
executor: "@gemini-3.6-flash"
result_ref: 362ef336eb53befebccbc2f9eeab802eb70ba2fc
created: 2026-07-28
---

# Review Sheet: OMS-016

## Result Reference
- Commit: `0dffdabe3b6af85c2de28d0f2827527e701b5f26`
- Branch: main (topvnsport repo)

## Acceptance Criteria

- [ ] Database migration adds multi-channel support tables (orders, payments, payment_ledger, invoices, order_events)
- [ ] Adapter pattern implemented: ChannelAdapter ABC, PaymentProvider ABC, InvoiceProvider ABC
- [ ] SePay refactored to adapter pattern with payment matching logic
- [ ] Event dispatcher system implemented (order.created, order.paid, order.completed, etc.)
- [ ] Background workers: channel_sync_worker, payment_reconcile_worker, invoice_batch_worker
- [ ] API endpoints for orders, payments, invoices, webhooks
- [ ] Unit tests for all adapters
- [ ] Integration tests for full flow

## Files Changed (30+)
- OMS/backend/adapters/channels/*.py
- OMS/backend/adapters/payments/*.py
- OMS/backend/adapters/invoices/*.py
- OMS/backend/events/*.py
- OMS/backend/workers/*.py
- OMS/backend/routers/*.py
- OMS/backend/alembic/versions/0007_add_multichannel_tables.py

## Review Checklist

1. [x] Run migrations and verify schema
2. [x] Run existing tests: `docker compose -f OMS/docker-compose.yml exec api pytest` (Failed: 4 tests failed due to missing pytest-asyncio)
3. [x] Verify adapter ABCs are correctly defined
4. [x] Verify SePay adapter implements PaymentProvider interface
5. [x] Check event dispatcher for proper async handling
6. [ ] Verify webhook endpoints have signature verification (Missing: webhook endpoints do not call verify_signature)
7. [x] Check for SQL injection / input validation issues
8. [x] Verify idempotency handling for webhooks

## Verdict

- [ ] PASS
- [x] CHANGES REQUESTED

### Notes
1. **Pytest Failure (4 test failures)**: `pytest-asyncio` is not included in `OMS/backend/requirements.txt` or installed in `oms_backend`, causing `@pytest.mark.asyncio` test functions in `test_adapters.py` (3 tests) and `test_multichannel_flow.py` (1 test) to fail with `Failed: async def functions are not natively supported.`
2. **Missing Webhook Signature Verification**: Webhook handlers in `routers/webhooks.py` (`/webhooks/sepay`, `/webhooks/vnpay`, `/webhooks/shopee`, `/webhooks/tiktok`, `/webhooks/lazada`) process requests without validating HMAC/HTTP signatures, leaving endpoints vulnerable to forged webhook payloads.

