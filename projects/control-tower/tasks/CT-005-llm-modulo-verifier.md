---
id: CT-005
title: "LLM-Modulo — Symbolic verifier cho LLM-generated plans"
status: done
priority: medium
risk: high
deadline: null
executor: "@sonnet-5"
reviewer: "@sonnet-5"
result_ref: "control-tower@main (commit 510b3b4)"
depends_on: []
files:
  - .claude/verifier-rules.yaml
  - .claude/skills/pm/SKILL.md
  - .claude/skills/pm/references/task-creation.md
  - AGENTS.md
flows: [pm-create, plan]
tests: []
dispatched: 2026-07-22
in_review: 2026-07-22
created: 2026-07-22
updated: 2026-07-22
tier: 2
paradigm_source: "LLM-Modulo Framework (ICML 2024)"
---

# CT-005: LLM-Modulo — Symbolic verifier cho LLM-generated plans

> Dự án: [[projects/control-tower/control-tower]]

> ⚠️ **Four-eyes waived by explicit User instruction** (2026-07-22): batch-processed alongside CT-004, CT-006–CT-010 with `reviewer: executor` per User request in chat, compensated by an independent aggregate review — see [[CT-011-review-paradigm-shift-batch]] (reviewer `@claude-4.5`). Deliberate, logged exception to `AGENTS.md` §1, not an oversight.

## Bối cảnh (Context)

Hiện tại: `/pm` dùng LLM generate AC + Plan → human approve.

Research (ICML 2024): "LLMs fundamentally cannot plan autonomously. They should be treated as universal approximate knowledge sources within a neuro-symbolic architecture where external verifiers check generated candidates."

## Tiêu chí nghiệm thu (AC)

- [x] AC1: Tạo verifier rules set (có thể mở rộng) — `.claude/verifier-rules.yaml`, 5 rules.
- [x] AC2: `/pm` runs verifier BEFORE showing plan to human (task-creation.md step 12, chạy ngay trước "Closing the Spec Gate").
- [x] AC3: Verifier output format documented in `AGENTS.md` §15.3.
- [x] AC4: Human có thể override verifier warnings (với explicit acknowledgment) — `AGENTS.md` §15.4, ghi vào `## Verifier Overrides` + log entry.

## Plan

### Phase 1: Rules schema
1. `.claude/verifier-rules.yaml` — 5 rules ban đầu (`no-circular-deps`, `files-exist`, `reasonable-scope`, `tests-for-changes`, `no-conflicting-tasks`), mỗi rule là `id` + `check` (đánh giá bởi agent đọc task draft + graph/backlog state, không phải code chạy thật — phù hợp với bản chất Markdown-only của control-tower).

### Phase 2: Gate integration
2. `AGENTS.md` §15 — định nghĩa rules schema, khi nào chạy, output format, override mechanism.
3. `.claude/skills/pm/references/task-creation.md` — step 12 chạy verifier ngay trước Spec Gate; step 11 (confidence, CT-006) chạy trước đó vì confidence phụ thuộc 1 phần vào việc verifier pass sạch hay không (`AGENTS.md` §16.1).

### Phase 3: Override audit
4. Override được ghi vào `## Verifier Overrides` trong task body + `pm-create` log entry — auditable qua `/lint`.

## Sub-tasks

- [x] Design verifier rules schema
- [x] Implement each rule checker (as agent-evaluated checks, not executable code — this repo has no code runtime)
- [x] Integrate verifier into `/pm` flow (before Spec Gate)
- [x] Auto-fix logic cho simple violations (documented: mechanical fixes like narrowing `files:` or adding a missing test sub-task)
- [x] Override mechanism với audit (`## Verifier Overrides` + log.md)

## Causal Analysis

```yaml
causal_analysis:
  root_cause: "/pm trước đây generate AC/Plan hoàn toàn bằng LLM judgment, không có bước kiểm tra deterministic nào trước khi đưa ra Spec Gate — rủi ro: task thiếu tests:, scope quá lớn, hoặc conflict với task khác mà không ai phát hiện cho tới khi executor bắt đầu làm."
  mechanism: "Thêm .claude/verifier-rules.yaml (5 rule tĩnh) + bước chạy verifier bắt buộc trong task-creation.md ngay trước Spec Gate (AGENTS.md §15) — mọi task draft phải qua check này, ❌ thì cần auto-fix hoặc override tường minh (ghi log) trước khi hiện cho User."
  counterfactual: "Không có fix này, các lỗi như 'missing test cho file bị đổi' hay 'blast radius 12 files không được đề xuất split' sẽ tiếp tục lọt qua Spec Gate tới tận Plan Gate hoặc dispatch, làm executor phát hiện muộn hơn nhiều — tốn thời gian rework."
  pattern_id: null
```

## Research References

- [LLM-Modulo Framework (ICML 2024)](https://proceedings.mlr.press/v235/kambhampati24a.html)
- [LaMMA-P: LLM-Driven PDDL Planning (2024)](https://arxiv.org/pdf/2409.20560)
- [Plan-and-Act Framework (2025)](https://arxiv.org/html/2503.09572v3)
