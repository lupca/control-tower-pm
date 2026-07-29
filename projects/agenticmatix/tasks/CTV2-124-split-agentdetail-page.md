---
id: CTV2-124
title: "Split AgentDetail Page"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: normal
risk: normal
deadline: null
executor: "@claude-opus-4.5"
reviewer: "@claude-opus-4.5"
verdict: pass
verdict_by: "@claude-opus-4.5"
verdict_note: "bypass mode - components extracted, tests pass"
result_ref: 6139100
completed: 2026-07-28
depends_on: [CTV2-122]
files:
  - frontend/src/pages/AgentDetail.tsx
  - frontend/src/components/agents/AgentProfileHeader.tsx
  - frontend/src/components/agents/AgentKpiCards.tsx
  - frontend/src/components/agents/AgentTaskList.tsx
  - frontend/src/pages/__tests__/AgentDetail.test.tsx
flows: []
tests:
  - frontend/src/pages/__tests__/AgentDetail.test.tsx
predicted_success: high
prediction_factors:
  score: 0.8
  deductions:
    - "touches hub node AgentDetailPage (degree 67) (-0.2)"
created: 2026-07-28
updated: 2026-07-28
---

# CTV2-124: Split AgentDetail Page

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

Phase 3/5 của [[CTV2-118-research-frontend-refactor-strategy]] — nguồn: `docs/research/frontend-refactor-strategy.md` §Component Audit (AgentDetail.tsx, 368 dòng, lines 118-205/207-248/250-362). Phụ thuộc [[CTV2-122-parallelize-api-calls]] (cùng sửa `AgentDetail.tsx`).

## Tiêu chí nghiệm thu (AC)

- [ ] Tách **AgentProfileHeader** (lines 118-205: profile + nav) ra `components/agents/AgentProfileHeader.tsx`.
- [ ] Tách **AgentKpiCards** (lines 207-248) ra `components/agents/AgentKpiCards.tsx`.
- [ ] Tách **AgentTaskList** (lines 250-362) ra `components/agents/AgentTaskList.tsx`.
- [ ] `AgentDetail.tsx` sau khi tách chỉ còn fetch data (đã parallelize ở CTV2-122) + compose 3 component trên.
- [ ] Test `AgentDetail.test.tsx` (đã có case null-id từ CTV2-120) bổ sung khẳng định: `AgentKpiCards` nhận đúng `executedCount`/`reviewedCount`/`completedCount` đã tính từ page.

## Verification
- `npm test -- AgentDetail` → pass (bao gồm case null-id cũ)

## Plan
1. Đọc `AgentDetail.tsx` sau khi CTV2-120/121/122 đã áp dụng, xác định lại đúng line range 3 phần.
2. Tách `AgentProfileHeader`, `AgentKpiCards`, `AgentTaskList` theo đúng ranh giới trên.
3. `AgentDetail.tsx` chỉ giữ state/fetch + compose.
4. Cập nhật test `AgentDetail.test.tsx` cho cấu trúc mới, giữ nguyên các case đã pass từ CTV2-120/121.
