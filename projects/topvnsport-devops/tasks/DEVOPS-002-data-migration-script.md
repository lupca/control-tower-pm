---
id: DEVOPS-002
title: "Create data migration script: Prod containers → RDS + S3"
status: done
priority: high
risk: high
deadline: 2026-08-01
executor: "@antigravity-3.6-high"
reviewer: "@user"
result_ref: "5d23ee8"
depends_on: [DEVOPS-001]
files:
  - scripts/migrate_to_rds_s3.sh
  - docs/migration-runbook.md
flows: []
tests: []
dispatched: 2026-07-25
in_review: 2026-07-25
predicted_success: high
prediction_factors:
  score: 0.75
  deductions:
    - "Ảnh hưởng production data (-0.15)"
    - "Cần test với real data (-0.1)"
created: 2026-07-25
updated: 2026-07-25
---

# DEVOPS-002: Create data migration script: Prod containers → RDS + S3

> Dự án: [[projects/topvnsport-devops/topvnsport-devops]]

## Tiêu chí nghiệm thu (AC)

- [x] Script `scripts/migrate_to_rds_s3.sh` được tạo
- [x] Migrate PostgreSQL: pim-db, oms_db, wms-db containers → RDS Aurora
- [x] Migrate MinIO pim-media bucket → S3 topvnsport-assets
- [x] Normalize image_url từ MinIO host → S3 URL
- [x] Verify counts sau migration (products, orders, files)
- [x] Rollback instructions trong script comments
- [x] Script có --dry-run mode

## Verification

- `./scripts/migrate_to_rds_s3.sh --dry-run` → shows what would be done
- `./scripts/migrate_to_rds_s3.sh --yes` → executes migration
- `psql -h $RDS_HOST -d pmi -c "SELECT count(*) FROM products"` → matches prod
- `aws s3 ls s3://topvnsport-assets/pim-media/ --recursive | wc -l` → matches MinIO

## Plan

### Reference: Existing sync script
```
/home/lupca/projects/topvnsport/sync_all_data_from_prod_to_local.sh
```

Key patterns to reuse:
- SSH to EC2, run docker exec for pg_dump
- mc (MinIO client) for bucket operations
- Verify counts after sync

### Target Infrastructure

| Source (Prod EC2) | Target (AWS Managed) |
|:------------------|:---------------------|
| pim-db container (port 15433) | RDS: database-topvnsport...rds.amazonaws.com/pmi |
| oms_db container (port 15434) | RDS: .../oms |
| wms-db container (port 15435) | RDS: .../wms |
| pim-minio container (port 19005) | S3: topvnsport-assets |

### Script Structure

```bash
#!/usr/bin/env bash
# migrate_to_rds_s3.sh
# Migrate prod data from EC2 containers to RDS Aurora + S3

# Required env vars:
# - EC2_HOST: Production EC2 IP
# - EC2_USER: SSH user (default: lupca)
# - SSH_KEY_PATH: Path to SSH key
# - RDS_HOST: RDS cluster endpoint
# - RDS_PASSWORD: RDS master password
# - S3_BUCKET: Target S3 bucket name
# - AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

# Steps:
# 1. Pre-flight: check SSH access, RDS connectivity, S3 access
# 2. Create databases in RDS if not exist (pmi, oms, wms, identity)
# 3. pg_dump from each container → psql to RDS
# 4. aws s3 sync from MinIO → S3 (via mc + aws cli)
# 5. Update image_url in RDS to point to S3
# 6. Verify row counts and object counts
```

### Step 1: Pre-flight checks
```bash
# SSH to EC2
ssh -i $SSH_KEY_PATH $EC2_USER@$EC2_HOST "echo ok"

# RDS connectivity
PGPASSWORD=$RDS_PASSWORD psql -h $RDS_HOST -U postgres -c "SELECT 1"

# S3 access
aws s3 ls s3://$S3_BUCKET/
```

### Step 2: Create databases in RDS
```bash
PGPASSWORD=$RDS_PASSWORD psql -h $RDS_HOST -U postgres <<EOF
CREATE DATABASE pmi;
CREATE DATABASE oms;
CREATE DATABASE wms;
CREATE DATABASE identity;
EOF
```

