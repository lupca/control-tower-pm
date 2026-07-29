---
id: CTV2-028
title: "E2E Tests (Playwright)"
status: done
priority: medium
risk: low
executor: "@gemini-3.6-flash"
reviewer: "@gpt-5.6-sol"
deadline: 2026-07-31
created: 2026-07-26
depends_on: [CTV2-022, CTV2-021]
files:
  - e2e/
  - playwright.config.ts
tests:
  - npx playwright test passes
  - Critical user flows covered
---

# CTV2-028: E2E Tests (Playwright)

## Setup

### playwright.config.ts
```typescript
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [['html'], ['list']],
  
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],

  webServer: {
    command: 'docker compose up -d',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
})
```

## Page Object Model

### Structure
```
e2e/
├── pages/
│   ├── BasePage.ts
│   ├── DashboardPage.ts
│   ├── TasksPage.ts
│   ├── KanbanPage.ts
│   └── TaskDetailPage.ts
├── fixtures/
│   └── test-data.ts
├── dashboard.spec.ts
├── tasks.spec.ts
├── kanban.spec.ts
└── task-chat.spec.ts
```

### BasePage.ts
```typescript
import { Page, Locator } from '@playwright/test'

export class BasePage {
  constructor(protected page: Page) {}

  async navigate(path: string) {
    await this.page.goto(path)
    await this.page.waitForLoadState('networkidle')
  }

  async waitForApi(endpoint: string) {
    await this.page.waitForResponse(
      resp => resp.url().includes(endpoint) && resp.status() === 200
    )
  }

  get nav() {
    return {
      dashboard: this.page.getByRole('link', { name: 'Dashboard' }),
      tasks: this.page.getByRole('link', { name: 'Tasks' }),
      kanban: this.page.getByRole('link', { name: 'Kanban' }),
      projects: this.page.getByRole('link', { name: 'Projects' }),
    }
  }
}
```

### DashboardPage.ts
```typescript
import { BasePage } from './BasePage'

export class DashboardPage extends BasePage {
  async goto() {
    await this.navigate('/')
    await this.waitForApi('/api/stats/overview')
  }

  get statsCards() {
    return {
      total: this.page.locator('[data-testid="stat-total"]'),
      active: this.page.locator('[data-testid="stat-active"]'),
      done: this.page.locator('[data-testid="stat-done"]'),
    }
  }

  get recentTasks() {
    return this.page.locator('[data-testid="recent-tasks"] li')
  }

  async clickTask(id: string) {
    await this.page.getByText(id).click()
  }
}
```

### TasksPage.ts
```typescript
export class TasksPage extends BasePage {
  async goto() {
    await this.navigate('/tasks')
    await this.waitForApi('/api/tasks')
  }

  get table() {
    return this.page.locator('table')
  }

  get rows() {
    return this.page.locator('table tbody tr')
  }

  async filterByStatus(status: string) {
    await this.page.getByRole('combobox', { name: 'Status' }).selectOption(status)
    await this.waitForApi('/api/tasks')
  }

  async clickRow(taskId: string) {
    await this.page.getByRole('row', { name: new RegExp(taskId) }).click()
  }
}
```

## Test Specs

### dashboard.spec.ts
```typescript
import { test, expect } from '@playwright/test'
import { DashboardPage } from './pages/DashboardPage'

test.describe('Dashboard', () => {
  let dashboard: DashboardPage

  test.beforeEach(async ({ page }) => {
    dashboard = new DashboardPage(page)
    await dashboard.goto()
  })

  test('displays stats cards', async () => {
    await expect(dashboard.statsCards.total).toBeVisible()
    await expect(dashboard.statsCards.active).toBeVisible()
    await expect(dashboard.statsCards.done).toBeVisible()
  })

  test('shows recent tasks', async () => {
    await expect(dashboard.recentTasks).toHaveCount.greaterThan(0)
  })

  test('navigates to task detail', async ({ page }) => {
    const firstTaskId = await dashboard.recentTasks.first().textContent()
    await dashboard.recentTasks.first().click()
    await expect(page).toHaveURL(/\/task\//)
  })
})
```

