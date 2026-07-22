---
id: CT-014
title: "Sửa design doc spawn pattern: task file link + model tiering"
status: done
priority: high
risk: low
deadline: null
executor: "@sonnet-5"
reviewer: "@claude-opus"
result_ref: "control-tower@main (knowledge/research/headless-cli-orchestration.md §8, uncommitted)"
depends_on: [CT-012]
files:
  - knowledge/research/headless-cli-orchestration.md
  - knowledge/agents/*.md
flows: []
tests: []
dispatched: 2026-07-22
in_review: 2026-07-22
predicted_success: high
prediction_factors:
  score: 0.9
  deductions:
    - "blast_radius: 1 file edit (-0.0)"
    - "no_tests: doc change, no code (-0.1)"
confidence_interval: [0.8, 0.95]
created: 2026-07-22
updated: 2026-07-22
---

# CT-014: Sửa design doc spawn pattern

> Dự án: [[projects/control-tower/control-tower]]

## Bối cảnh (Context)

Design doc hiện tại (CT-012) có 2 vấn đề:
1. **Viết chay prompt** — spawn command truyền AC/Plan inline thay vì đưa link task file
2. **Model tiering sai** — không phân biệt executor (model rẻ) vs reviewer (model đắt)

## Tiêu chí nghiệm thu (AC)

- [x] AC1: Section 8.1 template sửa: prompt = task file path (không inline AC/Plan)
- [x] AC2: Section 8.2 tích hợp Reputation (§12.3): chọn agent/model dựa trên domain match + success_rate, không hardcode
- [x] AC3: Section 8.3 ví dụ spawn: cwd + task file path + reputation-recommended model
- [x] AC4: Phân biệt rõ executor tier (model rẻ, high success_rate) vs reviewer tier (model đắt, thorough)

## Plan

### Step 1 — Đọc reputation system
Đọc `AGENTS-EXPERIMENTAL.md` §12 + `knowledge/agents/*.md` để hiểu cơ chế auto-recommend.

### Step 2 — Sửa section 8
Edit `knowledge/research/headless-cli-orchestration.md`:
- 8.1: Template dùng task file path (CLI tự đọc AC/Plan từ file)
- 8.2: Tích hợp §12.3 — query reputation, không hardcode model
- 8.3: Ví dụ với task file path + reputation query
- 8.4: Tiering rule: executor=cheap model with high success_rate, reviewer=expensive model for thoroughness

### Step 3 — Verify
Đọc lại file, confirm 4 AC pass.

## Sub-tasks

- [x] Đọc AGENTS-EXPERIMENTAL.md §12 (reputation)
- [x] Edit section 8.1 (task file path template)
- [x] Edit section 8.2 (reputation integration)
- [x] Edit section 8.3 (examples)
- [x] Add section 8.4 (tiering rule)

## Result

`knowledge/research/headless-cli-orchestration.md` §8 rewritten:
- 8.1: prompt = absolute task file path (in control-tower repo, since cwd = target repo — cross-repo path called out explicitly, no inline AC/Plan)
- 8.2: model resolved dynamically from `knowledge/agents/*.md` via §12.2 domain match + §12.3 success_rate/weakness filtering + tiering; old hardcoded CLI→model table replaced with a resolution algorithm (roster kept only as an illustrative snapshot)
- 8.3: full example re-derived for a `backend`+`testing` task — `@antigravity` (agy) executor + `@claude-opus` (claude) reviewer, both cwd + absolute task file path
- 8.4: new tiering rule — executor tier = cheap/fast + high success_rate, reviewer tier = expensive/thorough regardless of `total_tasks_executed`
