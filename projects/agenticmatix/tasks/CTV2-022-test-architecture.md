---
id: CTV2-022
title: "Test Architecture Setup"
status: done
priority: high
risk: low
executor: "@gemini-3.6-flash"
reviewer: "@gpt-5.6-sol"
deadline: 2026-07-28
created: 2026-07-26
files:
  - backend/tests/conftest.py
  - backend/tests/factories.py
  - frontend/vitest.config.ts
  - frontend/src/test/setup.ts
  - frontend/src/test/mocks/
  - docker-compose.test.yml
  - .env.test
  - pytest.ini
tests:
  - pytest runs with isolated test DB
  - vitest runs with MSW mocks
  - CI pipeline green
---

# CTV2-022: Test Architecture Setup

## Test Pyramid

```
        ╱╲
       ╱E2E╲         (10%) - Slow, expensive, critical paths only
      ╱──────╲
     ╱ Integr ╲      (20%) - API + DB, real HTTP calls
    ╱──────────╲
   ╱   Unit     ╲    (70%) - Fast, isolated, mock dependencies
  ╱──────────────╲
```

## Backend Test Stack (Python)

### Dependencies
```toml
# pyproject.toml [test]
pytest = "^8.0"
pytest-asyncio = "^0.23"
pytest-cov = "^4.1"
httpx = "^0.27"           # Async test client
factory-boy = "^3.3"      # Test fixtures
faker = "^24.0"           # Fake data
```

### Structure
```
backend/tests/
├── conftest.py           # Fixtures: test_db, test_client, factories
├── factories.py          # TaskFactory, ProjectFactory, AgentFactory
├── unit/
│   ├── test_state.py     # TaskState, GateType pure logic
│   ├── test_gates/       # Each gate in isolation (mocked deps)
│   └── test_services/    # AgentSelector, KnowledgeService
├── integration/
│   ├── test_api_tasks.py # Full HTTP → DB round-trip
│   ├── test_api_projects.py
│   └── test_graph_flow.py # LangGraph state transitions
└── fixtures/
    └── sample_data.json  # Seed data for integration tests
```

### Key Fixtures (conftest.py)
```python
@pytest.fixture(scope="session")
def test_db():
    """Isolated PostgreSQL for tests."""
    engine = create_engine(os.getenv("TEST_DATABASE_URL"))
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(test_db):
    """Transactional session - rollback after each test."""
    conn = test_db.connect()
    trans = conn.begin()
    session = Session(bind=conn)
    yield session
    session.close()
    trans.rollback()
    conn.close()

@pytest.fixture
def client(db_session):
    """Test client with dependency override."""
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as c:
        yield c
```

### Factory Pattern
```python
# factories.py
class TaskFactory(factory.Factory):
    class Meta:
        model = Task
    
    id = factory.Sequence(lambda n: f"T-{n:03d}")
    project = "test-project"
    title = factory.Faker("sentence")
    status = "todo"
    current_gate = "spec"

class ProjectFactory(factory.Factory):
    class Meta:
        model = Project
    
    id = factory.Sequence(lambda n: f"proj-{n}")
    name = factory.Faker("company")
    repo_root = "/tmp/test-repo"
```

## Frontend Test Stack (React)

### Dependencies
```json
{
  "devDependencies": {
    "vitest": "^2.0",
    "@testing-library/react": "^16.0",
    "@testing-library/user-event": "^14.5",
    "msw": "^2.3",
    "jsdom": "^24.0"
  }
}
```

### Structure
```
frontend/src/
├── test/
│   ├── setup.ts          # Vitest setup, MSW server
│   └── mocks/
│       ├── handlers.ts   # MSW request handlers
│       └── data.ts       # Mock response data
├── components/
│   └── __tests__/        # Component tests co-located
├── pages/
│   └── __tests__/
└── lib/
    └── __tests__/
```

### MSW Setup
```typescript
// test/mocks/handlers.ts
import { http, HttpResponse } from 'msw'

export const handlers = [
  http.get('/api/stats/overview', () => {
    return HttpResponse.json({
      total_tasks: 10,
      done_tasks: 3,
      active_tasks: 7,
      by_status: { todo: 5, dispatched: 2 }
    })
  }),
  
  http.get('/api/tasks', () => {
    return HttpResponse.json([
      { id: 'T-001', title: 'Test task', status: 'todo' }
    ])
  })
]

// test/setup.ts
import { setupServer } from 'msw/node'
import { handlers } from './mocks/handlers'

export const server = setupServer(...handlers)

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

### Vitest Config
```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      exclude: ['node_modules/', 'src/test/']
    },
    include: ['src/**/*.{test,spec}.{ts,tsx}']
  }
})
```

## Environment Separation

### docker-compose.test.yml
```yaml
services:
  db-test:
    image: postgres:16-alpine
    ports: ["5434:5432"]
    environment:
      POSTGRES_USER: ct_test
      POSTGRES_PASSWORD: test_secret
      POSTGRES_DB: control_tower_test
    tmpfs: /var/lib/postgresql/data  # RAM disk = fast
```

### .env.test
```bash
DATABASE_URL=postgresql://ct_test:test_secret@localhost:5434/control_tower_test
CT_ROOT=/tmp/ct-test-data
ENVIRONMENT=test
```

## Acceptance Criteria
- [ ] AC1: `conftest.py` với test_db, db_session, client fixtures
- [ ] AC2: `factories.py` với TaskFactory, ProjectFactory, AgentFactory
- [ ] AC3: Frontend `test/setup.ts` với MSW server
- [ ] AC4: `docker-compose.test.yml` cho isolated test DB
- [ ] AC5: `.env.test` với test environment variables
- [ ] AC6: `pytest.ini` và `vitest.config.ts` configured
- [ ] AC7: Sample test chạy pass: `pytest tests/unit/ -v`
- [ ] AC8: Sample test chạy pass: `npm test`
