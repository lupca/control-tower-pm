---
project: marketing-video-agent
full_name: "Marketing Video Agent - AI Video Creation Pipeline"
repo_root: /data/projects/marketing-video-agent
task_prefix: MVA
next_task_id: 2
created: 2026-07-22
updated: 2026-07-22
---

# Marketing Video Agent

Agent pipeline tự động tạo video marketing sử dụng AI. Hệ thống worker-based với các module: leader, research, download, capcut, slideshow, text2img, text2video, tts, delivery, promotion.

## Tiến độ
| Trạng thái | Số task |
|:---|---:|
| done | 0 |
| todo | 0 |
*(Cập nhật bởi `/report`)*

## Tasks
*(Cập nhật bởi `/report` — mỗi lần chạy sẽ regenerate lại toàn bộ danh sách này từ `tasks/*.md`)*
- [[MVA-001-simplify-architecture]] — Đơn giản hóa kiến trúc: từ 17 workers + Celery xuống 1 VideoAgent (changes-requested)

## Quy tắc phê duyệt riêng (Project Gates)
- Mọi thay đổi liên quan đến cấu trúc pipeline (worker orchestration, engine selection) cần User xác nhận trước khi executor thực hiện.
- Test case phải chạy với pytest trong venv phù hợp (`venv-light` hoặc `venv-heavy` tùy dependency) — reviewer độc lập xác nhận qua `/verdict pass`.

## References (tài liệu trong repo code — chỉ tham chiếu, KHÔNG copy)
| Tài liệu | Path | Mô tả |
|:---|:---|:---|
| CLAUDE.md | `CLAUDE.md` | Dev conventions, project structure |
| README.md | `README.md` | Project overview, setup instructions |
| PLAN_SIMPLIFY.md | `PLAN_SIMPLIFY.md` | Simplification plan for the pipeline |
