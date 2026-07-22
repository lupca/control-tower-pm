---
id: MVA-001
title: "Đơn giản hóa kiến trúc: từ 17 workers + Celery xuống 1 VideoAgent"
status: dispatched
priority: high
risk: high
deadline: null
executor: "@gpt-5.6-luna"
reviewer: null
result_ref: null
depends_on: []
files:
  - worker_agent/agent_runner.py
  - worker_tts/engine.py
  - worker_text2video/engine.py
  - worker_unbox/make_viral.py
  - worker_unbox/unbox_viral.py
  - worker_unbox/unbox_engine/
  - worker_download/celery_worker.py
  - shared_core/config.py
  - shared_core/worker_base.py
  - shared_core/minio_utils.py
  - admin-api/
  - docker-compose.yml
  - dev.sh
flows: [run_agent_session, _build_review_video, main]
tests:
  - test_e2e_tmcp_agent.py
  - test_flow.py
  - tests/test_translify_graph.py
dispatched: 2026-07-22
in_review: null
predicted_success: low
prediction_factors:
  score: 0.2
  deductions:
    - "blast_radius: 168 files (-0.5)"
    - "hub_bridge: true — hits make_unbox_viral (115°), insert_log (78°), execute_video_task (59°) (-0.2)"
    - "no_tests: false — existing e2e tests need adaptation (-0.1)"
confidence_interval: [0.1, 0.4]
created: 2026-07-22
updated: 2026-07-22
plan_approved: true
---

# MVA-001: Đơn giản hóa kiến trúc: từ 17 workers + Celery xuống 1 VideoAgent

> Dự án: [[projects/marketing-video-agent/marketing-video-agent]]

## Tiêu chí nghiệm thu (AC)

- [ ] **AC1:** Cấu trúc mới hoạt động: `python run.py "brief text"` → video output trong `output/`
- [ ] **AC2:** Engines hoạt động độc lập: `from engines.tts import generate_speech` không cần DB/Celery/MinIO
- [ ] **AC3:** SQLite job tracking: `jobs.db` lưu history với status/result_path/error
- [ ] **AC4:** smolagents Tools wrap engines: TTSTool, VideoTool, EditTool, DownloadTool
- [ ] **AC5:** Xóa sạch legacy: admin-api/, docker-compose*.yml, celery_worker.py files, shared_core/worker_base.py
- [ ] **AC6:** requirements.txt minimal: không còn celery, redis, psycopg2, minio
- [ ] **AC7:** Tests adapted: test_flow.py hoặc test mới chạy được với kiến trúc mới

## Verifier Results

```
✅ no-circular-deps: passed
✅ files-exist: passed (paths confirmed via graph)
❌ reasonable-scope: 168 files — REQUIRES SPLIT (see Sub-tasks below)
✅ tests-for-changes: existing tests + adaptation sub-task
✅ no-conflicting-tasks: no overlapping tasks
```

## Verifier Overrides

User cần xác nhận chấp nhận scope lớn VÀ phương án split thành phases dưới đây.

## Plan

### Phase 1: Tạo structure mới + core modules (estimated: 30 min)

**Files tạo mới:**
1. `config.py` — Simplified dataclass config (chỉ giữ LLM, ComfyUI, storage paths, TTS provider)
   - Copy từ `shared_core/config.py`, xóa DatabaseConfig, RedisConfig, MinIOConfig
   - Thêm `db_path: str` cho SQLite
2. `database.py` — SQLite JobDB class
   - Schema: `jobs(id, brief, status, result_path, error, created_at, completed_at)`
   - Methods: `create_job()`, `complete_job()`, `fail_job()`
3. `storage.py` — LocalStorage adapter (optional, có thể inline trong engines)
   - `ensure_dir()`, `get_output_path()`, `cleanup_temp()`
4. Tạo folders: `mkdir -p engines tools`

### Phase 2: Extract engines (estimated: 1.5 hours)

**2.1. TTS Engine** (`engines/tts.py`)
- Copy `worker_tts/engine.py::_edge_tts_async()` và `generate_melotts_audio()`
- Wrap thành `generate_speech(text, voice, speed, output_path) -> Path`
- XÓA: DB lookup (`_get_tts_model_config_from_db`), MinIO upload (`upload_file_to_minio`)

**2.2. Text2Video Engine** (`engines/text2video.py`)
- Copy `worker_text2video/engine.py::submit_video_prompt()`, `check_video_status()`, `submit_ltx_video_prompt()`
- Wrap thành `generate_video(prompt, width, height, comfyui_url, output_path) -> Path`
- XÓA: MinIO dependencies, DB logging

**2.3. Download Engine** (`engines/download.py`)
- Copy YouTube download logic từ `worker_download/celery_worker.py`
- Wrap thành `download_media(url, output_path) -> Path`
- Sử dụng `yt-dlp` trực tiếp, không qua MinIO

