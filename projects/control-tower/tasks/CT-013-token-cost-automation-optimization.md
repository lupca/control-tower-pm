---
id: CT-013
title: "Tối ưu chi phí token + luồng tự động đa agent (không giảm độ chính xác so với manual)"
status: todo
priority: high
risk: normal
deadline: null
executor: null
reviewer: null
result_ref: null
depends_on: []
files:
  - log.md (568 dòng, tăng ~280/ngày, mọi skill cùng ghi + /pm phải đọc cho bước "similar tasks")
  - projects/control-tower/control-tower.md (next_task_id — shared mutable counter)
  - index.md §3 (bảng tiến độ — duplicate state với <name>.md + frontmatter)
  - AGENTS-EXPERIMENTAL.md §18.1 (events.jsonl — định nghĩa nhưng chưa implement)
  - projects/*/reviews/ (phiếu review copy nguyên AC/DoD — duplicate token)
  - .claude/skills/ (chuỗi file mỗi macro phải đọc — baseline token đo tại đây)
flows: []
tests: []
dispatched: null
in_review: null
predicted_success: high
prediction_factors:
  score: 0.9
  deductions:
    - "blast_radius: khảo sát toàn hệ nhưng deliverable = 1 research doc (-0.0)"
    - "hub_bridge: n/a — meta-project không có code graph (-0.0)"
    - "no_tests: true — research task, deliverable là doc không phải code (-0.1)"
confidence_interval: [0.75, 0.95]
created: 2026-07-22
updated: 2026-07-22T20:00
---

# CT-013: Tối ưu chi phí token + luồng tự động đa agent

> Dự án: [[projects/control-tower/control-tower]]

## Bối cảnh (Context)

Hệ thống đang hoạt động **rất tốt ở chế độ manual**. Mục tiêu của task này KHÔNG phải "scaling" chung chung mà là 3 điều User chốt (2026-07-22):

1. **Tối ưu chi phí token nhất có thể** khi đa agent hoạt động.
2. **Luồng tự động thật mượt mà** (giảm thao tác tay ở các khớp nối /pm → dispatch → review-order → verdict).
3. **Ràng buộc cứng: KHÔNG giảm tính chính xác/hiệu suất so với manual hiện tại** — Spec Gate + Plan Gate + four-eyes + human confirm khi close giữ nguyên 100%; chỉ tự động hóa phần cơ học.

Được phép thay đổi cách lưu trữ hoặc bất cứ thành phần nào (File-Over-API không phải bất khả xâm phạm — nhưng thay đổi phải chứng minh đáng giá). Vấn đề #0 (AGENTS.md context bloat) đã xử lý trước đó (commit `cf9886f`, giảm 636 → 152 dòng core) — dùng làm mốc so sánh cách tiếp cận.

Khảo sát sơ bộ + search OSS đã làm 2026-07-22 (kết quả nhúng trong AC bên dưới) — executor thẩm định sâu và được quyền bác bỏ nếu số liệu không ủng hộ.

## Tiêu chí nghiệm thu (AC)

> Deliverable là **research doc**: `knowledge/research/token-cost-automation-optimization.md` (frontmatter chuẩn `AGENTS-PLAYBOOK.md` §11.3, `type: research`, `scope: general`).

- [ ] AC1 — **Baseline chi phí token của luồng manual**: bảng "mỗi macro đọc gì / bao nhiêu dòng / lặp lại bao nhiêu lần trong 1 chu kỳ task trọn vẹn" (chuỗi `/pm` → dispatch → `/review-order` → `/verdict` → `/report`). Số liệu khởi điểm đã đo: `/pm` đọc CLAUDE.md + AGENTS.md (152) + AGENTS-REFERENCE (84) + index.md (78) + SKILL+references (~92) + project file + log.md (568, tăng ~280/ngày) + patterns; phiếu review copy nguyên AC/DoD (~40-80 dòng duplicate); `/report` rescan 43 file kể cả 24 task done bất biến. Vẽ đường tăng trưởng chi phí theo thời gian nếu không làm gì.
- [ ] AC2 — **Xác nhận/bác bỏ 6 blocker tự động hóa** (đánh giá dưới lăng kính token + automation, kèm bằng chứng đo được): (1) log.md append-only shared-write phình vô hạn; (2) next_task_id race khi 2 phiên /pm song song; (3) events.jsonl §18.1 chưa implement → đa agent không có state để poll/claim; (4) 24/27 task done không archive → scan O(n) vĩnh viễn; (5) tiến độ duplicate 3 nơi sync tay; (6) inbox.md + prediction-accuracy.md shared-write (nghi ngờ: chưa phải blocker).
- [ ] AC3 — **Đánh giá opensource/thư viện**, tối thiểu các ứng viên đã tìm được: **Beads** (`bd`, steveyegge/beads — git-backed issue tracker cho coding agents: JSONL source of truth + SQLite cache, DAG deps, hash ID, `bd ready`, compaction — nghi ngờ đánh trúng blocker #1-#4 cùng lúc), **gnap** (git-native task board), **swarm-protocol** (MCP: claim/conflict/heartbeat/handoff), **Claude Code native** (Agent Teams / subagents / hooks), **headless CLI** (`claude -p`, `codex exec` — giao với CT-012). Trục đánh giá bắt buộc từng ứng viên: giải quyết blocker nào / chi phí tích hợp + migration / tương thích git + File-Over-API / **có phá gates + four-eyes không (phá → loại)**.
- [ ] AC4 — **Đề xuất kiến trúc target**: so sánh tối thiểu 2-3 phương án (Incremental — vá từng lỗ giữ triết lý file; Beads-backend — bd quản tầng task, markdown giữ spec/knowledge/ADR; Hybrid) với **ước lượng token saving từng phương án** và mô tả luồng tự động end-to-end tương ứng. Mỗi phương án phải chỉ rõ cơ chế bảo toàn độ chính xác: gates + four-eyes + human confirm giữ ở đâu, phần nào được tự động hóa (chỉ phần cơ học: spawn, chuyển status, append log, regenerate report).
- [ ] AC5 — **Roadmap task follow-up**: 1 thay đổi = 1 task ứng viên (tên, phạm vi 1 câu, depends_on, cờ "cần ADR" nếu đụng AGENTS*/skill/storage), xếp thứ tự blocker-trước + task-mở-khóa-task-khác trước. Task này **chỉ nghiên cứu** — mọi thay đổi thật nằm ở follow-up, tạo qua `/pm` từng cái.

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] Đo baseline token: bảng chi phí đọc theo macro + đường tăng trưởng (AC1)
- [ ] Xác nhận/bác bỏ 6 blocker với bằng chứng đo được (AC2)
- [ ] Thẩm định sâu Beads / gnap / swarm-protocol / Claude native / headless CLI theo 4 trục (AC3)
- [ ] Thiết kế + so sánh 2-3 phương án kiến trúc, ước lượng saving từng phương án (AC4)
- [ ] Viết roadmap follow-up + đóng gói research doc vào `knowledge/research/` (AC5)

## Research References

- Commit `cf9886f` — split AGENTS.md 636→152 dòng core (mốc so sánh)
- [Beads Documentation](https://steveyegge.github.io/beads/) + [GitHub steveyegge/beads](https://github.com/steveyegge/beads) + [Beads Blows Up — Steve Yegge](https://steve-yegge.medium.com/beads-blows-up-a0a61bb889b4)
- [9 Open-Source Agent Orchestrators 2026 — Augment Code](https://www.augmentcode.com/tools/open-source-agent-orchestrators) (gnap, swarm-protocol)
- [Best Multi-Agent Coding Orchestrators 2026 — amux](https://amux.io/blog/best-multi-agent-orchestrators-2026/) · [The Code Agent Orchestra — Addy Osmani](https://addyosmani.com/blog/code-agent-orchestra/)
- [[CT-012-model-a-cli-agent-orchestration]] — Model A headless CLI (agy/claude/codex/copilot); kiến trúc target của CT-013 phải khớp với CT-012
- [[CT-008-stigmergic-coordination]] — events.jsonl §18.1 định nghĩa nhưng chưa implement
