---
id: WMS-006
title: "Migrate WMS to RDS Aurora"
status: completed
priority: high
risk: normal
deadline: 2026-08-10
executor: "@antigravity-3.6-medium"
reviewer: null
result_ref: null
depends_on: [DEVOPS-001]
files:
  - WMS/backend/.env.prod
  - WMS/backend/core/config.py
  - WMS/docker-compose.prod.yml
flows: [inventory-update, inbound, outbound]
tests:
  - WMS/backend/tests/test_inventory.py
dispatched: 2026-07-25
in_review: 2026-07-25
predicted_success: high
prediction_factors:
  score: 0.75
  deductions:
    - "Ảnh hưởng production (-0.1)"
    - "Cần verify inventory flow (-0.15)"
created: 2026-07-25
updated: 2026-07-25
---

# WMS-006: Migrate WMS to RDS Aurora

> Dự án: [[projects/topvnsport-wms/topvnsport-wms]]

## Tiêu chí nghiệm thu (AC)

- [x] WMS backend kết nối được RDS Aurora thay vì PostgreSQL container
- [x] docker-compose.prod.yml không còn db service
- [x] Environment variables được cập nhật cho RDS
- [x] Inventory CRUD operations hoạt động bình thường

## Verification

- `cd WMS && docker compose -f docker-compose.prod.yml config` → không có service db
- `grep "DATABASE_URL" WMS/backend/.env.prod` → contains RDS endpoint
- API test: `curl .../wms-api/api/inventory` → returns inventory from RDS

## Plan

### Step 1: Update WMS database connection
1. Edit `WMS/backend/.env.prod`:
   ```
   DATABASE_URL=postgresql://postgres:<password>@database-topvnsport.cluster-copm008y8icu.us-east-1.rds.amazonaws.com:5432/wms
   ```

### Step 2: Update docker-compose.prod.yml
1. Remove `db` service (PostgreSQL container)
2. Add/update env vars to api service:
   ```yaml
   environment:
     - DATABASE_URL=${DATABASE_URL}
   ```

### Step 3: Verify config.py
- Check `WMS/backend/core/config.py` không hardcode connection string

## Sub-tasks

- [x] Update WMS/.env.prod với RDS connection string
- [x] Remove db service từ docker-compose.prod.yml
- [x] Verify inventory API works với RDS

## References

- RDS endpoint: `database-topvnsport.cluster-copm008y8icu.us-east-1.rds.amazonaws.com`
- Database name: `wms`
- See: `topvnsport-devops/docs/prod-infrastructure.md`
