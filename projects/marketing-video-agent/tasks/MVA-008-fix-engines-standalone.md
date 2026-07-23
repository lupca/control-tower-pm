---
id: MVA-008
title: "Fix engines hoạt động độc lập (bỏ qua Ollama)"
status: done
review_rounds: 2
done: 2026-07-23
priority: high
risk: normal
deadline: null
executor: "@antigravity-3.6-high"
reviewer: "@gpt-5.6-sol"
result_ref: "b9d41913e7dcadaae7c5fd5b9dd73a817ce0f7cb"
depends_on: [MVA-007]
files:
  - engines/tts.py
  - engines/text2video.py
  - engines/download.py
  - engines/unbox/make_viral.py
  - tools/tts_tool.py
  - tools/video_tool.py
  - tools/edit_tool.py
  - tools/download_tool.py
  - storage.py
  - requirements.txt
  - CLAUDE.md
  - tests/test_simplified.py
flows: []
tests:
  - tests/test_simplified.py
dispatched: 2026-07-23
in_review: "2026-07-23T15:37:00+07:00"
predicted_success: medium
prediction_factors:
  score: 0.6
  deductions:
    - "MoviePy v2 migration phức tạp (-0.2)"
    - "nhiều fix phân tán (-0.1)"
    - "TTS có thể timeout do network (-0.1)"
confidence_interval: [0.4, 0.75]
created: 2026-07-23
updated: 2026-07-23
plan_approved: true
---

# MVA-008: Fix engines hoạt động độc lập (bỏ qua Ollama)

> Dự án: [[projects/marketing-video-agent/marketing-video-agent]]

## Bối cảnh

Smoke test MVA-007 + review sol cho thấy: imports OK nhưng runtime chưa ổn. TTS timeout/0-byte, tools thiếu params, MoviePy v2 xung đột, code thừa. Mục tiêu: mỗi engine chạy được standalone — bỏ qua Ollama/LLM agent orchestration.

## Tiêu chí nghiệm thu (AC)

- [x] **AC1:** TTS gen file thực tế: `generate_speech('Xin chào', output_path='test.mp3')` → file > 0 bytes. Nếu edge-tts timeout do network → ghi SKIP kèm lý do, không block.
- [x] **AC2:** VideoTool output unique path — không ghi đè `output/generated.mp4` (dùng uuid hoặc timestamp)
- [x] **AC3:** EditTool nhận `text_events` param — xóa hardcode "VỢT CẦU LÔNG SIÊU ĐỈNH"
- [x] **AC4:** TTSTool expose `speed` và `provider` params
- [x] **AC5:** MoviePy v2 compatible: xóa `moviepy.editor` import, `.set_*()` → `.with_*()`
- [x] **AC6:** Xóa `storage.py` (orphan, không ai import)
- [x] **AC7:** Dọn `requirements.txt`: xóa deps không dùng (`ffmpeg-python`, `pydantic`, `websocket-client` — verify trước khi xóa)
- [x] **AC8:** Cập nhật `CLAUDE.md` phản ánh kiến trúc mới (standalone agent, engines/, tools/)
- [x] **AC9:** `pytest tests/` vẫn pass sau tất cả changes
- [x] **AC10:** Tạo bảng trạng thái runtime test từng engine (import + chạy thực nếu có thể, SKIP nếu cần external service)

## Lưu ý quan trọng

- **BỎ QUA Ollama/LLM**: run.py, agent.py không cần fix — fail do Ollama không có là chấp nhận được
- **BỎ QUA ComfyUI**: text2video engine sẽ fail runtime nếu ComfyUI không chạy — chấp nhận, chỉ fix code bugs
- Focus: code quality + engines chạy standalone khi gọi trực tiếp

## Plan

1. Fix `engines/tts.py`: kiểm tra generate_speech sync, thêm timeout handling
2. Fix `tools/video_tool.py`: unique output path
3. Fix `tools/edit_tool.py`: thêm text_events param, truyền xuống make_viral_video
4. Fix `tools/tts_tool.py`: thêm speed, provider inputs
5. Fix MoviePy v2 trong `engines/unbox/`: moviepy.editor → moviepy, .set_*→.with_*
6. Xóa `storage.py`
7. Audit + dọn `requirements.txt`
8. Rewrite `CLAUDE.md`
9. Chạy tests
10. Tạo bảng trạng thái runtime

---

### Bảng trạng thái Runtime Test từng Engine (AC10)

| Engine / Component | Module Path | Status | Chi tiết / Lý do |
|---|---|---|---|
| **TTS Engine** | [engines/tts.py](file:///data/projects/marketing-video-agent/engines/tts.py) | **PASS** | `generate_speech('Xin chào')` tạo file `temp/test_ac1.mp3` có kích thước 10,656 bytes (> 0) |
| **Video Engine** | [engines/text2video.py](file:///data/projects/marketing-video-agent/engines/text2video.py) | **SKIP** | Code bugs đã fix & unique output path đã bổ sung. Skip runtime do server ComfyUI chưa khởi chạy ở `localhost:8188` |
| **Download Engine** | [engines/download.py](file:///data/projects/marketing-video-agent/engines/download.py) | **SKIP** | Bổ sung fallback path cho `yt-dlp` binary (`.venv-light/bin/yt-dlp`). Skip download thực tế do cần URL live media |
| **Unbox Viral Engine** | [engines/unbox/make_viral.py](file:///data/projects/marketing-video-agent/engines/unbox/make_viral.py) | **PASS** | Tương thích MoviePy v2, loại bỏ hardcode "VỢT CẦU LÔNG SIÊU ĐỈNH", preview mode (`preview=True`) trả về `status="preview_ready"` thành công |
