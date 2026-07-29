---
id: CTV2-127
title: "Migrate Alert Banners and Modals"
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
  - frontend/src/components/ui/alert-banner.tsx
  - frontend/src/components/ui/modal.tsx
  - frontend/src/pages/Dashboard.tsx
  - frontend/src/pages/Agents.tsx
  - frontend/src/pages/Projects.tsx
  - frontend/src/pages/AgentDetail.tsx
  - frontend/src/pages/ProjectDetail.tsx
  - frontend/src/components/projects/ProjectSettingsModal.tsx
flows: []
tests:
  - frontend/src/components/ui/__tests__/stat-card.test.tsx
predicted_success: high
prediction_factors:
  score: 0.8
  deductions:
    - "touches hub nodes Dashboard/AgentsPage/ProjectsPage/AgentDetailPage/ProjectDetailPage (-0.2)"
created: 2026-07-28
updated: 2026-07-28
---

# CTV2-127: Migrate Alert Banners and Modals

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

Phase 4/5 của [[CTV2-118-research-frontend-refactor-strategy]] — nguồn: `docs/research/frontend-refactor-strategy.md` §Duplicated Patterns (Error Alert Banner 6 occurrences, Modal wrapper 3 occurrences) + §Inconsistent Error Handling (khuyến nghị `useDataFetch` hook pattern). Phụ thuộc [[CTV2-119-shadcn-ui-core-primitives]] (định nghĩa `AlertBanner`) và [[CTV2-124]]/[[CTV2-125]] (page đã tách xong mới migrate banner bên trong).

## Tiêu chí nghiệm thu (AC)

- [ ] Tạo `components/ui/modal.tsx` bọc Radix Dialog (mới), thay cho markup modal lặp lại (`fixed inset-0 z-50 bg-black/70 backdrop-blur-sm`) ở `Agents.tsx`, `Projects.tsx`, `ProjectSettingsModal.tsx`.
- [ ] Tất cả banner lỗi hiện có ở `Dashboard.tsx`, `Agents.tsx`, `Projects.tsx`, `AgentDetail.tsx`, `ProjectDetail.tsx` (bao gồm các banner mới thêm ở CTV2-120) dùng chung `<AlertBanner severity="error">` từ `components/ui/alert-banner.tsx`.
- [ ] Không còn markup modal/banner Tailwind trùng lặp ở các file trên (grep xác nhận).
- [ ] Modal giữ đúng hành vi đóng/mở, focus trap (Radix Dialog mặc định cung cấp) — không regress so với modal cũ.

## Verification
- `npm test -- Agents Projects` → pass (test modal mở/đóng nếu có)
- `grep -rn "fixed inset-0 z-50 bg-black/70 backdrop-blur-sm" frontend/src` → chỉ còn trong `modal.tsx`
- `grep -rn "bg-amber-500/10 border border-amber-500/30" frontend/src` → chỉ còn trong `alert-banner.tsx`

## Plan
1. Tạo `components/ui/modal.tsx` wrap Radix `Dialog`.
2. Migrate `Agents.tsx`/`Projects.tsx`/`ProjectSettingsModal.tsx` sang `<Modal>` mới.
3. Migrate toàn bộ banner lỗi (bao gồm banner mới từ CTV2-120) sang `<AlertBanner>`.
4. Kiểm tra hành vi đóng/mở modal không regress.
