---
id: MVA-001
title: "Đơn giản hóa kiến trúc: từ 17 workers + Celery xuống 1 VideoAgent"
status: done
priority: high
risk: high
deadline: null
executor: "@gpt-5.6-luna-high"
reviewer: "@gpt-5.6-sol"
result_ref: "marketing-video-agent@main (commit 46a19e1a)"
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
in_review: 2026-07-22
done: 2026-07-22
predicted_success: low
prediction_factors:
  score: 0.2
  deductions:
    - "blast_radius: 168 files (-0.5)"
    - "hub_bridge: true — hits make_unbox_viral (115°), insert_log (78°), execute_video_task (59°) (-0.2)"
    - "no_tests: false — existing e2e tests need adaptation (-0.1)"
confidence_interval: [0.1, 0.4]
created: 2026-07-22
updated: 2026-07-23
review_rounds: 4
plan_approved: true
causal_analysis:
  root_cause: "Legacy code patterns không tương thích với smolagents API mới"
  mechanism: "nullable schema validation, edge_tts rate format"
  counterfactual: "Nếu có integration tests từ đầu thì phát hiện sớm hơn"
  pattern_id: null
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

## Findings từ reviewer (Lần 1)

**Status: CHANGES REQUESTED** — Phase 4 (Cleanup) chưa hoàn thành.

### Đã làm đúng (Phase 1-3):
- [x] `engines/` với 4 files + `unbox/` subdirectory
- [x] `tools/` với 4 files
- [x] Root files: `agent.py`, `config.py`, `storage.py`, `database.py`, `run.py`
- [x] `tests/test_simplified.py` mới

### Chưa làm (Phase 4 - Cleanup):

**17 worker folders cần xóa:**
```bash
rm -rf worker_agent/ worker_base/ worker_capcut/ worker_chat/ \
       worker_delivery/ worker_download/ worker_leader/ worker_promotion/ \
       worker_research/ worker_review/ worker_slideshow/ worker_text2img/ \
       worker_text2video/ worker_translify/ worker_tts/ worker_unbox/
```

**Legacy scripts cần xóa:**
```bash
rm -f dev-stop.sh
```

**shared_core/ cần xử lý (12 files):**

| File | Action | Lý do |
|:---|:---|:---|
| `__init__.py` | XÓA | Không cần |
| `__pycache__/` | XÓA | Cache |
| `alter_db.py` | XÓA | PostgreSQL migration |
| `audio_utils.py` | GIỮ/MOVE | Nếu `engines/unbox/` còn dùng → move sang `engines/utils/` |
| `config.py` | XÓA | Đã thay bằng root `config.py` |
| `constants.py` | REVIEW | Nếu còn dùng → move sang root hoặc `engines/` |
| `database.py` | XÓA | PostgreSQL, đã thay bằng SQLite `database.py` |
| `gpu_utils.py` | GIỮ/MOVE | Nếu engines còn dùng → move sang `engines/utils/` |
| `llm_resolver.py` | REVIEW | Nếu `agent.py` còn dùng → move sang root |
| `minio_utils.py` | XÓA | MinIO không còn dùng |
| `models.py` | XÓA | SQLAlchemy models cho PostgreSQL |
| `schemas.py` | REVIEW | Pydantic schemas — nếu còn dùng → move |
| `video_schemas.py` | REVIEW | Nếu engines còn dùng → move |

### Action Plan cho Executor

```bash
cd /data/projects/marketing-video-agent

# 1. Xóa tất cả worker folders
rm -rf worker_agent/ worker_base/ worker_capcut/ worker_chat/ \
       worker_delivery/ worker_download/ worker_leader/ worker_promotion/ \
       worker_research/ worker_review/ worker_slideshow/ worker_text2img/ \
       worker_text2video/ worker_translify/ worker_tts/ worker_unbox/

# 2. Xóa legacy script
rm -f dev-stop.sh

# 3. Xử lý shared_core/ - XÓA những file chắc chắn không dùng
rm -rf shared_core/__pycache__/
rm -f shared_core/__init__.py
rm -f shared_core/alter_db.py
rm -f shared_core/config.py
rm -f shared_core/database.py
rm -f shared_core/minio_utils.py
rm -f shared_core/models.py

# 4. REVIEW các file còn lại trước khi xóa/move:
# - grep -r "audio_utils" engines/ → nếu dùng, move
# - grep -r "gpu_utils" engines/ → nếu dùng, move
# - grep -r "llm_resolver" . → nếu agent.py dùng, move
# - grep -r "schemas" engines/ → nếu dùng, move
# - grep -r "video_schemas" engines/ → nếu dùng, move
# - grep -r "constants" . → nếu dùng, move

# 5. Nếu không file nào còn dùng shared_core/:
rm -rf shared_core/

# 6. Verify không còn import shared_core trong code mới
grep -r "from shared_core" engines/ tools/ agent.py config.py database.py run.py
# Phải trả về empty

# 7. Test lại
python -c "from engines.tts import generate_speech; print('OK')"
python -c "from database import JobDB; print('OK')"
pytest tests/test_simplified.py -v
```

### Checklist trước khi báo lại

- [ ] Tất cả 17 worker_* folders đã xóa
- [ ] `dev-stop.sh` đã xóa
- [ ] `shared_core/` đã xử lý (xóa hoặc move files còn dùng)
- [ ] Không còn `from shared_core` import trong code mới
- [ ] Tests vẫn pass

## Findings từ reviewer (Lần 2)

**Status: CHANGES REQUESTED** — AC1/AC4/AC7 fail. Reviewer: @gpt-5.6-sol

### AC Status

| AC | Status | Issue |
|:---|:---|:---|
| AC1 | ❌ | CLI fails before generation — smolagents tool validation error |
| AC2 | ✅ | Standalone TTS import succeeds |
| AC3 | ✅ | SQLite tracks success/failure correctly |
| AC4 | ❌ | TTSTool/DownloadTool fail smolagents validation — optional args lack `nullable: true` |
| AC5 | ✅ | Legacy paths removed |
| AC6 | ✅ | No Celery/Redis/psycopg2/minio deps |
| AC7 | ❌ | Tests not fully adapted |

### Rework Tasks

- [ ] Fix `tools/tts_tool.py:13` — add `nullable: true` to optional arguments
- [ ] Fix `tools/download_tool.py:11` — add `nullable: true` to optional arguments
- [ ] Fix `tests/conftest.py:33` — remove import of deleted `shared_core`
- [ ] Remove/adapt legacy tests that import `worker_translify`, `shared_core`, PostgreSQL, admin API
- [x] Verify `run.py "brief"` produces video output after tool fixes

## Findings từ reviewer (Lần 3)

**Status: CHANGES REQUESTED** — AC2 fails. Reviewer: @gpt-5.6-sol (effort=high)

### Fixed from Lần 2
- [x] AC4: nullable fixes — all 4 smolagents tools instantiate successfully
- [x] AC7: legacy cleanup — no shared_core imports, pytest 2/2 pass
- [x] AC3, AC5, AC6: pass

### Blocking Issue
- [ ] **AC2 fails**: `engines/tts.py:10` passes `rate="default"` to edge_tts → `ValueError: Invalid rate 'default'`

### Notes
- AC1: CLI passes validation but no video output (local LLM/ComfyUI unavailable — environment issue, not code)

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
