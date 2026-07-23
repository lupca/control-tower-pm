---
id: MVA-004
title: "Fix bugs + ổn định engines hiện tại"
status: todo
priority: high
risk: normal
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: []
files:
  - engines/text2video.py
  - engines/tts.py
  - engines/unbox/make_viral.py
  - tools/video_tool.py
  - tools/tts_tool.py
  - tools/edit_tool.py
  - storage.py
  - CLAUDE.md
  - requirements.txt
flows: []
tests:
  - tests/test_simplified.py
dispatched: null
in_review: null
predicted_success: high
prediction_factors:
  score: 0.75
  deductions:
    - "nhiều fix nhỏ phân tán (-0.15)"
    - "MoviePy v2 migration cần cẩn thận (-0.1)"
confidence_interval: [0.6, 0.85]
created: 2026-07-23
updated: 2026-07-23
plan_approved: false
---

# MVA-004: Fix bugs + ổn định engines hiện tại

> Dự án: [[projects/marketing-video-agent/marketing-video-agent]]

## Bối cảnh

Nghiên cứu từ @gpt-5.6-sol phát hiện nhiều bugs trong engines hiện tại mà @antigravity không thấy. Cần fix trước khi thêm capability mới.

## Tiêu chí nghiệm thu (AC)

- [ ] **AC1:** VideoTool output unique path (không ghi đè `output/generated.mp4` giữa các scene)
- [ ] **AC2:** EditTool nhận `text_events` param — không hardcode "VỢT CẦU LÔNG SIÊU ĐỈNH"
- [ ] **AC3:** MoviePy v2 compatible: `.set_start()` → `.with_start()`, xóa `moviepy.editor` import
- [ ] **AC4:** TTSTool expose `speed` và `provider` params cho LLM chọn MeloTTS
- [ ] **AC5:** Xóa `storage.py` orphan (không ai import)
- [ ] **AC6:** Cập nhật `CLAUDE.md` phản ánh kiến trúc mới (xóa mô tả Celery/workers/admin-api)
- [ ] **AC7:** Dọn dependencies thừa trong `requirements.txt`: `ffmpeg-python`, `pydantic`, `websocket-client` (nếu không dùng)
- [ ] **AC8:** Tests pass sau tất cả changes

## Plan

1. `tools/video_tool.py`: output → `output/video_{uuid}.mp4`
2. `tools/edit_tool.py`: thêm `text_events` input, truyền xuống `make_viral_video()`
3. `engines/unbox/`: migrate MoviePy v1 API → v2
4. `tools/tts_tool.py`: thêm `speed`, `provider` inputs
5. Xóa `storage.py`
6. Rewrite `CLAUDE.md` cho kiến trúc standalone agent
7. Audit + dọn `requirements.txt`
8. Chạy tests

## Effort ước tính: 3-4 giờ