### tasks.spec.ts
```typescript
test.describe('Tasks Table', () => {
  let tasks: TasksPage

  test.beforeEach(async ({ page }) => {
    tasks = new TasksPage(page)
    await tasks.goto()
  })

  test('displays task table', async () => {
    await expect(tasks.table).toBeVisible()
    await expect(tasks.rows).toHaveCount.greaterThan(0)
  })

  test('filters by status', async () => {
    const initialCount = await tasks.rows.count()
    await tasks.filterByStatus('done')
    
    // Should have fewer or equal rows
    const filteredCount = await tasks.rows.count()
    expect(filteredCount).toBeLessThanOrEqual(initialCount)
  })

  test('navigates to detail on row click', async ({ page }) => {
    await tasks.clickRow('T-001')
    await expect(page).toHaveURL('/task/T-001')
  })
})
```

### kanban.spec.ts
```typescript
test.describe('Kanban Board', () => {
  test('displays columns by status', async ({ page }) => {
    await page.goto('/kanban')
    
    await expect(page.locator('[data-status="todo"]')).toBeVisible()
    await expect(page.locator('[data-status="dispatched"]')).toBeVisible()
    await expect(page.locator('[data-status="in-review"]')).toBeVisible()
    await expect(page.locator('[data-status="done"]')).toBeVisible()
  })

  test('drag and drop changes status', async ({ page }) => {
    await page.goto('/kanban')
    
    const card = page.locator('[data-task-id="T-001"]')
    const targetColumn = page.locator('[data-status="dispatched"]')
    
    await card.dragTo(targetColumn)
    
    // Verify API call was made
    const response = await page.waitForResponse('/api/tasks/T-001')
    expect(response.status()).toBe(200)
    
    // Verify card is in new column
    await expect(targetColumn.locator('[data-task-id="T-001"]')).toBeVisible()
  })
})
```

### task-chat.spec.ts
```typescript
test.describe('Task Detail + Chat', () => {
  test('displays task info and chat panel', async ({ page }) => {
    await page.goto('/task/T-001')
    
    // Task info visible
    await expect(page.getByTestId('task-title')).toBeVisible()
    await expect(page.getByTestId('task-status')).toBeVisible()
    await expect(page.getByTestId('task-ac-list')).toBeVisible()
    
    // Chat panel visible
    await expect(page.getByTestId('chat-panel')).toBeVisible()
  })

  test('sends chat message', async ({ page }) => {
    await page.goto('/task/T-001')
    
    const input = page.getByPlaceholder('Type a message...')
    await input.fill('Hello from E2E test')
    await input.press('Enter')
    
    // Message appears in chat
    await expect(page.getByText('Hello from E2E test')).toBeVisible()
  })
})
```

## Critical User Flows

| Flow | Steps | Verified |
|------|-------|----------|
| Dashboard → Task | Dashboard loads → click task → detail page | Stats, navigation |
| Filter Tasks | Tasks page → select status → table updates | API filtering |
| Kanban Drag | Kanban → drag card → status changes | State mutation |
| Task Chat | Task detail → send message → response | SSE streaming |
| Project Drill | Projects → click → tasks list | Nested navigation |

## Acceptance Criteria
- [ ] AC1: Playwright configured với Page Object Model
- [ ] AC2: Dashboard tests (stats, recent tasks, navigation)
- [ ] AC3: Tasks table tests (filter, sort, row click)
- [ ] AC4: Kanban tests (columns, drag-drop)
- [ ] AC5: Task detail + chat tests
- [ ] AC6: All tests run against Docker stack
- [ ] AC7: Screenshots on failure
- [ ] AC8: HTML report generated
