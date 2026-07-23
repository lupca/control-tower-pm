---
id: MVA-007
title: "Xác nhận pipeline hiện tại hoạt động (smoke test)"
status: done
review_rounds: 1
done: 2026-07-23
priority: high
risk: normal
deadline: null
executor: "@antigravity-3.6-high"
reviewer: "@gpt-5.6-sol"
result_ref: "smoke-test-verified"
depends_on: []
files:
  - run.py
  - agent.py
  - engines/tts.py
  - engines/text2video.py
  - engines/download.py
  - engines/unbox/make_viral.py
  - tools/tts_tool.py
  - tools/video_tool.py
  - tools/edit_tool.py
  - tools/download_tool.py
  - config.py
  - database.py
flows: [run_agent_session]
tests:
  - tests/test_simplified.py
dispatched: 2026-07-23
in_review: 2026-07-23
predicted_success: medium
prediction_factors:
  score: 0.5
  deductions:
    - "cần ComfyUI/LLM server chạy local (-0.3)"
    - "MoviePy v2 xung đột có thể gây lỗi (-0.1)"
    - "known bugs chưa fix (-0.1)"
confidence_interval: [0.3, 0.7]
created: 2026-07-23
updated: 2026-07-23
plan_approved: true
---

# MVA-007: Xác nhận pipeline hiện tại hoạt động (smoke test)

> Dự án: [[projects/marketing-video-agent/marketing-video-agent]]

## Mục đích

Smoke test xác nhận trạng thái thực tế của pipeline trước khi bắt tay vào MVA-002→006. Không cần fix gì — chỉ ghi nhận cái gì chạy, cái gì không.

## Tiêu chí nghiệm thu (AC)

- [x] **AC1:** Chạy `pytest tests/` — ghi nhận pass/fail (OK - 2 passed in 0.01s)
- [x] **AC2:** Chạy `python -c "from engines.tts import generate_speech"` — xác nhận import OK (OK)
- [x] **AC3:** Chạy `python -c "from engines.text2video import generate_video"` — xác nhận import OK (OK)
- [x] **AC4:** Chạy `python -c "from engines.unbox.make_viral import make_viral_video"` — xác nhận import OK (OK)
- [x] **AC5:** Chạy `python -c "from engines.download import download_media"` — xác nhận import OK (OK)
- [x] **AC6:** Thử gen TTS: `python -c "import asyncio; from engines.tts import generate_speech; asyncio.run(generate_speech('Xin chào', output_path='test_tts.mp3'))"` — ghi nhận kết quả (FAIL lệnh async vì `generate_speech` là sync function; OK khi gọi sync direct)
- [x] **AC7:** Chạy `python run.py "test brief"` — ghi nhận output hoặc error (FAIL - Connection Error tới Ollama/LLM local server tại port 11434)
- [x] **AC8:** Kiểm tra `jobs.db` có ghi record không (OK - Bảng `jobs` ghi nhận job mới với status `failed` & lý do lỗi)
- [x] **AC9:** Tổng hợp báo cáo: mỗi engine/tool → trạng thái (OK/FAIL/SKIP) + lý do (OK)

## Plan

Chỉ chạy và ghi nhận. Không sửa code. Output là báo cáo trạng thái.