**2.4. Unbox Engine** (`engines/unbox/`)
- `mkdir -p engines/unbox`
- Copy nguyên `worker_unbox/unbox_engine/*.py` (video_viral.py, video_unbox.py, text_overlay.py, audio.py, transitions.py, types.py)
- Copy `worker_unbox/make_viral.py` → `engines/unbox/make_viral.py`
- Refactor imports: `from worker_unbox.unbox_engine.X` → `from .X`
- XÓA: `shared_core.minio_utils`, `shared_core.database` imports
- GIỮA: `shared_core.audio_utils` (nếu còn dùng) hoặc inline

### Phase 3: Create agent + CLI (estimated: 1 hour)

**3.1. smolagents Tools** (`tools/`)
- `tools/__init__.py` — export all tools
- `tools/tts_tool.py` — `TTSTool(Tool)` wrapping `engines.tts.generate_speech`
- `tools/video_tool.py` — `VideoTool(Tool)` wrapping `engines.text2video.generate_video`
- `tools/edit_tool.py` — `EditTool(Tool)` wrapping `engines.unbox.make_viral`
- `tools/download_tool.py` — `DownloadTool(Tool)` wrapping `engines.download.download_media`

**3.2. VideoAgent** (`agent.py`)
- Copy core logic từ `worker_agent/agent_runner.py::create_agent()`
- Sử dụng `smolagents.CodeAgent` + `OpenAIServerModel`
- Load instructions từ `prompts/agent_instructions.txt` (giữ nguyên)
- `run(brief) -> Path` — tạo job trong SQLite, chạy agent, return result path

**3.3. CLI Entry** (`run.py`)
- argparse: `python run.py "brief"` hoặc `python run.py -f brief.txt`
- Optional: `--output` directory override
- Print result path khi xong

**3.4. Adapt tests**
- Tạo `tests/test_simplified.py` hoặc adapt `test_flow.py`
- Test: `from engines.tts import generate_speech` → verify file created
- Test: `from agent import VideoAgent; agent.run("test brief")` → verify job in SQLite

### Phase 4: Cleanup legacy (estimated: 30 min)

**Xóa files/folders:**
```bash
rm -rf admin-api/
rm docker-compose*.yml Dockerfile .dockerignore
rm dev.sh dev-stop.sh dev-docker-pipeline.sh dev-selective.sh restart_workers.sh
rm shared_core/worker_base.py
rm */celery_worker.py  # trong tất cả worker_* folders
rm init_worker_configs.py video_creator_dump.sql test_video_creator.db
```

**Update requirements.txt:**
```
# REMOVE:
celery
redis
psycopg2-binary
minio
fastapi
uvicorn

# KEEP:
smolagents>=1.24.0
pydantic>=2.0
edge-tts
moviepy>=2.0
opencv-python-headless
ffmpeg-python
librosa
soundfile
yt-dlp
requests
websocket-client
```

**Optional cleanup (later):**
- Xóa các worker_* folders sau khi verify engines hoạt động
- Giữ lại `prompts/` (đang dùng)

## Sub-tasks (Proposed Split)

Theo migration steps trong `PLAN_SIMPLIFY.md`, đề xuất chia thành 4 phases:

### Phase 1: Tạo structure mới + core modules
- [ ] Tạo folders: `engines/`, `tools/`
- [ ] Tạo `config.py` (simplified, dataclass-based)
- [ ] Tạo `database.py` (SQLite JobDB)
- [ ] Tạo `storage.py` (LocalStorage adapter)

### Phase 2: Extract engines (pure functions, no deps)
- [ ] Extract `worker_tts/engine.py` → `engines/tts.py`
- [ ] Extract `worker_text2video/engine.py` → `engines/text2video.py`
- [ ] Extract `worker_download/` → `engines/download.py`
- [ ] Move `worker_unbox/unbox_engine/` + `make_viral.py` → `engines/unbox/`

### Phase 3: Create agent + CLI
- [ ] Create smolagents Tools (`tools/tts_tool.py`, `tools/video_tool.py`, etc.)
- [ ] Create `agent.py` (VideoAgent class using smolagents CodeAgent)
- [ ] Create `run.py` CLI entry point
- [ ] Adapt tests for new architecture

### Phase 4: Cleanup legacy
- [ ] Delete `admin-api/`
- [ ] Delete `docker-compose*.yml`, `Dockerfile`, `.dockerignore`
- [ ] Delete `dev.sh`, `dev-stop.sh`, `restart_workers.sh`
- [ ] Delete all `celery_worker.py` files
- [ ] Delete `shared_core/worker_base.py`
- [ ] Update `requirements.txt` (remove celery, redis, psycopg2, minio)

## Risk Notes

- **⚠️ HIGH RISK:** Touches multiple hub nodes:
  - `make_unbox_viral` (115 connections) — KEEP, refactor
  - `insert_log` (78 connections) — DELETE
  - `execute_video_task` (59 connections) — DELETE
- **20 untested hotspots** identified by graph — nhiều sẽ bị xóa nhưng `make_viral`, `unbox_engine/*` cần test
- **Breaking change:** API incompatible — external systems calling admin-api sẽ cần migrate sang CLI/direct import

## References

- Plan chi tiết: `/data/projects/marketing-video-agent/PLAN_SIMPLIFY.md`
- Kiến trúc mới: Single VideoAgent (smolagents) → Engines (pure functions) → Local storage
