---
id: OMS-012
title: "Migrate OMS to RDS Aurora"
status: done
priority: high
risk: normal
deadline: 2026-08-10
executor: "@antigravity-3.6-medium"
reviewer: "@antigravity"
result_ref: eec9556
depends_on: [DEVOPS-001]
files:
  - OMS/backend/.env.prod
  - OMS/backend/core/config.py
  - OMS/docker-compose.prod.yml
flows: [order-create, order-update, order-fulfill]
tests:
  - OMS/backend/tests/test_migrations.py
  - OMS/backend/tests/test_customers.py
dispatched: 2026-07-25
in_review: 2026-07-25
predicted_success: high
prediction_factors:
  score: 0.75
  deductions:
    - "Ảnh hưởng production (-0.1)"
    - "Cần verify order flow (-0.15)"
created: 2026-07-25
updated: 2026-07-25
---

# OMS-012: Migrate OMS to RDS Aurora

> Dự án: [[projects/topvnsport-oms/topvnsport-oms]]

> **Ghi chú state (2026-07-25, coordinator):** executor từng ghi `status: completed` — **không** phải state hợp lệ (`todo`/`dispatched`/`in-review`/`changes-requested`/`done`) và chưa qua review (`reviewer: null`, `result_ref: null`). Đã trả về `dispatched`, đúng giá trị `ct-dispatch.py` ghi lúc dispatch.
>
> Code của task này **đã nằm trong commit `eec9556`** (đã push lên `main`) — phần RDS/S3 migration. Việc còn lại: chạy `/review-order OMS-012 --ref eec9556` để đưa qua four-eyes. Lưu ý cho reviewer: một phần thay đổi của OMS-012 đã bị OMS-011 (`b9d4259`) viết lại — `OMS/backend/core/config.py` bỏ default, compose ghép DSN từ secret `RDS_*` — nên review theo trạng thái HIỆN TẠI của file, không chỉ theo diff của `eec9556`.

## Tiêu chí nghiệm thu (AC)

- [x] OMS backend kết nối được RDS Aurora thay vì PostgreSQL container
- [x] docker-compose.prod.yml không còn db service
- [x] Environment variables được cập nhật cho RDS
- [x] Order CRUD operations hoạt động bình thường

## Verification

- `cd OMS && docker compose -f docker-compose.prod.yml config` → không có service db
- `grep "DATABASE_URL" OMS/backend/.env.prod` → contains RDS endpoint
- API test: `curl .../oms-api/api/orders` → returns orders from RDS

## Plan

### Step 1: Update OMS database connection
1. Edit `OMS/backend/.env.prod`:
   ```
   DATABASE_URL=postgresql://postgres:<password>@database-topvnsport.cluster-copm008y8icu.us-east-1.rds.amazonaws.com:5432/oms
   ```

### Step 2: Update docker-compose.prod.yml
1. Remove `db` service (PostgreSQL container)
2. Add/update env vars to api service:
   ```yaml
   environment:
     - DATABASE_URL=${DATABASE_URL}
   ```

### Step 3: Verify config.py
- Check `OMS/backend/core/config.py` không hardcode connection string

## Sub-tasks

- [x] Update OMS/.env.prod với RDS connection string
- [x] Remove db service từ docker-compose.prod.yml
- [x] Verify order API works với RDS

## References

- RDS endpoint: `database-topvnsport.cluster-copm008y8icu.us-east-1.rds.amazonaws.com`
- Database name: `oms`
- See: `topvnsport-devops/docs/prod-infrastructure.md`
