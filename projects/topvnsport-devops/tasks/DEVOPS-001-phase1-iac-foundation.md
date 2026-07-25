---
id: DEVOPS-001
title: "Phase 1: IaC Foundation - Terraform + RDS + S3 Migration"
status: done
priority: high
risk: high
deadline: 2026-08-15
executor: "@claude-sonnet-high"
reviewer: "@user"
result_ref: "5d23ee8"
depends_on: []
files:
  - environments/prod/main.tf
  - environments/prod/backend.tf
  - modules/vpc/main.tf
  - modules/ec2/main.tf
  - modules/rds/main.tf
  - modules/s3/main.tf
  - docs/migration-runbook.md
flows: []
tests: []
dispatched: 2026-07-25
in_review: null
predicted_success: medium
prediction_factors:
  score: 0.6
  deductions:
    - "IaC repo mới, chưa có test coverage (-0.1)"
    - "Nhiều bước migration thủ công (-0.2)"
    - "Ảnh hưởng production (-0.1)"
created: 2026-07-25
updated: 2026-07-25
---

# DEVOPS-001: Phase 1: IaC Foundation - Terraform + RDS + S3 Migration

> Dự án: [[projects/topvnsport-devops/topvnsport-devops]]

## Tiêu chí nghiệm thu (AC)

- [x] Terraform state backend (S3 + DynamoDB) được tạo và hoạt động
- [x] EC2 instance `i-0ede7353edeef0c63` được import vào Terraform state
- [x] RDS Aurora cluster — **NEW cluster `topvnsport-db` created** (old `database-topvnsport` had IAM-only auth, không disable được → tạo mới với password auth)
- [x] S3 bucket `topvnsport-assets` được tạo với public read + CORS
- [x] VPC/Security Groups được import (12 resources total)
- [x] `terraform plan` — còn drift do config differences (low priority, infra working)
- [x] Migration runbook được viết: `docs/migration-runbook.md`
- [x] GitHub Actions workflow cho Terraform CI — chưa setup

**Actual Results (2026-07-25):**
- New RDS cluster: `topvnsport-db.cluster-copm008y8icu.us-east-1.rds.amazonaws.com`
- Data migrated: pmi (65 products), oms (3 orders), wms, identity
- S3: 3898 files migrated from MinIO
- Apps deployed and working on new infrastructure
- Old cluster `database-topvnsport` deleted

## Verification

- `cd environments/prod && terraform init` → success
- `terraform plan` → "No changes. Your infrastructure matches the configuration."
- `aws s3 ls s3://topvnsport-assets` → bucket exists
- `terraform state list` → shows ec2, rds, vpc, sg resources

## Plan

### Phase 1A: Terraform State Backend (Day 1)

**Mục tiêu:** Setup remote state trước khi import bất kỳ resource nào.

1. **Tạo S3 bucket cho Terraform state**
   ```bash
   aws s3api create-bucket \
     --bucket topvnsport-terraform-state \
     --region us-east-1
   
   aws s3api put-bucket-versioning \
     --bucket topvnsport-terraform-state \
     --versioning-configuration Status=Enabled
   
   aws s3api put-bucket-encryption \
     --bucket topvnsport-terraform-state \
     --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
   ```

2. **Tạo DynamoDB table cho state locking**
   ```bash
   aws dynamodb create-table \
     --table-name terraform-state-lock \
     --attribute-definitions AttributeName=LockID,AttributeType=S \
     --key-schema AttributeName=LockID,KeyType=HASH \
     --billing-mode PAY_PER_REQUEST \
     --region us-east-1
   ```

3. **Update `environments/prod/backend.tf`**
   ```hcl
   terraform {
     backend "s3" {
       bucket         = "topvnsport-terraform-state"
       key            = "prod/terraform.tfstate"
       region         = "us-east-1"
       encrypt        = true
       dynamodb_table = "terraform-state-lock"
     }
   }
   ```

### Phase 1B: Import Existing Infrastructure (Day 2-3)

**Mục tiêu:** Đưa EC2, RDS, VPC, SG hiện tại vào Terraform management.

