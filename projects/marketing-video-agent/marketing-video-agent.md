---
project: marketing-video-agent
full_name: "Marketing Video Agent - AI Video Creation Pipeline"
repo_root: /data/projects/marketing-video-agent
task_prefix: MVA
next_task_id: 11
created: 2026-07-22
updated: 2026-07-22
---

# Marketing Video Agent

Agent pipeline tự động tạo video marketing sử dụng AI. Hệ thống worker-based với các module: leader, research, download, capcut, slideshow, text2img, text2video, tts, delivery, promotion.

## Tiến độ
| Trạng thái | Số task |
|:---|---:|
| done | 8 |
| todo | 2 |
*(Cập nhật bởi `/report`)*

## Tasks
*(Cập nhật bởi `/report` — mỗi lần chạy sẽ regenerate lại toàn bộ danh sách này từ `tasks/*.md`)*
- [[MVA-001-simplify-architecture]] — Đơn giản hóa kiến trúc: từ 17 workers + Celery xuống 1 VideoAgent (done)
- [[MVA-002-restore-text2img-engine]] — Khôi phục engine text2img (done)
- [[MVA-003-restore-slideshow-engine]] — Khôi phục engine slideshow (done)
- [[MVA-004-fix-engine-bugs-stability]] — Fix bugs + ổn định engines hiện tại (done)
- [[MVA-005-tts-resilience-cloud-fallback]] — Gia cố TTS + cloud video fallback (todo)
- [[MVA-006-restore-capcut-parser]] — Khôi phục CapCut parser (todo)
- [[MVA-007-verify-current-pipeline]] — Smoke test pipeline hiện tại (done)
- [[MVA-008-fix-engines-standalone]] — Fix engines standalone (done)
- [[MVA-009-fix-remaining-engine-issues]] — Fix 3 blocking issues từ review (done)
- [[MVA-010-test-orchestration-siliconflow]] — Test orchestration pipeline với SiliconFlow API (done)

## Quy tắc phê duyệt riêng (Project Gates)
- Mọi thay đổi liên quan đến cấu trúc pipeline (worker orchestration, engine selection) cần User xác nhận trước khi executor thực hiện.
- Test case phải chạy với pytest trong venv phù hợp (`venv-light` hoặc `venv-heavy` tùy dependency) — reviewer độc lập xác nhận qua `/verdict pass`.

## References (tài liệu trong repo code — chỉ tham chiếu, KHÔNG copy)
| Tài liệu | Path | Mô tả |
|:---|:---|:---|
| CLAUDE.md | `CLAUDE.md` | Dev conventions, project structure |
| README.md | `README.md` | Project overview, setup instructions |
| PLAN_SIMPLIFY.md | `PLAN_SIMPLIFY.md` | Simplification plan for the pipeline |
| LLM Providers | `docs/llm-providers.md` | SiliconFlow API keys, models (Qwen3-32B, GLM-5.1) |
