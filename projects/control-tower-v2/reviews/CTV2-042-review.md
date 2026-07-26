---
id: CTV2-042
task_path: projects/control-tower-v2/tasks/CTV2-042-e2e-full-flow-test.md
project: control-tower-v2
result_ref: 2c69638
executor: "@gpt-5.6-luna-high"
reviewer: "@gpt-5.6-sol"
status: pending
issued: 2026-07-26
verdict: null
verdict_date: null
---

# Phiếu Review: CTV2-042 — E2E Full Flow Test

- Dự án: control-tower-v2 (`/home/lupca/projects/control-tower-v2`)
- Task gốc: `projects/control-tower-v2/tasks/CTV2-042-e2e-full-flow-test.md`
- Result-ref: 2c69638
- Executor: @gpt-5.6-luna-high
- Reviewer: @gpt-5.6-sol
- Ngày phát phiếu: 2026-07-26

## Acceptance Criteria cần verify

- [ ] AC1: Playwright config set up correctly
- [ ] AC2: E2E test creates task via UI
- [ ] AC3: E2E test dispatches and monitors SSE
- [ ] AC4: E2E test verifies completion
- [ ] AC5: Backend integration test covers full flow
- [ ] AC6: Tests can run in CI (headless)

## Files to Review

- e2e/full-flow.spec.ts
- e2e/playwright.config.ts
- backend/tests/integration/test_full_flow.py

## Test Commands

```bash
cd /home/lupca/projects/control-tower-v2
npx playwright test e2e/full-flow.spec.ts
docker compose exec backend pytest tests/integration/test_full_flow.py -v
```

## Trả kết quả

`/verdict CTV2-042 <pass|changes> --reviewer @gpt-5.6-sol [--commit <hash>] [--notes "..."]`
