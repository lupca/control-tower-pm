---
id: MVA-001
task_path: projects/marketing-video-agent/tasks/MVA-001.md
project: marketing-video-agent
result_ref: e337a5e79a4f
executor: @gpt-5.6-luna-high
reviewer: null
status: pending
issued: 2026-07-22
verdict: null
verdict_date: null
---

# Phiếu Review: MVA-001 — Đơn giản hóa kiến trúc: từ 17 workers + Celery xuống 1 VideoAgent

- Dự án: marketing-video-agent (`/data/projects/marketing-video-agent`)
- Task gốc: `projects/marketing-video-agent/tasks/MVA-001-simplify-architecture.md`
- Result-ref: `e337a5e79a4f` (Rework: nullable fixes + legacy test cleanup)
- Executor: @gpt-5.6-luna-high
- Ngày phát phiếu: 2026-07-22 (updated)

## Acceptance Criteria cần verify

- [ ] **AC1:** Cấu trúc mới hoạt động: `python run.py "brief text"` → video output trong `output/`
- [ ] **AC2:** Engines hoạt động độc lập: `from engines.tts import generate_speech` không cần DB/Celery/MinIO
- [ ] **AC3:** SQLite job tracking: `jobs.db` lưu history với status/result_path/error
- [ ] **AC4:** smolagents Tools wrap engines: TTSTool, VideoTool, EditTool, DownloadTool
- [ ] **AC5:** Xóa sạch legacy: admin-api/, docker-compose*.yml, celery_worker.py files, shared_core/worker_base.py
- [ ] **AC6:** requirements.txt minimal: không còn celery, redis, psycopg2, minio
- [ ] **AC7:** Tests adapted: test_flow.py hoặc test mới chạy được với kiến trúc mới

## Definition of Done (AGENTS.md mục 3)

- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%:
  - `test_e2e_tmcp_agent.py`
  - `test_flow.py`
  - `tests/test_translify_graph.py`
  - `tests/test_simplified.py` (mới, nếu có)
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (bạn đang review, hãy xác nhận bạn ≠ @gpt-5.6-luna-high)

## Test gợi ý chạy trong repo code

```bash
cd /data/projects/marketing-video-agent

# Activate venv
source .venv-light/bin/activate

# Test simplified architecture
python -c "from engines.tts import generate_speech; print('TTS engine OK')"
python -c "from database import JobDB; db = JobDB(); print('SQLite OK')"

# Run CLI test
python run.py "Test brief for video creation"

# Check requirements.txt không còn legacy deps
grep -E "celery|redis|psycopg2|minio" requirements.txt && echo "FAIL: legacy deps still present" || echo "OK: no legacy deps"

# Run available tests
pytest tests/test_simplified.py -v
```

## Câu hỏi rủi ro (từ code-review-graph, tĩnh)

### HIGH Priority (6 questions)

1. **Bridge node risk:** `run_test` (test_e2e_tmcp_agent.py) là connector giữa nhiều code regions — có còn hoạt động với kiến trúc mới không?

2. **Bridge node risk:** `test_job_db_tracks_success_and_failure` (tests/test_simplified.py) — test mới này có cover đúng JobDB functionality không?

3. **Hub node untested:** `make_unbox_viral` (114 connections) không có test coverage trực tiếp — refactor có ảnh hưởng không?

4. **Hub node untested:** `generate_image_and_upload` (93 connections) — có còn được sử dụng sau refactor không?

### MEDIUM Priority (5 questions)

5. **Surprising coupling:** `resolve_llm_config` calls `get_settings` cross-community — coupling này có còn sau khi simplified config.py?

6. **Untested hotspot:** `make_unbox_viral` có 114 connections nhưng không có test — risk cho refactor?

7. **Untested hotspot:** `generate_image_and_upload` có 93 connections nhưng không có test — đã được xóa hay refactor?

### LOW Priority (2 questions)

8. **Thin community:** `shared-core-database-config` chỉ có 2 members — đã được merge/xóa chưa?

9. **Thin community:** `shared-core-redis-config` chỉ có 2 members — đã được xóa (không còn Redis)?

## Lưu ý đặc biệt cho task này

- **Risk: HIGH** — Task này có blast radius 168 files, chạm nhiều hub nodes
- **Predicted success: LOW** (0.2) — cần review kỹ
- **Breaking change:** External systems calling admin-api sẽ không hoạt động — verify không còn external dependency

## Gợi ý công cụ

Repo code đích có thể có sẵn skill `/code-review` — khuyến khích dùng để đọc diff + chạy test một cách có cấu trúc.

## Trả kết quả

Sau khi review xong, báo lại cho control-tower bằng lệnh:

```
/verdict MVA-001 pass --reviewer @<tên bạn> --commit cfdd8f68aea0
```

hoặc nếu cần sửa:

```
/verdict MVA-001 changes --reviewer @<tên bạn> --notes "..."
```
