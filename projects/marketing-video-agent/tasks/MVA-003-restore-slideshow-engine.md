---
id: MVA-003
title: "Khôi phục engine slideshow (video từ ảnh sản phẩm)"
status: todo
priority: high
risk: high
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: [MVA-002]
files:
  - engines/slideshow/
  - tools/slideshow_tool.py
  - requirements.txt
flows: []
tests: []
dispatched: null
in_review: null
predicted_success: medium
prediction_factors:
  score: 0.5
  deductions:
    - "scope lớn: toàn bộ slideshow_engine (audio_sync, hook_outro, visuals, pipeline) (-0.3)"
    - "phụ thuộc MVA-002 (cần gen ảnh) (-0.1)"
    - "chưa có test (-0.1)"
confidence_interval: [0.3, 0.6]
created: 2026-07-23
updated: 2026-07-23
plan_approved: false
---

# MVA-003: Khôi phục engine slideshow (video từ ảnh sản phẩm)

> Dự án: [[projects/marketing-video-agent/marketing-video-agent]]

## Bối cảnh

`worker_slideshow` bị xóa hoàn toàn sau refactor. Đây là định dạng video marketing phổ biến nhất trên TikTok/Reels cho e-commerce: ảnh sản phẩm + nhạc beat-sync + intro hook + outro CTA.

Source: nghiên cứu @gpt-5.6-sol + @antigravity (2026-07-23).

## Tiêu chí nghiệm thu (AC)

- [ ] **AC1:** `engines/slideshow/` chứa pipeline hoàn chỉnh: audio_sync, visuals, hook_outro
- [ ] **AC2:** Beat-sync: thời lượng slide tự động khớp phách nhạc nền
- [ ] **AC3:** Visual effects: Ken Burns (zoom/pan), transition (whip/flash)
- [ ] **AC4:** Intro hook (banner + TTS) và Outro CTA hoạt động
- [ ] **AC5:** `tools/slideshow_tool.py` — SlideshowTool wrap engine, nhận list ảnh + audio + text
- [ ] **AC6:** Output video 9:16 chuẩn TikTok/Reels
- [ ] **AC7:** Test: `pytest tests/test_slideshow.py` pass

## Plan

1. `git show 77bc43b^:worker_slideshow/slideshow_engine/` — lấy code cũ
2. Port 4 module: `audio_sync.py`, `visuals.py`, `hook_outro.py`, `pipeline.py` → `engines/slideshow/`
3. Xóa DB/MinIO/Celery, giữ core rendering
4. Tạo `tools/slideshow_tool.py` — SlideshowTool
5. Tạo `tests/test_slideshow.py`
6. Đăng ký tool trong `agent.py`

## Effort ước tính: 4-6 giờ