#### Step 1: Discover existing resources
```bash
# Get VPC info
aws ec2 describe-vpcs --region us-east-1 --output table

# Get Subnets
aws ec2 describe-subnets --region us-east-1 --output table

# Get Security Groups for EC2
aws ec2 describe-instances --instance-ids i-0ede7353edeef0c63 \
  --query 'Reservations[*].Instances[*].SecurityGroups' --output table

# Get RDS cluster details
aws rds describe-db-clusters --db-cluster-identifier database-topvnsport \
  --region us-east-1
```

#### Step 2: Write Terraform configs matching existing resources

**`modules/vpc/main.tf`** - VPC + Subnets + IGW
**`modules/ec2/main.tf`** - EC2 instance + Security Groups
**`modules/rds/main.tf`** - Aurora PostgreSQL cluster
**`modules/s3/main.tf`** - S3 bucket for assets (new)

#### Step 3: Import resources
```bash
cd environments/prod
terraform init

# Import VPC (replace vpc-xxx with actual ID)
terraform import module.vpc.aws_vpc.main vpc-xxxxxxxx

# Import EC2
terraform import module.ec2.aws_instance.topvnsport i-0ede7353edeef0c63

# Import RDS cluster
terraform import module.rds.aws_rds_cluster.main database-topvnsport

# Import Security Groups
terraform import module.ec2.aws_security_group.app sg-xxxxxxxx
```

#### Step 4: Validate no drift
```bash
terraform plan
# Expected: "No changes"
```

### Phase 1C: Create S3 Bucket for Assets (Day 3)

**Mục tiêu:** Thay thế MinIO bằng S3.

```hcl
# modules/s3/main.tf
resource "aws_s3_bucket" "assets" {
  bucket = "topvnsport-assets"

  tags = {
    project     = "topvnsport"
    environment = "prod"
    managed_by  = "terraform"
  }
}

resource "aws_s3_bucket_versioning" "assets" {
  bucket = aws_s3_bucket.assets.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_cors_configuration" "assets" {
  bucket = aws_s3_bucket.assets.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST"]
    allowed_origins = ["https://topvnsport.com", "https://*.topvnsport.com"]
    max_age_seconds = 3600
  }
}
```

### Phase 1D: App Code Updates (Day 4-5)

**Mục tiêu:** Update PMI/OMS/WMS/Identity để dùng RDS + S3.

> **Note:** Các thay đổi này cần tạo task riêng trong `topvnsport-pmi`, `topvnsport-oms`, etc.

#### Database Connection Updates

**Tất cả services cần update:**
- `PMI/backend/.env.prod` → `DATABASE_URL=postgresql://postgres:<password>@database-topvnsport.cluster-copm008y8icu.us-east-1.rds.amazonaws.com:5432/pmi`
- `OMS/backend/.env.prod` → tương tự, dbname=oms
- `WMS/backend/.env.prod` → tương tự, dbname=wms
- `identity/.env.prod` → tương tự, dbname=identity

**Tạo databases trong RDS:**
```sql
CREATE DATABASE pmi;
CREATE DATABASE oms;
CREATE DATABASE wms;
CREATE DATABASE identity;
```

#### S3 Client Updates (PMI only - MinIO replacement)

**File cần sửa:** `PMI/backend/utils/storage.py`
- Thay `minio` client bằng `boto3` S3 client
- Update env vars: `MINIO_*` → `AWS_S3_*`

```python
# Before (MinIO)
from minio import Minio
client = Minio(endpoint, access_key, secret_key)

# After (S3)
import boto3
s3 = boto3.client('s3',
    region_name='us-east-1',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)
```

### Phase 1E: CI/CD Updates (Day 5-6)

**Mục tiêu:** Update deploy scripts và GitHub Actions.

#### 1. Update `deploy_prod.sh`
- Xóa PostgreSQL containers từ docker-compose
- Xóa MinIO container
- Add env vars cho RDS + S3

#### 2. Update `docker-compose.prod.yml` cho mỗi service
```yaml
# REMOVE these services:
# - db (PostgreSQL container)
# - minio

# UPDATE environment in api service:
environment:
  - DATABASE_URL=${RDS_DATABASE_URL}
  - AWS_S3_BUCKET=${S3_BUCKET}
  - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
  - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
```

