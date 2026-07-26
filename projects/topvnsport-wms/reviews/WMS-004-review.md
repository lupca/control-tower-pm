---
id: WMS-004
task_path: projects/topvnsport-wms/tasks/WMS-004-fix-race-conditions.md
project: topvnsport-wms
result_ref: 01ebdd7092f7a76bf5c8a20fdc1cefe2be5e3756
executor: "@antigravity-3.6-high"
reviewer: "@antigravity"
status: passed
issued: 2026-07-26
verdict: pass
verdict_date: 2026-07-26
---

# Phiếu Review: WMS-004 — Fix race conditions: receive scan, pick scan + row locking

- Dự án: topvnsport-wms (`/home/lupca/projects/topvnsport`)
- Task gốc: `projects/topvnsport-wms/tasks/WMS-004-fix-race-conditions.md`
- Result-ref: 01ebdd7092f7a76bf5c8a20fdc1cefe2be5e3756
- Executor: @antigravity-3.6-high
- Ngày phát phiếu: 2026-07-26

## Acceptance Criteria cần verify
- [x] Receive scan có `with_for_update()` khi update `received_qty`
- [x] Pick scan có `with_for_update()` khi update `picked_qty`
- [x] Concurrent receive test: 10 operators scan cùng barcode → total = 10
- [x] Concurrent pick test: 10 pickers cùng order → correct total

## Definition of Done (AGENTS.md mục 3)
- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: WMS/backend/tests/
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (bạn đang review, hãy xác nhận bạn ≠ @antigravity-3.6-high)

## Test gợi ý chạy trong repo code
docker compose -f WMS/docker-compose.yml exec api pytest WMS/backend/tests/

## Review Toolchain
Chạy review theo repo's toolchain:
  cat .claude/review-toolchain.md
Repo PHẢI khai báo toolchain. Với mỗi tool trong pipeline:
  - Preflight theo knowledge/tools/tool-registry.md (health_check → install nếu cần → re-check)
  - Tool required=hard mà preflight fail sau install → BLOCK + escalate, không review với partial tools
  - /code-review là baseline tool trong registry, chạy cùng (không thay thế) các tools khác
Chạy tất cả tools trong pipeline, aggregate kết quả,
rồi verify từng AC item.

## Trả kết quả
Sau khi review xong, báo lại cho control-tower bằng lệnh:
`/verdict WMS-004 <pass|changes> --reviewer @<tên bạn> [--commit <hash>] [--notes "..."]`