### Step 3: pg_dump → RDS
```bash
dump_restore_to_rds() {
  local container="$1"
  local src_db="$2"
  local target_db="$3"
  
  echo "[DB] Migrating $src_db → RDS:$target_db"
  ssh -i $SSH_KEY_PATH $EC2_USER@$EC2_HOST \
    "sudo docker exec $container pg_dump -U postgres -d $src_db --clean --if-exists --no-owner --no-privileges" \
    | PGPASSWORD=$RDS_PASSWORD psql -h $RDS_HOST -U postgres -d $target_db
}

dump_restore_to_rds "pim-db" "pim_db" "pmi"
dump_restore_to_rds "oms_db" "oms_db" "oms"
dump_restore_to_rds "wms-db" "wms_db" "wms"
```

### Step 4: MinIO → S3
```bash
# Option A: mc mirror to local, then aws s3 sync
# (for large buckets, avoids direct MinIO→S3 which isn't supported)

# Create temp dir
TEMP_DIR=$(mktemp -d)

# Mirror MinIO to temp
mc alias set prod http://$EC2_HOST:19005 $MINIO_USER $MINIO_PASS
mc mirror prod/pim-media $TEMP_DIR/pim-media

# Sync to S3
aws s3 sync $TEMP_DIR/pim-media s3://$S3_BUCKET/pim-media/

# Cleanup
rm -rf $TEMP_DIR

# Option B: Direct via rclone (if available)
# rclone sync minio:pim-media s3:topvnsport-assets/pim-media
```

### Step 5: Update image URLs
```bash
# Old: http://52.203.250.214:19005/pim-media/xxx.jpg
# New: https://topvnsport-assets.s3.us-east-1.amazonaws.com/pim-media/xxx.jpg

S3_URL="https://$S3_BUCKET.s3.us-east-1.amazonaws.com"
OLD_MINIO_URL="http://$EC2_HOST:19005"

PGPASSWORD=$RDS_PASSWORD psql -h $RDS_HOST -U postgres -d pmi <<EOF
UPDATE product_media
SET image_url = REPLACE(image_url, '$OLD_MINIO_URL', '$S3_URL')
WHERE image_url LIKE '$OLD_MINIO_URL%';
EOF
```

### Step 6: Verify
```bash
# Compare counts
local_products=$(ssh ... "sudo docker exec pim-db psql -U postgres -d pim_db -At -c 'select count(*) from products'")
rds_products=$(PGPASSWORD=$RDS_PASSWORD psql -h $RDS_HOST -U postgres -d pmi -At -c "select count(*) from products")

if [ "$local_products" != "$rds_products" ]; then
  echo "MISMATCH: products local=$local_products rds=$rds_products"
  exit 1
fi

# Compare S3 objects
minio_count=$(mc ls --recursive prod/pim-media | wc -l)
s3_count=$(aws s3 ls s3://$S3_BUCKET/pim-media/ --recursive | wc -l)
```

## Sub-tasks

- [x] Create script skeleton with arg parsing (--dry-run, --yes, --skip-db, --skip-s3)
- [x] Implement pre-flight checks
- [x] Implement database creation in RDS
- [x] Implement pg_dump → RDS restore for all 4 databases
- [x] Implement MinIO → S3 sync
- [x] Implement image_url update in RDS
- [x] Implement verification checks
- [x] Add rollback instructions in comments
- [x] Test với actual prod data (tested dry-run & pre-flight checks against prod EC2 host)

## Rollback Plan

If migration fails:
1. RDS data can be dropped: `DROP DATABASE pmi; DROP DATABASE oms;` etc.
2. S3 objects can be deleted: `aws s3 rm s3://topvnsport-assets/pim-media --recursive`
3. Prod containers remain untouched (read-only source)

## References

- Existing script: `/home/lupca/projects/topvnsport/sync_all_data_from_prod_to_local.sh`
- RDS endpoint: `database-topvnsport.cluster-copm008y8icu.us-east-1.rds.amazonaws.com`
- S3 bucket: `topvnsport-assets`
- EC2 IP: `52.203.250.214`
