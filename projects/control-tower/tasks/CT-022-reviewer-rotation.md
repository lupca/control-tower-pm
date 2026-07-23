---
id: CT-022
title: "Reviewer Rotation — track rejections, enforce reviewer change"
status: done
priority: medium
risk: normal
deadline: null
executor: "@claude-opus-4.5"
reviewer: "@lupca"
result_ref: "inline-session-2026-07-23"
depends_on: []
files:
  - .claude/skills/verdict/SKILL.md
  - .claude/skills/review-order/SKILL.md
flows: [verdict-changes, review-order]
tests: []
dispatched: 2026-07-23
in_review: 2026-07-23
predicted_success: high
prediction_factors:
  score: 0.9
  deductions:
    - "content_only: skill markdown edit (-0.0)"
    - "no_tests: meta-project (-0.1)"
confidence_interval: [0.85, 0.95]
created: 2026-07-23
updated: 2026-07-23
rejections: 0
---

# CT-022: Reviewer Rotation — track rejections, enforce reviewer change

> Dự án: [[projects/control-tower/control-tower]]

## Bối cảnh

Tránh ping-pong giữa cùng executor/reviewer khi task bị reject nhiều lần. Nếu reviewer reject 2+ lần, cần góc nhìn thứ 3 (reviewer khác) để xác nhận lỗi có thật hay reviewer quá khắt khe.

## Tiêu chí nghiệm thu (AC)

- [x] **AC1:** `/verdict changes` tăng `rejections:` counter trong task frontmatter
- [x] **AC2:** `/verdict changes` alert khi `rejections >= 2`: "Cần đổi Reviewer hoặc nâng cấp Executor"
- [x] **AC3:** `/review-order` refuse nếu `rejections >= 2` và `--reviewer` trùng reviewer cũ

## Implementation

**verdict/SKILL.md Step 3b:**
- Step 4: Increment `rejections:` (default 0)
- Step 5: Write `rejections: <N>` to frontmatter
- Step 9: Alert if `rejections >= 2`

**review-order/SKILL.md:**
- New Step 2: Validate reviewer rotation — refuse if same reviewer on `rejections >= 2`

## Notes

- Implemented inline by coordinator (not dispatched) — small skill edit approved in session
- Handoff Tracking (Component 2) deferred — optional `--track` flag if needed later
