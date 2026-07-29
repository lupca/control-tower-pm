---
id: CTV2-120
title: "Fix High-Severity Bugs from Pre-scan"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: high
risk: normal
deadline: null
executor: "@gpt-5.6-luna-high"
reviewer: "@gemini-3.1-pro-high"
result_ref: "912db309ca18f802eb42203e27fe9e67ebd7e6c3"
depends_on: []
files:
  - frontend/src/pages/AgentDetail.tsx
  - frontend/src/pages/ProjectDetail.tsx
  - frontend/src/pages/Dashboard.tsx
flows: []
tests:
  - frontend/src/pages/__tests__/AgentDetail.test.tsx
predicted_success: high
prediction_factors:
  score: 0.8
  deductions:
    - "touches hub nodes AgentDetailPage/Dashboard/ProjectDetailPage (degree 67/66/61) (-0.2)"
created: 2026-07-28
updated: 2026-07-28
dispatched: 2026-07-28
---

# CTV2-120: Fix High-Severity Bugs from Pre-scan

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

Phase 1/5 của [[CTV2-118-research-frontend-refactor-strategy]] — nguồn: `docs/research/frontend-refactor-strategy.md` §Code Smell Findings (OCR pre-scan), bug severity HIGH/MEDIUM.

## Tiêu chí nghiệm thu (AC)

- [x] `AgentDetail.tsx:82-83`: filter task theo executor/reviewer phải guard `t.id != null` (tránh null dereference).
- [x] `AgentDetail.tsx:114-116`: bỏ fallback capabilities hard-code, hoặc lấy từ agent thật; không hiển thị dữ liệu giả khi `agent.capabilities` rỗng/không hợp lệ.
- [x] `ProjectDetail.tsx:46-52`: khi fetch tasks lỗi, set `tasksError` state hiển thị banner cho user thay vì chỉ `console.warn`.
- [x] `ProjectDetail.tsx:192`: khi `created_at` null, hiển thị "Unknown" thay vì fallback `Date.now()`.
- [x] `Dashboard.tsx:133`: khi API lỗi, hiển thị banner lỗi cho user (không chỉ log console).
- [x] Test `AgentDetail.test.tsx` khẳng định: với `tasks` chứa item `id: null`, component không throw và không hiển thị task đó trong executor/reviewer list.

## Verification
- `npm test -- AgentDetail` → pass với case `id: null`
- Review code diff: không còn `Date.now()` fallback cho created_at, không còn hardcoded capabilities fallback

## Plan
1. Sửa 2 bug trong `AgentDetail.tsx` (null-guard filter, bỏ fallback capabilities).
2. Sửa 2 bug trong `ProjectDetail.tsx` (error banner cho task fetch, "Unknown" cho created_at).
3. Sửa 1 bug trong `Dashboard.tsx` (error banner cho stats fetch).
4. Viết/cập nhật test `AgentDetail.test.tsx` cho case null id.
