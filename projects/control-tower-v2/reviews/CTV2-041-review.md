---
id: CTV2-041
task_path: projects/control-tower-v2/tasks/CTV2-041-dashboard-projects-fix.md
project: control-tower-v2
result_ref: 1b0209a
executor: "@gpt-5.6-luna-high"
reviewer: "@gpt-5.6-sol"
status: pending
issued: 2026-07-26
verdict: null
verdict_date: null
---

# Phiếu Review: CTV2-041 — Fix Dashboard Project Progress section

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-041-dashboard-projects-fix.md`
- Result-ref: 1b0209a
- Executor: @gpt-5.6-luna-high
- Reviewer: @gpt-5.6-sol
- Ngày phát phiếu: 2026-07-26

## Acceptance Criteria cần verify

- [ ] AC1: Dashboard shows project cards with completion rates
- [ ] AC2: At least top 5 projects displayed
- [ ] AC3: Clicking project card navigates to project detail

## Definition of Done (AGENTS.md mục 3)

- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: Dashboard Project Progress shows real projects, API returns projectProgress array
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (bạn đang review, hãy xác nhận bạn ≠ @gpt-5.6-luna-high)

## Test gợi ý chạy trong repo code

```bash
cd /home/lupca/projects/control-tower-v2
docker compose exec frontend npm test
docker compose exec backend pytest tests/
```

## Files to Review

- frontend/src/pages/Dashboard.tsx
- frontend/src/components/dashboard/ProjectCards.tsx
- backend/app/api/stats.py

## Review Toolchain

Chạy review theo repo's toolchain:
```bash
cat .claude/review-toolchain.md
```

## Trả kết quả

Sau khi review xong, báo lại cho control-tower bằng lệnh:
`/verdict CTV2-041 <pass|changes> --reviewer @gpt-5.6-sol [--commit <hash>] [--notes "..."]`
