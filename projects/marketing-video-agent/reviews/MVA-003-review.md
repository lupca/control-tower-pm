---
id: MVA-003
task_path: projects/marketing-video-agent/tasks/MVA-003-restore-slideshow-engine.md
project: marketing-video-agent
result_ref: "4700920a4a8fb429499ee7f338b30be7b32bab1c"
executor: "@gpt-5.6-sol"
reviewer: "@antigravity"
status: completed
issued: 2026-07-24
verdict: pass
verdict_date: 2026-07-24
---

# Phiếu Review: MVA-003 — Khôi phục engine slideshow (video từ ảnh sản phẩm)

- Dự án: marketing-video-agent (`/data/projects/marketing-video-agent`)
- Task gốc: `projects/marketing-video-agent/tasks/MVA-003-restore-slideshow-engine.md`
- Result-ref: `4700920a4a8fb429499ee7f338b30be7b32bab1c`
- Executor: @gpt-5.6-sol
- Reviewer: @antigravity
- Ngày phát phiếu: 2026-07-24

## Acceptance Criteria cần verify

- [x] **AC1:** `engines/slideshow/` chứa pipeline hoàn chỉnh: audio_sync, visuals, hook_outro
- [x] **AC2:** Beat-sync: thời lượng slide tự động khớp phách nhạc nền
- [x] **AC3:** Visual effects: Ken Burns (zoom/pan), transition (whip/flash)
- [x] **AC4:** Intro hook (banner + TTS) và Outro CTA hoạt động
- [x] **AC5:** `tools/slideshow_tool.py` — SlideshowTool wrap engine, nhận list ảnh + audio + text
- [x] **AC6:** Output video 9:16 chuẩn TikTok/Reels
- [x] **AC7:** Test: `pytest tests/test_slideshow.py` pass

## Definition of Done (AGENTS.md mục 3)

- [x] Toàn bộ AC pass
- [x] Test liên quan xanh 100%: `tests/test_slideshow.py`
- [x] Không regression (test khác trong module vẫn xanh — `pytest tests/`)
- [x] Reviewer khác executor (@antigravity ≠ @gpt-5.6-sol)

## Test gợi ý chạy trong repo code

```bash
# Full test suite
.venv-light/bin/pytest tests/ -v

# Slideshow tests only
.venv-light/bin/pytest tests/test_slideshow.py -v

# Smoke render (nếu có ảnh test + audio)
.venv-light/bin/python -c "
from engines.slideshow import render_slideshow
# Cần chuẩn bị: ít nhất 2 ảnh + 1 file audio
"

# Check output resolution 9:16
# ffprobe output file → verify 1080x1920
```

## Câu hỏi rủi ro (từ code-review-graph, tĩnh)

1. **[HIGH] Hub node untested:** `render_slideshow` (pipeline.py) có 80 connections nhưng không có direct test coverage. Tests có cover đủ pipeline chính không?
2. **[HIGH] Bridge node mới:** `compute_beat_synced_durations` (audio_sync.py) là critical connector — verify logic beat-sync có unit test riêng không?
3. **[LOW] Thin community:** `slideshow-motion` chỉ 2 members — có nên merge với community khác không?
4. **MoviePy v2 compatibility:** Code mới phải dùng `.with_start()/.with_duration()/.with_position()` — KHÔNG dùng legacy `.set_*()` (xem CLAUDE.md project guidelines).
5. **Unique output paths:** File generators phải trả unique output path (uuid/timestamp) — kiểm tra `SlideshowTool.forward()` có hardcode `output/slideshow.mp4` không.

## Gợi ý công cụ

Repo code đích có sẵn skill `/code-review` — khuyến khích dùng để đọc diff + chạy test một cách có cấu trúc.

## Trả kết quả

Sau khi review xong, báo lại cho control-tower bằng lệnh:
```
/verdict MVA-003 <pass|changes> --reviewer @antigravity [--commit <hash>] [--notes "..."]
```
