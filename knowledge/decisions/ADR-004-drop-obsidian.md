---
type: decision
scope: general
created: 2026-07-22
updated: 2026-07-22
tags: [tooling, visualization, simplification]
related: [[ADR-001-file-over-api]]
---

# ADR-004: Bỏ hoàn toàn Obsidian khỏi control-tower

## Context

Hệ thống từng dùng Obsidian làm lớp trực quan hóa: `.obsidian/graph.json` (tô màu Graph view theo project), `control-tower-map.canvas` (sơ đồ luồng Mô hình B), và quy ước wikilink được giải thích bằng lý do "để Obsidian Graph vẽ cạnh". Bước onboarding project mới (AGENTS-PLAYBOOK.md §10) bắt buộc cập nhật 2 file này thủ công — từng bị bỏ sót (WMS) và tốn công bảo trì mà không phục vụ vận hành thật.

## Decision

Bỏ Obsidian hoàn toàn (User quyết định 2026-07-22): xóa `.obsidian/` + `control-tower-map.canvas`, ignore `.obsidian/` trong `.gitignore`, gỡ bước "Update the Obsidian visualization" khỏi runbook onboarding, gỡ các câu giải thích wikilink-vì-Obsidian trong skill/reference.

Dòng backlink `> Dự án: [[...]]` và wikilink trong `## Tasks` **giữ nguyên** — chúng vẫn là quy ước điều hướng thuần Markdown, vô hại, và tồn tại trong 40+ file task cũ; không đáng công gỡ.

## Consequences

- Dễ hơn: onboarding project mới bớt 1 bước thủ công dễ sai; repo không còn file config editor-specific.
- Mất đi: không còn sơ đồ trực quan luồng Model B và Graph view tô màu. Nếu sau này cần visualization, tạo từ dữ liệu thật (frontmatter/JSONL) thay vì bảo trì tay.

## Status

Accepted
