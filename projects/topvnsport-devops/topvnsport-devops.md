---
project: topvnsport-devops
full_name: "TopVNSport - DevOps (Infrastructure as Code)"
repo_root: /home/lupca/projects/topvnsport-devops
repo_url: git@github.com:lupca/topvnsport-devops.git
task_prefix: DEVOPS
next_task_id: 5
created: 2026-07-25
updated: 2026-07-25
---

# TopVNSport - DevOps

Infrastructure as Code (IaC) repository chứa Terraform để deploy hệ thống TopVNSport. Sử dụng GitHub Actions CI/CD để deploy hạ tầng.

## Tiến độ
| Trạng thái | Số task |
|:---|---:|
| done | 3 |
*(Cập nhật bởi `/report`)*

## Tasks
*(Cập nhật bởi `/report` — mỗi lần chạy sẽ regenerate lại toàn bộ danh sách này từ `tasks/*.md`)*
- [[DEVOPS-001-phase1-iac-foundation]] — Phase 1: IaC Foundation - Terraform + RDS + S3 Migration (done)
- [[DEVOPS-002-data-migration-script]] — Create data migration script: Prod containers → RDS + S3 (done)
- [[DEVOPS-003-verify-prod-migration]] — Verify Phase 1 migration on production (done)
- [[DEVOPS-004-domain-migration-voma-https]] — Domain migration voma.vn + HTTPS cho PIM/OMS/WMS (todo)

## Quy tắc phê duyệt riêng (Project Gates)
- Mọi thay đổi Terraform (`*.tf`) phải có `terraform plan` output trong PR trước khi merge.
- `terraform apply` chỉ được chạy qua GitHub Actions CI/CD, không manual apply.
- Các secret (API keys, credentials) phải được quản lý qua GitHub Secrets hoặc external secret manager, KHÔNG hardcode trong code.
- Mọi resource phải có tag `project: topvnsport`, `environment: <env>`, `managed_by: terraform`.

## Tech Stack
- **IaC:** Terraform
- **CI/CD:** GitHub Actions
- **Cloud Provider:** (TBD - AWS/GCP/Azure)
- **State Backend:** (TBD - S3/GCS/Azure Blob với state locking)

## References
| Tài liệu | Path | Mô tả |
|:---|:---|:---|
| CLAUDE.md | `CLAUDE.md` | Dev conventions, terraform commands |
