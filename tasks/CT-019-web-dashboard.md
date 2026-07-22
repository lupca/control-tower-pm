---
id: CT-019
title: "Triển khai Web Dashboard cho Control Tower (Astro + React)"
status: ready
priority: high
risk: normal
deadline: 2026-08-10
executor: "@antigravity"
reviewer: null
result_ref: null
depends_on: []
files:
  - projects/control-tower-web/src/content/config.ts
  - projects/control-tower-web/src/pages/index.astro
  - projects/control-tower-web/src/pages/kanban.astro
  - projects/control-tower-web/src/pages/tasks.astro
  - projects/control-tower-web/src/pages/graph.astro
  - projects/control-tower-web/src/pages/timeline.astro
  - projects/control-tower-web/src/pages/agents.astro
  - projects/control-tower-web/src/pages/log/[page].astro
flows: [dashboard-overview, kanban-view, task-explorer, dag-graph, audit-log-pagination]
tests: []
created: 2026-07-22
updated: 2026-07-22
---

# CT-019: Triển khai Web Dashboard cho Control Tower (Astro + React)

> Dự án: [[projects/control-tower/control-tower]]

## Tiêu chí nghiệm thu (AC)
- [x] Tạo dự án `/home/lupca/projects/control-tower-web/` với Astro 5 + React 19 + TypeScript.
- [x] Script `content-link.sh` tạo symlink tự động từ data gốc sang Content Collections (`tasks`, `projects`, `reviews`, `agents`, `adrs`, `log.md`, `inbox.md`).
- [x] Schema type-safe Zod cho 5 collections trong `src/content/config.ts`.
- [x] Giao diện Linear/GitHub Dark Mode: Overview Dashboard, Kanban Board (`@hello-pangea/dnd`), Task Data Grid (`@tanstack/react-table`), Dependency DAG Graph (`@xyflow/react`), Gantt Timeline (`frappe-gantt`), Agent Roster, và Paginated Audit Log (20 entries/trang).

## Verification
- `npm run build` hoặc `./node_modules/.bin/astro build` -> 0 type errors, static HTML generation 100% thành công.

## Plan
1. Khởi tạo cấu trúc thư mục `/home/lupca/projects/control-tower-web/`.
2. Tạo script symlink `content-link.sh` và thiết lập Zod schemas (`config.ts`).
3. Phát triển các React UI components & Astro pages.
4. Kiểm thử build tĩnh và xác nhận dữ liệu hiển thị chính xác.
