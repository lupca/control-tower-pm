---
id: CTV2-042
title: "E2E Test: Full Task Flow (Create → Dispatch → Complete)"
status: todo
priority: high
risk: medium
deadline: 2026-07-30
executor:
depends_on: [CTV2-043]
reviewer:
files:
  - e2e/full-flow.spec.ts
  - e2e/playwright.config.ts
  - backend/tests/integration/test_full_flow.py
tests:
  - Playwright E2E test passes
  - Backend integration test passes
  - Flow works in real browser
created: 2026-07-26
effort: 6h
---

# CTV2-042: E2E Full Task Flow Test

## Scope

Automated test cho complete task lifecycle:
1. Create task via /pm command
2. Dispatch to agent
3. Monitor agent output (SSE)
4. Complete/verdict
5. Verify final state

## Components

### 1. Playwright E2E (Frontend)

```typescript
// e2e/full-flow.spec.ts
test('complete task flow', async ({ page }) => {
  // 1. Go to tasks page
  await page.goto('/tasks');
  
  // 2. Open task detail
  await page.click('text=CT-001');
  
  // 3. Click dispatch
  await page.click('button:has-text("Dispatch")');
  
  // 4. Wait for status change
  await expect(page.locator('.status-badge')).toHaveText('dispatched');
  
  // 5. Verify SSE output appears
  await expect(page.locator('.agent-output')).toBeVisible();
  
  // 6. Wait for completion (or timeout)
  await expect(page.locator('.status-badge')).toHaveText('done', { timeout: 60000 });
});
```

### 2. Backend Integration Test

```python
# backend/tests/integration/test_full_flow.py
def test_create_dispatch_complete_flow():
    # 1. Create task via /pm
    response = client.post("/api/chat", json={
        "message": "/pm Test E2E task --project test"
    })
    task_id = extract_task_id(response)
    
    # 2. Dispatch
    response = client.post("/api/dispatch", json={
        "task_id": task_id,
        "agent_id": "@test-agent"
    })
    run_id = response.json()["run_id"]
    
    # 3. Poll for completion
    while True:
        status = client.get(f"/api/runs/{run_id}").json()["status"]
        if status in ["success", "failed"]:
            break
        time.sleep(1)
    
    # 4. Verdict
    response = client.post("/api/chat", json={
        "message": f"/verdict {task_id} pass"
    })
    
    # 5. Verify done
    task = client.get(f"/api/tasks/{task_id}").json()
    assert task["status"] == "done"
```

## AC

- [ ] AC1: Playwright config set up correctly
- [ ] AC2: E2E test creates task via UI
- [ ] AC3: E2E test dispatches and monitors SSE
- [ ] AC4: E2E test verifies completion
- [ ] AC5: Backend integration test covers full flow
- [ ] AC6: Tests can run in CI (headless)

## Dependencies

- CTV2-036 (Agent Output Viewer) - for SSE monitoring
- CTV2-037 (TaskDetail Dispatch) - for dispatch button
