---
id: PMI-023
title: "Migrate PMI + Identity to RDS and replace MinIO with S3"
status: dispatched
priority: high
risk: high
deadline: 2026-08-10
executor: "@gpt-5.6-luna-high"
reviewer: null
result_ref: null
depends_on: [DEVOPS-001]
files:
  - PMI/backend/.env.prod
  - PMI/backend/utils/storage.py
  - PMI/backend/core/config.py
  - PMI/docker-compose.prod.yml
  - identity/.env.prod
  - identity/docker-compose.prod.yml
flows: [product-create, product-update, file-upload, auth]
tests:
  - PMI/backend/tests/test_storage.py
dispatched: 2026-07-25
in_review: null
predicted_success: medium
prediction_factors:
  score: 0.6
  deductions:
    - "Thay đổi storage layer (-0.2)"
    - "Ảnh hưởng production (-0.1)"
    - "Cần test upload/download (-0.1)"
created: 2026-07-25
updated: 2026-07-25
---

# PMI-023: Migrate PMI + Identity to RDS and replace MinIO with S3

> Dự án: [[projects/topvnsport-pmi/topvnsport-pmi]]

## Tiêu chí nghiệm thu (AC)

- [ ] PMI backend kết nối được RDS Aurora thay vì PostgreSQL container
- [ ] Identity service kết nối được RDS Aurora
- [ ] MinIO client trong `utils/storage.py` được thay bằng boto3 S3
- [ ] Upload/download file hoạt động với S3
- [ ] docker-compose.prod.yml không còn db và minio services
- [ ] Environment variables được cập nhật cho RDS + S3

## Verification

- `cd PMI && docker compose -f docker-compose.prod.yml config` → không có service db, minio
- `grep -r "minio" PMI/backend/` → 0 matches (đã thay bằng boto3)
- `grep "DATABASE_URL" PMI/backend/.env.prod` → contains RDS endpoint
- API test: `curl -X POST .../api/products -F "image=@test.jpg"` → upload thành công

## Plan

### Step 1: Update PMI database connection
1. Edit `PMI/backend/.env.prod`:
   ```
   DATABASE_URL=postgresql://postgres:<password>@database-topvnsport.cluster-copm008y8icu.us-east-1.rds.amazonaws.com:5432/pmi
   ```
2. Edit `PMI/backend/core/config.py` nếu có hardcoded connection

### Step 2: Update Identity database connection
1. Edit `identity/.env.prod`:
   ```
   DATABASE_URL=postgresql://postgres:<password>@database-topvnsport.cluster-copm008y8icu.us-east-1.rds.amazonaws.com:5432/identity
   ```

### Step 3: Replace MinIO with S3 in storage.py
1. Remove minio dependency: `pip uninstall minio`
2. Add boto3: `pip install boto3`
3. Rewrite `PMI/backend/utils/storage.py`:
   - Replace `from minio import Minio` → `import boto3`
   - Replace MinIO client init → S3 client init
   - Update upload/download/delete methods to use S3 API
4. Update env vars: `MINIO_*` → `AWS_S3_*`, `S3_BUCKET`

### Step 4: Update docker-compose.prod.yml
1. Remove `db` service (PostgreSQL container)
2. Remove `minio` service
3. Add env vars to api service:
   ```yaml
   environment:
     - DATABASE_URL=${DATABASE_URL}
     - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
     - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
     - AWS_S3_BUCKET=${S3_BUCKET}
     - AWS_DEFAULT_REGION=us-east-1
   ```

### Step 5: Update requirements.txt
- Remove: `minio`
- Add: `boto3`

## Sub-tasks

- [ ] Update PMI/.env.prod với RDS connection string
- [ ] Update identity/.env.prod với RDS connection string
- [ ] Rewrite utils/storage.py từ MinIO → boto3 S3
- [ ] Update requirements.txt
- [ ] Remove db + minio services từ docker-compose.prod.yml
- [ ] Test upload/download với S3

## References

- RDS endpoint: `database-topvnsport.cluster-copm008y8icu.us-east-1.rds.amazonaws.com`
- S3 bucket: `topvnsport-assets`
- AWS region: `us-east-1`
- See: `topvnsport-devops/docs/prod-infrastructure.md`
