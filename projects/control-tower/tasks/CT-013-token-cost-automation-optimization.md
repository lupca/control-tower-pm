---
id: CT-013
title: "Đo baseline token cost của luồng manual"
status: done
priority: normal
risk: low
deadline: null
executor: "@claude-opus-4.5"
reviewer: "@lupca"
result_ref: "control-tower@main (knowledge/research/token-baseline-manual-flow.md)"
depends_on: [CT-012]
files:
  - .claude/skills/ (chuỗi file mỗi macro phải đọc — baseline token đo tại đây)
  - log.md
  - AGENTS.md, AGENTS-REFERENCE.md, index.md
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

# CT-013: Đo baseline token cost của luồng manual

> Dự án: [[projects/control-tower/control-tower]]

## Bối cảnh (Context)

**Re-scoped (2026-07-22):** Sau discussion, đã kết luận:
- Script-orchestrator ROI thấp (~25-30% token saving)
- Không cần DB/Beads, MD + script đủ
- Headless dispatch là key → CT-012 đã cover

Task này thu hẹp scope: chỉ **đo baseline token** để có data point so sánh sau khi CT-012 implement. Không còn architecture proposals hay OSS evaluation.

## Tiêu chí nghiệm thu (AC)

> Deliverable là **research doc**: `knowledge/research/token-baseline-manual-flow.md`

- [x] AC1 — **Baseline chi phí token của luồng manual**: bảng "mỗi macro đọc gì / bao nhiêu dòng / lặp lại bao nhiêu lần trong 1 chu kỳ task trọn vẹn" (chuỗi `/pm` → dispatch → `/review-order` → `/verdict` → `/report`). Vẽ đường tăng trưởng chi phí theo thời gian. Data point này dùng để so sánh sau khi CT-012 (headless dispatch) được implement.

## Plan

> Re-scoped 2026-07-22. Task này chỉ ĐỌC + viết 1 file research doc.

### Step 1 — Đo baseline token (→ AC1)
Dùng `wc -l` trên chuỗi file mỗi macro bắt phải đọc (theo Step 0/1 của từng SKILL.md trong `.claude/skills/`): CLAUDE.md, AGENTS.md, AGENTS-REFERENCE.md, index.md, SKILL.md + references, project file, log.md. Lập bảng: macro × (file, số dòng, đọc mấy lần trong 1 chu kỳ task trọn vẹn `/pm`→dispatch→`/review-order`→`/verdict`→`/report`). Đo tốc độ phình log.md. Ngoại suy chi phí 1/3/6 tháng.

### Step 2 — Đóng gói
Viết `knowledge/research/token-baseline-manual-flow.md`, báo done kèm result_ref (commit hash).

## Sub-tasks

- [ ] Đo baseline token: bảng chi phí đọc theo macro + đường tăng trưởng (AC1)
- [ ] Viết research doc `knowledge/research/token-baseline-manual-flow.md`

## Research References

- Commit `cf9886f` — split AGENTS.md 636→152 dòng core (mốc so sánh)
- [[CT-012-model-a-cli-agent-orchestration]] — task này chạy SAU CT-012 để có context headless dispatch
