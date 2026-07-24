# Knowledge Index

Danh mục toàn bộ knowledge file (cross-project + per-project). Cập nhật tự động bởi `/report`. Xem `AGENTS.md` mục 11 cho quy tắc knowledge (loại file, frontmatter, routing).

## Cross-project (`knowledge/`)

| Type | File | Tags | Updated |
|:---|:---|:---|:---|
| decision | [[ADR-001-file-over-api]] | architecture, control-tower | 2026-07-21 |
| decision | [[ADR-002-paradigm-shifts-roadmap]] | architecture, control-tower, paradigm-shift, research | 2026-07-22 |
| decision | [[ADR-003-model-a-cli-agent-orchestration]] | control-tower, model-a, orchestration | 2026-07-22 |
| decision | [[ADR-004-drop-obsidian]] | tooling, visualization, simplification | 2026-07-22 |
| decision | [[ADR-005-archive-dormant-experimental-guidance]] | control-tower, documentation, skills, experimental | 2026-07-23 |
| decision | [[ADR-006-coordination-modes-and-task-states]] | control-tower, coordination, gates, workflow | 2026-07-23 |
| decision | [[ADR-007-report-stats-script]] | control-tower, tooling, report, automation, tokens | 2026-07-24 |
| research | [[discount-promotion-architecture]] | pricing, discount, promotion, e-commerce | 2026-07-22 |
| metric | [[prediction-accuracy]] | metrics, prediction, control-tower, accuracy | 2026-07-22 |
| guide | [[setup-crg-daemon-autostart]] | tooling, code-review-graph, daemon | 2026-07-24 |
| agent | [[@antigravity]] | agent, profile, ai | 2026-07-24 |
| agent | [[@antigravity-3.6]] | agent, profile, ai, deprecated | 2026-07-22 |
| agent | [[@antigravity-3.6-low]] | agent, profile, ai | 2026-07-22 |
| agent | [[@antigravity-3.6-medium]] | agent, profile, ai | 2026-07-22 |
| agent | [[@antigravity-3.6-high]] | agent, profile, ai | 2026-07-23 |
| agent | [[@claude]] | agent, profile, ai, deprecated | 2026-07-22 |
| agent | [[@claude-opus]] | agent, profile, ai | 2026-07-23 |
| agent | [[@claude-sonnet-low]] | agent, profile, ai | 2026-07-22 |
| agent | [[@claude-sonnet-medium]] | agent, profile, ai | 2026-07-22 |
| agent | [[@claude-sonnet-high]] | agent, profile, ai | 2026-07-24 |
| agent | [[@claude-fable]] | agent, profile, ai | 2026-07-24 |
| agent | [[@sonnet-5]] | agent, profile, ai, deprecated | 2026-07-22 |
| agent | [[@gpt-5.6-luna]] | agent, profile, ai | 2026-07-22 |
| agent | [[@gpt-5.6-luna-high]] | agent, profile, ai | 2026-07-24 |
| agent | [[@gpt-5.6-sol]] | agent, profile, ai | 2026-07-24 |
| agent | [[@dev-tung]] | agent, profile, human | 2026-07-21 |
| agent | [[@lupca]] | agent, profile, ai | 2026-07-23 |

*Không tính vào bảng trên (thiếu `type:` frontmatter, không thể phân loại):* `knowledge/guides/review-toolchain.md`, `knowledge/guides/setup-code-review-graph.md`, `knowledge/research/headless-cli-orchestration.md`, `knowledge/research/token-baseline-manual-flow.md`. `knowledge/patterns/*.md` (4 file) dùng schema riêng (`pattern_id`/`category`/`severity`), đã có index riêng tại `knowledge/patterns/_index.md`.

## Per-project (`projects/<name>/docs/`)

*(4 file tồn tại nhưng đều thiếu `type:` frontmatter — chưa thể phân loại theo domain/decision/convention/research)*

| Project | File | Ghi chú |
|:---|:---|:---|
| marketing-video-agent | `docs/llm-providers.md` | có `title`/`project`/`updated`, thiếu `type:` |
| topvnsport-web | `docs/plan.md` | không có frontmatter |
| topvnsport-web | `docs/api chính thức.md` | không có frontmatter |
| topvnsport-web | `docs/Tích hợp Zalo OTP Website.md` | không có frontmatter |
