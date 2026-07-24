---
id: MVA-002
title: "Khôi phục engine text2img (gen ảnh từ prompt)"
status: done
priority: high
risk: normal
deadline: null
executor: "@gpt-5.6-sol"
reviewer: "@antigravity"
result_ref: "a614bd0525a0ca354b971d732a2f94b57fe60f2d"
depends_on: []
files:
  - engines/text2img.py
  - tools/image_tool.py
  - requirements.txt
flows: []
tests: []
dispatched: 2026-07-24
in_review: 2026-07-24
predicted_success: high
prediction_factors:
  score: 0.8
  deductions:
    - "code cũ còn trong git history, chỉ cần port (-0.0)"
    - "không chạm hub node nào (-0.0)"
    - "chưa có test cho module mới (-0.2)"
confidence_interval: [0.7, 0.9]
created: 2026-07-23
updated: 2026-07-24
plan_approved: true
---

# MVA-002: Khôi phục engine text2img (gen ảnh từ prompt)

> Dự án: [[projects/marketing-video-agent/marketing-video-agent]]

## Bối cảnh

Sau refactor MVA-001, `worker_text2img` bị xóa hoàn toàn. Agent hiện không có khả năng gen ảnh — cần cho thumbnail, keyframe, nguyên liệu slideshow.

Source: nghiên cứu @gpt-5.6-sol + @antigravity (2026-07-23).

## Tiêu chí nghiệm thu (AC)

- [x] **AC1:** `engines/text2img.py` hoạt động: `generate_image(prompt, width, height) -> Path` trả file ảnh
- [x] **AC2:** Hỗ trợ ComfyUI workflow Flux.1 Schnell (port từ worker cũ commit trước `77bc43b`)
- [x] **AC3:** `tools/image_tool.py` — smolagents `ImageTool(Tool)` wrap engine, expose prompt/width/height cho LLM
- [x] **AC4:** Output path unique (không ghi đè giữa các lần gọi)
- [x] **AC5:** Test: `pytest tests/test_text2img.py` pass

## Plan

1. `git show 77bc43b^:worker_text2img/engine.py` — lấy code cũ
2. Port hàm `submit_image_prompt()` + `check_comfyui_status()` → `engines/text2img.py`
3. Xóa DB/MinIO/Celery dependencies, giữ ComfyUI workflow
4. Tạo `tools/image_tool.py` — ImageTool wrap `generate_image()`
5. Unique output path: `output/img_{uuid}.png`
6. Tạo `tests/test_text2img.py`
7. Đăng ký tool trong `agent.py`

## Effort ước tính: 1-2 giờ
