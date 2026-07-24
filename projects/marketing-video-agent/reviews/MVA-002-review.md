---
id: MVA-002
task_path: projects/marketing-video-agent/tasks/MVA-002-restore-text2img-engine.md
project: marketing-video-agent
result_ref: "a614bd0525a0ca354b971d732a2f94b57fe60f2d"
executor: "@gpt-5.6-sol"
reviewer: "@antigravity"
status: approved
issued: 2026-07-24
verdict: pass
verdict_date: 2026-07-24
---

# Phiếu Review: MVA-002 — Khôi phục engine text2img (gen ảnh từ prompt)

- Dự án: marketing-video-agent (`/data/projects/marketing-video-agent`)
- Task gốc: `projects/marketing-video-agent/tasks/MVA-002-restore-text2img-engine.md`
- Result-ref: `a614bd0525a0ca354b971d732a2f94b57fe60f2d`
- Executor: @gpt-5.6-sol
- Ngày phát phiếu: 2026-07-24

## Acceptance Criteria cần verify

- [x] **AC1:** `engines/text2img.py` hoạt động: `generate_image(prompt, width, height) -> Path` trả file ảnh
- [x] **AC2:** Hỗ trợ ComfyUI workflow Flux.1 Schnell (port từ worker cũ commit trước `77bc43b`)
- [x] **AC3:** `tools/image_tool.py` — smolagents `ImageTool(Tool)` wrap engine, expose prompt/width/height cho LLM
- [x] **AC4:** Output path unique (không ghi đè giữa các lần gọi)
- [x] **AC5:** Test: `pytest tests/test_text2img.py` pass

## Definition of Done (AGENTS.md mục 3)

- [x] Toàn bộ AC pass
- [x] Test liên quan xanh 100%: `tests/test_text2img.py`
- [x] Không regression (test khác trong module vẫn xanh — `pytest tests/`)
- [x] Reviewer khác executor (bạn đang review, hãy xác nhận bạn ≠ @gpt-5.6-sol)

## Test gợi ý chạy trong repo code

```bash
# Full test suite
.venv-light/bin/pytest tests/ -v

# Text2img tests only
.venv-light/bin/pytest tests/test_text2img.py -v

# Check unique output path logic
.venv-light/bin/python -c "from engines.text2img import generate_image; print(generate_image.__doc__)"
```

## Câu hỏi rủi ro

1. ComfyUI workflow Flux.1 Schnell: verify workflow JSON/dict matches codebase cũ (commit trước 77bc43b)
2. Polling logic: timeout + retry khi ComfyUI chậm?
3. Unique output path: dùng uuid hay timestamp? Verify không collision.
4. ImageTool đã được đăng ký trong `agent.py` và `tools/__init__.py` chưa?

## Gợi ý công cụ

Repo code đích có sẵn skill `/code-review` — khuyến khích dùng để đọc diff + chạy test.

## Trả kết quả

```
/verdict MVA-002 <pass|changes> --reviewer @antigravity [--commit <hash>] [--notes "..."]
```
