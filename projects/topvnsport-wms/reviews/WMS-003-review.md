# Phiếu Review: WMS-003 — Fix CI Docker Compose network label mismatch for oms_default

- Dự án: topvnsport-wms (`/home/lupca/projects/topvnsport`)
- Task gốc: `projects/topvnsport-wms/tasks/WMS-003-fix-ci-docker-network-label-mismatch.md`
- Result-ref: `feature/WMS-003-fix-ci-docker-network-label-mismatch`
- Executor: @antigravity
- Ngày phát phiếu: 2026-07-22

## Acceptance Criteria cần verify

- [ ] E2E workflow (`e2e.yml`) passes on a clean CI runner (no stale networks)
- [ ] E2E workflow passes on a CI runner with pre-existing networks from a previous run
- [ ] Local `./start_all.sh` still works correctly for dev environment
- [ ] All subsystems (PMI, OMS, WMS, web, gateway) can communicate across their shared networks

## Definition of Done (AGENTS.md mục 3)

- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: `e2e_tests/tests/test_full_flow.py`
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (bạn đang review, hãy xác nhận bạn ≠ @antigravity)

## Test gợi ý chạy trong repo code

```bash
# Test locally with clean slate
docker network rm oms_default pmi_default wms_default gateway_network identity_default 2>/dev/null || true
./start_all.sh --no-watch
docker ps  # verify all services up

# Simulate stale network (CI scenario)
docker compose -f OMS/docker-compose.yml down -v
docker network create oms_default  # create without compose labels
./start_all.sh --no-watch  # should NOT fail now

# E2E test
cd /home/lupca/projects/topvnsport
pytest e2e_tests/tests/test_full_flow.py -v
```

## Câu hỏi rủi ro (từ code-review-graph, tĩnh)

- Files trong scope: `start_all.sh`, `OMS/docker-compose.yml`, `OMS/docker-compose.prod.yml`, `.github/workflows/e2e.yml`
- Không có application flows bị ảnh hưởng (chỉ là infra/CI config)
- Verify rằng fix chỉ thêm `default: {name: oms_default, external: true}` vào OMS compose files, không thay đổi logic khác

## Gợi ý công cụ

Repo code đích có sẵn skill `/code-review` — khuyến khích dùng để đọc diff + chạy test một cách có cấu trúc.

## Trả kết quả

Sau khi review xong, báo lại cho control-tower bằng lệnh:

```
/verdict WMS-003 <pass|changes> --reviewer @<tên bạn> [--commit <hash>] [--notes "..."]
```
