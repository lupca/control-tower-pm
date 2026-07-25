---
id: MPT-001
title: "Generate video test chủ đề 'áo thể thao' (sports jersey) qua CLI, verify pipeline E2E"
status: dispatched
priority: medium
risk: high
deadline: null
executor: "@gpt-5.6-luna-high"
reviewer: null
result_ref: null
depends_on: []
files:
  - cli.py
flows: []
tests:
  - test/services/test_cli.py
dispatched: 2026-07-25
in_review: null
predicted_success: low
prediction_factors:
  score: 0.3
  deductions:
    - "blast_radius: 50 file bị ảnh hưởng (2-hop) từ cli.py, >15 (-0.5)"
    - "hits hub/bridge node: cli.py::parse_args (hub #3, bridge), cli.py::prepare_cli_files (hub, bridge) (-0.2)"
  note: "Task KHÔNG sửa code (chỉ chạy CLI để verify pipeline hoạt động) — công thức blast-radius/hub-node vốn tính cho task đổi code, ở đây phản ánh cli.py là entry-point trung tâm (đúng bản chất, không phải dấu hiệu rủi ro code). Rủi ro thực của task này nằm ở cấu hình API key/network/provider, không phải ở việc sửa code."
created: 2026-07-25
updated: 2026-07-25
---

# MPT-001: Generate video test chủ đề "áo thể thao" (sports jersey) qua CLI, verify pipeline E2E

> Dự án: [[projects/money-printer-turbo/money-printer-turbo]]

## Tiêu chí nghiệm thu (AC)
- [ ] Video MP4 hoàn chỉnh được sinh ra (`storage/tasks/<task-id>/final-1.mp4` hoặc tương đương), file tồn tại, kích thước > 0, phát được (kiểm tra bằng `ffprobe`).
- [ ] Nội dung script/video bám đúng chủ đề "áo thể thao" (sports jersey) — không lạc đề.
- [ ] Pipeline chạy trọn đủ stage (`script → terms → audio → subtitle → materials → video`) không lỗi, dùng **SiliconFlow** làm LLM script-gen và/hoặc TTS provider (theo `config.toml`).
- [ ] SiliconFlow API key **chỉ** được set trong `config.toml` (hoặc biến môi trường) trên máy chạy executor — KHÔNG xuất hiện trong log/output/report executor gửi lại, KHÔNG được paste vào bất kỳ file nào của control-tower.
- [ ] Executor báo cáo lại đường dẫn tuyệt đối file video thật + log chạy thực tế (không phải khẳng định suông) làm `result_ref:`.

## Verification
*(lệnh cụ thể executor chạy để tự kiểm tra)*
- `cd /data/projects/MoneyPrinterTurbo && uv run python cli.py --video-subject "Áo thể thao (sports jersey): chất liệu, công dụng và cách chọn mua" --video-source pexels --stop-at video` → exit code 0, in ra 1 JSON object.
- `test -s <VIDEO_FILE trong JSON output> && ffprobe -v error -show_entries format=duration -of default=nw=1 <path>` → không lỗi, `duration > 0`.
- `uv run pytest test/services/test_cli.py -q` → 100% pass (regression check, CLI vẫn hoạt động đúng theo test suite có sẵn, không liên quan trực tiếp SiliconFlow nhưng đảm bảo không có breakage).
- Xác nhận thủ công: SiliconFlow API key chỉ xuất hiện trong `config.toml` của repo đích — `grep -rn "sk-" /home/lupca/projects/control-tower/` (control-tower repo, KHÔNG phải target repo) phải KHÔNG match gì.

## Pre-scan findings (OCR)
*(chạy `ocr scan --path cli.py`, không nằm trong scope AC nhưng nêu để executor lưu ý)*
- `cli.py` dòng 470-482 (medium/maintainability): logic validate `--bgm-type` không phân biệt rõ giá trị chưa-set (`None`) và "random" set tường minh → hành vi CLI vs UI (WebUI) có thể lệch nhau. **Ngoài scope task này** (task không dùng `--bgm-type`/`--bgm-file`).
- `cli.py` dòng 736-756, `prepare_cli_files` (medium/bug): copy local material không atomic — nếu copy file thứ N lỗi giữa chừng, các file N-1 đã copy trước đó bị mồ côi trong `storage/local_videos/`. **Ngoài scope task này** (dùng `--video-source pexels`, không phải `local`).

## Plan
1. **Cấu hình provider (không đụng code)**: mở `config.toml` (tự sinh từ `config.example.toml` nếu chưa có) tại `/data/projects/MoneyPrinterTurbo`, set SiliconFlow làm LLM provider (`app.llm_provider = "siliconflow"` hoặc theo đúng key config tương ứng trong `app/config/config.py`/`app/models/llm_provider.py`) + `siliconflow_api_key`. Key do user cung cấp trực tiếp cho executor lúc thực thi — **không đi qua control-tower, không log ra console/report**.
2. **(Tuỳ chọn) Voice**: nếu muốn TTS cũng qua SiliconFlow, chọn 1 giọng từ `get_siliconflow_voices()` (`app/services/voice.py`) khi set `--voice-name`; mặc định Edge TTS (miễn phí) vẫn dùng được nếu chỉ cần SiliconFlow cho phần LLM script/terms.
3. **Chạy CLI** (không sửa code): `uv run python cli.py --video-subject "Áo thể thao (sports jersey): chất liệu, công dụng và cách chọn mua" --video-source pexels --stop-at video`. Nếu Pexels chưa có API key, executor có thể hỏi lại user hoặc đổi `--video-source` (nêu rõ trong report).
4. **Xử lý lỗi theo stage** (`cli.py` in ra `failed_stage` khi lỗi — xem `_run_pipeline` trong `app/services/task.py`): nếu fail ở `script`/`terms` → kiểm tra lại SiliconFlow key/base_url; nếu fail ở `materials` → kiểm tra Pexels key hoặc đổi `--video-source local` kèm `--video-materials`.
5. **Verify output**: lấy `VIDEO_FILE` path từ JSON output, chạy `ffprobe` xác nhận file hợp lệ (theo `## Verification`).
6. **Regression check**: `uv run pytest test/services/test_cli.py -q` — đảm bảo CLI vẫn xanh, không phải do executor gây lỗi phụ.
7. **Báo cáo**: trả về đường dẫn tuyệt đối video + log chạy thật (không tóm tắt suông) làm `result_ref:` cho `/review-order` sau này. Không paste giá trị API key vào báo cáo.

Không có file code nào bị sửa trong plan này — toàn bộ là cấu hình (`config.toml`, ngoài `files:`/git tracking chính thức vì đây là file runtime config) + thực thi CLI có sẵn.

## Sub-tasks
- [ ] Set SiliconFlow API key vào `config.toml` của `/data/projects/MoneyPrinterTurbo` — executor tự nhận key trực tiếp từ user lúc thực thi, KHÔNG qua control-tower, KHÔNG lưu vào bất kỳ file control-tower nào.
- [ ] Chạy `cli.py --video-subject "..."` với `--video-source pexels` (mặc định, có thể đổi theo yêu cầu cụ thể user bổ sung khi thực thi).
- [ ] Verify file MP4 output tồn tại + phát được (ffprobe).
- [ ] Báo cáo lại đường dẫn tuyệt đối video + log chạy làm `result_ref:`.
