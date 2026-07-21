---
type: decision
scope: general
created: 2026-07-21
updated: 2026-07-21
tags: [architecture, control-tower]
related: []
---

# ADR-001: File-Over-API — quản lý task bằng Markdown + Git thay vì Jira/Linear/Notion

## Context
Điều phối công việc giữa nhiều repo (topvnsport-pmi, topvnsport-oms, ...) và nhiều executor/reviewer (người, nhiều AI khác nhau) cần một nơi duy nhất chứa trạng thái task, audit trail, và knowledge — nhưng không muốn phụ thuộc một SaaS ngoài (Jira/Linear/Notion) với API riêng, quyền truy cập riêng, và dữ liệu không nằm cùng chỗ với code.

## Decision
Toàn bộ task, tiến độ, audit log và domain knowledge được lưu dưới dạng file Markdown (+ YAML frontmatter) trong chính repo `control-tower`, versioned bằng git. Không có backend, không có API riêng — mọi thao tác đọc/ghi là đọc/ghi file. Agent (Claude Code) đóng vai trò lớp điều phối đọc/ghi các file này theo luật chơi trong `AGENTS.md`.

## Consequences
- **Dễ hơn**: audit trail tự nhiên qua `git log`/`git blame`; không cần đồng bộ giữa "trạng thái thật" và "trạng thái trong tool"; bất kỳ ai có git clone đều xem được toàn bộ lịch sử; executor/reviewer ngoài hệ chỉ cần đọc 1 file, không cần tài khoản/API riêng.
- **Khó hơn**: không có UI kéo-thả, không có notification tự động, không có dashboard real-time — phải tự dựng (vd Obsidian graph/canvas) nếu muốn trực quan hoá.
- **Trade-off chấp nhận**: nhiều task đồng thời có thể gây git conflict nếu chung 1 file lớn — đây là lý do dẫn tới quyết định tách task-per-file (xem migration task-per-file, 2026-07-21).

## Status
Accepted
