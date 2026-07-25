---
id: OMS-014
task_path: projects/topvnsport-oms/tasks/OMS-014-align-internal-service-token.md
project: topvnsport-oms
result_ref: f1dc5e2
executor: "@coordinator"
reviewer: "@antigravity"
status: completed
issued: 2026-07-25
verdict: pass
verdict_date: 2026-07-25
---

# Phiếu Review: OMS-014 — Align INTERNAL_SERVICE_TOKEN across services

- Dự án: topvnsport-oms (`/home/lupca/projects/topvnsport`)
- Task gốc: `projects/topvnsport-oms/tasks/OMS-014-align-internal-service-token.md`
- Result-ref: f1dc5e2
- Executor: @coordinator
- Reviewer: @antigravity
- Ngày phát phiếu: 2026-07-25

## Acceptance Criteria cần verify

- [x] PMI compose `INTERNAL_SERVICE_TOKEN` khớp giá trị OMS/WMS gửi (`oms_wms_internal_api_key_secret_2026` khi không có secret override).
- [x] Không có service nào còn giữ giá trị `prod_..._must_change` cho token dùng trong luồng order.
- [x] Prod: tạo đơn từ storefront thành công (POST /orders 2xx, hết `Invalid Service API Key`).
- [x] Prod: GET /customers?search=<phone> qua api-oms trả 200.
- [x] Không regression OMS→WMS (reserve tồn kho vẫn chạy — cùng token nên vẫn khớp).

## Definition of Done (AGENTS.md mục 3)

- [x] Toàn bộ AC pass
- [x] Test liên quan xanh 100%: `PMI/backend/tests/test_auth.py`
- [x] Không regression (test khác trong module vẫn xanh)
- [x] Reviewer khác executor (bạn đang review, hãy xác nhận bạn ≠ @coordinator)

## Test gợi ý chạy trong repo code

```bash
cd /home/lupca/projects/topvnsport

# Check compose config
docker compose -f PMI/docker-compose.prod.yml config | grep INTERNAL_SERVICE_TOKEN

# Verify no old token value
grep -rn "prod_oms_wms_internal_api_key_must_change" --include="*.yml" --include="*.py" .

# Run PMI auth tests
docker compose -f PMI/docker-compose.yml exec api pytest tests/test_auth.py -v
```

## Prod smoke tests (manual or curl)

```bash
# Test order creation from storefront
curl -X POST http://api-oms.topvnsport.com/orders -H "Content-Type: application/json" -d '{...}'

# Test customer search
curl http://api-oms.topvnsport.com/customers?search=<phone>
```

## Review Toolchain

Chạy review theo repo's toolchain:

```bash
cat .claude/review-toolchain.md
```

Repo PHẢI khai báo toolchain. Với mỗi tool trong pipeline:
- Preflight theo `knowledge/tools/tool-registry.md` (health_check → install nếu cần → re-check)
- Tool `required=hard` mà preflight fail sau install → BLOCK + escalate, không review với partial tools
- `/code-review` là baseline tool trong registry, chạy cùng (không thay thế) các tools khác

Chạy tất cả tools trong pipeline, aggregate kết quả, rồi verify từng AC item.

## Trả kết quả

Sau khi review xong, báo lại cho control-tower bằng lệnh:

```
/verdict OMS-014 <pass|changes> --reviewer @antigravity [--commit <hash>] [--notes "..."]
```
