---
project: control-tower-web
full_name: "Control Tower Web - Dashboard UI"
repo_root: /home/lupca/projects/control-tower-web
task_prefix: CTW
next_task_id: 14
created: 2026-07-23
updated: 2026-07-23
---

# Control Tower Web

Web dashboard cho control-tower, built với Astro + Tailwind CSS.

## Tiến độ
| Trạng thái | Số task |
|:---|---:|
| done | 13 |
*(Cập nhật bởi `/report`)*

## Tasks
*(Cập nhật bởi `/report` — mỗi lần chạy sẽ regenerate lại toàn bộ danh sách này từ `tasks/*.md`)*
- [[CTW-001-research-css-and-file-overwrite-bugs]] — Research: CSS not loading + file overwrite bugs (done)
- [[CTW-002-setup-npm-environment]] — Setup npm environment cho control-tower-web (done)
- [[CTW-003-fix-dev-server-connection-refused]] — Fix dev server startup - ERR_CONNECTION_REFUSED on port 3004 (done)
- [[CTW-004-fix-gantt-timeline-blocked]] — Fix Gantt Timeline bị che không thao tác được (done)
- [[CTW-005-fix-knowledge-base-links]] — Fix Knowledge Base không click xem chi tiết được (done)
- [[CTW-006-fix-task-completion-data]] — Fix Task Completion hiện 0% sai data (done)
- [[CTW-007-fix-kanban-board-layout]] — Fix Kanban Board bảng bé che hết task (done)
- [[CTW-008-fix-dashboard-data-loading]] — Fix dashboard data loading bugs (done)
- [[CTW-009-fix-agent-roster-dynamic]] — Agent Roster load dynamic data từ knowledge/agents/ (done)
- [[CTW-010-kanban-collapsible-columns]] — Kanban Board - collapsible columns (done)
- [[CTW-011-task-agent-detail-pages]] — Add task detail & agent detail pages (done)
- [[CTW-012-knowledge-base-full-tree]] — Knowledge Base load full tree + folder categorization (done)
- [[CTW-013-fix-inbox-log-live-sync]] — Fix inbox & log pages read from live control-tower repo (done)

## Quy tắc phê duyệt riêng (Project Gates)
- UI changes cần screenshot hoặc preview trước khi merge.

## References (tài liệu trong repo code — chỉ tham chiếu, KHÔNG copy)
| Tài liệu | Path | Mô tả |
|:---|:---|:---|
| astro.config.mjs | `astro.config.mjs` | Astro configuration |
| tailwind.config.mjs | `tailwind.config.mjs` | Tailwind configuration |
