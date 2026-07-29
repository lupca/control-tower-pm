---
id: CTV2-126
title: "Migrate Stat Cards to Shared Component"
repo_root: /home/lupca/projects/control-tower-v2
status: todo
priority: normal
risk: normal
deadline: null
executor: "@gpt-5.6-luna-high"
reviewer: null
result_ref: null
depends_on: [CTV2-119, CTV2-124, CTV2-125]
files:
  - frontend/src/components/ui/stat-card.tsx
  - frontend/src/pages/Dashboard.tsx
  - frontend/src/pages/AgentDetail.tsx
  - frontend/src/pages/ProjectDetail.tsx
  - frontend/src/pages/Projects.tsx
  - frontend/src/components/agents/AgentStats.tsx
  - frontend/src/components/dashboard/KpiCards.tsx
flows: []
tests:
  - frontend/src/components/ui/__tests__/stat-card.test.tsx
predicted_success: high
prediction_factors:
  score: 0.8
  deductions:
    - "touches hub nodes Dashboard/AgentDetailPage/ProjectDetailPage/ProjectsPage (-0.2)"
created: 2026-07-28
updated: 2026-07-28
---

# CTV2-126: Migrate Stat Cards to Shared Component

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

Phase 4/5 của [[CTV2-118-research-frontend-refactor-strategy]] — nguồn: `docs/research/frontend-refactor-strategy.md` §Duplicated Patterns (Stat Card, 15+ occurrences). Phụ thuộc [[CTV2-119-shadcn-ui-core-primitives]] (định nghĩa `StatCard`) và [[CTV2-124-split-agentdetail-page]]/[[CTV2-125-split-projectdetail-page]] (các KPI-card component vừa tách phải dùng `StatCard` mới thay vì markup lặp).

## Tiêu chí nghiệm thu (AC)

- [ ] `AgentKpiCards.tsx` (từ CTV2-124), `ProjectKpiCards.tsx` (từ CTV2-125), `Dashboard.tsx`, `Projects.tsx`, `AgentStats.tsx`, `dashboard/KpiCards.tsx` đều dùng chung `<StatCard>` từ `components/ui/stat-card.tsx` thay vì markup Tailwind lặp lại (`rounded-xl border border-gray-800/80 bg-gray-900/60 p-4 shadow-lg backdrop-blur-sm flex items-center justify-between`).
- [ ] Không còn class Tailwind trùng lặp cho stat card ở 7 file trên (grep xác nhận).
- [ ] Giao diện không đổi (visual parity) — cùng icon/label/value/trend hiển thị như trước.
- [ ] Test `stat-card.test.tsx` mở rộng: khẳng định `trend` prop render đúng mũi tên tăng/giảm.

## Verification
- `npm test -- stat-card` → pass
- `grep -rn "rounded-xl border border-gray-800/80 bg-gray-900/60 p-4 shadow-lg backdrop-blur-sm" frontend/src` → chỉ còn xuất hiện bên trong `stat-card.tsx`

## Plan
1. Xác nhận `StatCard` (CTV2-119) hỗ trợ đủ prop cần cho cả 7 nơi dùng (icon, label, value, trend).
2. Thay từng nơi dùng markup lặp bằng `<StatCard>`.
3. Kiểm tra visual parity (screenshot/manual so sánh trước-sau nếu cần).
4. Mở rộng test `stat-card.test.tsx` cho prop `trend`.
