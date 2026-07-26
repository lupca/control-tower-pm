---
id: CTV2-037
task_path: projects/control-tower-v2/tasks/CTV2-037-taskdetail-dispatch.md
project: control-tower-v2
result_ref: b4fadd4
executor: "@gpt-5.6-luna-high"
reviewer: "@gpt-5.6-sol"
status: pending
issued: 2026-07-26
verdict: null
verdict_date: null
---

# Phiếu Review: CTV2-037 — Frontend: TaskDetail Dispatch + Run History

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-037-taskdetail-dispatch.md`
- Result-ref: b4fadd4
- Executor: @gpt-5.6-luna-high
- Reviewer: @gpt-5.6-sol
- Ngày phát phiếu: 2026-07-26

## Acceptance Criteria cần verify

- [ ] AC1: DispatchButton triggers real dispatch
- [ ] AC2: RunHistory shows all runs for task
- [ ] AC3: RunCard expandable với AgentOutputViewer
- [ ] AC4: Toast notifications cho success/error
- [ ] AC5: Cancel button works cho running tasks

## Definition of Done (AGENTS.md mục 3)

- [ ] Toàn bộ AC pass
- [ ] Test liên quan xanh 100%: Dispatch button triggers POST /api/dispatch, Run history loads from API, AgentOutputViewer embedded in RunCard, New run appears in history after dispatch
- [ ] Không regression (test khác trong module vẫn xanh)
- [ ] Reviewer khác executor (bạn đang review, hãy xác nhận bạn ≠ @gpt-5.6-luna-high)

## Test gợi ý chạy trong repo code

```bash
cd /home/lupca/projects/control-tower-v2
docker compose exec frontend npm test
docker compose exec backend pytest tests/
```

## Files to Review

- frontend/src/pages/TaskDetail.tsx
- frontend/src/components/task/DispatchButton.tsx
- frontend/src/components/task/RunHistory.tsx
- frontend/src/components/task/RunCard.tsx

## Review Toolchain

Chạy review theo repo's toolchain:
```bash
cat .claude/review-toolchain.md
```

## Trả kết quả

Sau khi review xong, báo lại cho control-tower bằng lệnh:
`/verdict CTV2-037 <pass|changes> --reviewer @gpt-5.6-sol [--commit <hash>] [--notes "..."]`
