---
id: MVA-009
title: "Fix 3 blocking issues từ review MVA-008"
status: done
review_rounds: 1
done: 2026-07-23
priority: high
risk: normal
deadline: null
executor: "@antigravity-3.6-high"
reviewer: "@antigravity"
result_ref: 6e2b16fec5721d5efef56a0dc9df431f49c35c51
depends_on: [MVA-008]
files:
  - engines/tts.py
  - engines/download.py
  - engines/unbox/text_overlay.py
  - engines/unbox/video_unbox.py
  - tests/test_simplified.py
flows: []
tests:
  - tests/test_simplified.py
dispatched: 2026-07-23
in_review: 2026-07-23
predicted_success: high
prediction_factors:
  score: 0.7
  deductions:
    - "MoviePy v2 migration cần cẩn thận với .resized/.rotated/.with_* (-0.15)"
    - "TTS timeout cần async handling (-0.1)"
    - "venv có MoviePy 1.0.3 nhưng requirements yêu cầu >=2.0 — cần pip install (-0.05)"
confidence_interval: [0.55, 0.85]
created: 2026-07-23
updated: 2026-07-23
plan_approved: true
---

# MVA-009: Fix 3 blocking issues từ review MVA-008

> Dự án: [[projects/marketing-video-agent/marketing-video-agent]]

## Bối cảnh

Review MVA-008 bởi @gpt-5.6-sol phát hiện 3 issues blocking:
1. MoviePy v2 migration chưa hoàn tất (text_overlay.py, video_unbox.py)
2. Download engine thiếu yt-dlp fallback path
3. TTS treo pytest (không timeout)

## Tiêu chí nghiệm thu (AC)

- [x] **AC1:** MoviePy v2 hoàn tất trong `engines/unbox/text_overlay.py`:
  - Xóa `moviepy.editor` import/fallback
  - `.set_start()` → `.with_start()`, `.set_duration()` → `.with_duration()`
  - `.resize()` → `.resized()`, `.rotate()` → `.rotated()`
  - Xóa `verbose=False` trong `write_videofile()`
- [x] **AC2:** MoviePy v2 hoàn tất trong `engines/unbox/video_unbox.py`:
  - Tương tự AC1
- [x] **AC3:** `engines/download.py` tìm yt-dlp đúng cách: dùng `shutil.which("yt-dlp")` trước, fallback tới `.venv-light/bin/yt-dlp` hoặc `.venv-heavy/bin/yt-dlp` nếu không tìm thấy trên PATH
- [x] **AC4:** `engines/tts.py` có bounded timeout (30s) cho edge-tts call. Nếu timeout → raise exception rõ ràng thay vì treo
- [x] **AC5:** Test TTS trong `tests/test_simplified.py` dùng `pytest.mark.skipif` hoặc timeout fixture, không bắt AssertionError
- [x] **AC6:** Upgrade MoviePy trong venv: `pip install moviepy>=2.0` (nếu venv hiện có 1.0.3)
- [x] **AC7:** `pytest tests/` pass hoàn tất (không timeout, không treo)

## Lưu ý

- BỎ QUA Ollama/ComfyUI — như MVA-008
- MoviePy migration guide: https://zulko.github.io/moviepy/getting_started/updating_to_v2.html
- Commit changes khi xong
- Cập nhật task file: tick AC, set status=in_review, set result_ref=commit hash