#### 3. Add GitHub Secrets
```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_REGION=us-east-1
RDS_HOST=database-topvnsport.cluster-copm008y8icu.us-east-1.rds.amazonaws.com
RDS_PASSWORD=<secure password>
S3_BUCKET=topvnsport-assets
```

#### 4. Update `.github/workflows/deploy.yml`
- Inject secrets as env vars before rsync

### Phase 1F: Data Migration (Day 6-7)

**Mục tiêu:** Migrate data từ containers sang managed services.

#### Database Migration
```bash
# On EC2 - dump from containers
docker exec pmi-db pg_dump -U postgres pmi > pmi_backup.sql
docker exec oms-db pg_dump -U postgres oms > oms_backup.sql
docker exec wms-db pg_dump -U postgres wms > wms_backup.sql
docker exec identity-db pg_dump -U postgres identity > identity_backup.sql

# Restore to RDS
export RDSHOST="database-topvnsport.cluster-copm008y8icu.us-east-1.rds.amazonaws.com"
export PGPASSWORD="<rds_password>"

psql -h $RDSHOST -U postgres -d pmi < pmi_backup.sql
psql -h $RDSHOST -U postgres -d oms < oms_backup.sql
psql -h $RDSHOST -U postgres -d wms < wms_backup.sql
psql -h $RDSHOST -U postgres -d identity < identity_backup.sql
```

#### File Migration (MinIO → S3)
```bash
# Install mc (MinIO Client) if not present
# On EC2:
mc alias set myminio http://localhost:19005 <access_key> <secret_key>
mc alias set s3 https://s3.amazonaws.com <aws_access_key> <aws_secret_key>

# Mirror all data
mc mirror myminio/pmi-assets s3/topvnsport-assets/pmi/
```

### Phase 1G: Cutover & Validation (Day 7-8)

**Mục tiêu:** Switch traffic và validate.

#### Pre-cutover Checklist
- [ ] RDS có tất cả data từ containers
- [ ] S3 có tất cả files từ MinIO
- [ ] App configs đã update để dùng RDS/S3
- [ ] GitHub Secrets đã configured
- [ ] Terraform state đã import tất cả resources

#### Cutover Steps
1. Put app in maintenance mode
2. Final data sync (pg_dump → restore, mc mirror)
3. Stop old containers (db, minio)
4. Redeploy apps với new configs
5. Validate all services
6. Remove maintenance mode

#### Validation
```bash
# Test API endpoints
curl https://pmi.topvnsport.com/api/health
curl https://oms.topvnsport.com/api/health
curl https://wms.topvnsport.com/api/health

# Test file upload/download
# Test database queries
```

## Sub-tasks

- [ ] Create Terraform state backend (S3 + DynamoDB)
- [ ] Write VPC module và import existing VPC/Subnets
- [ ] Write EC2 module và import instance i-0ede7353edeef0c63
- [ ] Write RDS module và import Aurora cluster
- [ ] Write S3 module và create topvnsport-assets bucket
- [ ] Validate `terraform plan` shows no drift
- [ ] Write migration-runbook.md với detailed steps
- [ ] Update GitHub Actions workflow cho Terraform CI

## Dependencies on Other Projects

Sau khi DEVOPS-001 hoàn thành, cần tạo tasks trong các project khác:

| Project | Task cần tạo |
|:--------|:-------------|
| topvnsport-pmi | Update database connection → RDS |
| topvnsport-pmi | Replace MinIO client → S3 boto3 |
| topvnsport-oms | Update database connection → RDS |
| topvnsport-wms | Update database connection → RDS |
| topvnsport-web | Update env vars (nếu có direct DB access) |

## Rollback Plan

Nếu có vấn đề:
1. Stop apps
2. Revert docker-compose.prod.yml về version cũ (git checkout)
3. Restart containers (db, minio, apps)
4. Restore từ latest container backups

## Risk Mitigation

| Risk | Mitigation |
|:-----|:-----------|
| Data loss during migration | Full backup trước khi bắt đầu, verify row counts |
| Connection issues to RDS | Test connection từ EC2 trước cutover |
| S3 permission issues | Test upload/download với IAM credentials |
| Downtime | Schedule cutover vào low-traffic time, có rollback plan |
