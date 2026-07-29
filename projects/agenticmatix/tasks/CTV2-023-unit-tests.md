---
id: CTV2-023
title: "Unit Tests (Backend + Frontend)"
status: done
priority: high
risk: low
executor: "@gemini-3.6-flash"
reviewer: "@gpt-5.6-sol"
deadline: 2026-07-29
created: 2026-07-26
depends_on: [CTV2-022]
files:
  - backend/tests/unit/
  - frontend/src/**/__tests__/
tests:
  - pytest tests/unit/ passes
  - npm test passes
  - Coverage > 70%
---

# CTV2-023: Unit Tests

## Backend Unit Tests

### 1. State & Models (`tests/unit/test_state.py`)
```python
def test_task_state_default_values():
    state = TaskState()
    assert state.current_gate == GateType.SPEC
    assert state.status == "todo"
    assert state.mode == Mode.SUPERVISED

def test_four_eyes_violation():
    with pytest.raises(FourEyesViolation):
        task = TaskFactory(executor="@alice", reviewer="@alice")
```

### 2. Gates (`tests/unit/test_gates/`)

#### test_spec_gate.py
```python
@pytest.fixture
def spec_gate(mocker):
    """Gate with mocked LLM."""
    llm = mocker.Mock()
    llm.generate.return_value = {
        "acceptance_criteria": ["AC1", "AC2"],
        "files": ["src/main.py"],
        "tests": ["test passes"]
    }
    return SpecGate(llm=llm)

def test_spec_gate_extracts_ac(spec_gate):
    state = TaskState(raw_input="Add login feature")
    result = spec_gate.process(state)
    assert len(result.acceptance_criteria) == 2
    assert result.current_gate == GateType.PLAN

def test_spec_gate_rejects_empty_input(spec_gate):
    state = TaskState(raw_input="")
    with pytest.raises(SpecGateError):
        spec_gate.process(state)
```

#### test_dispatch_gate.py
```python
def test_dispatch_requires_executor():
    state = TaskState(executor=None)
    gate = DispatchGate()
    with pytest.raises(DispatchGateError):
        gate.process(state)

def test_dispatch_sets_status_and_timestamp():
    state = TaskState(executor="@alice")
    result = DispatchGate().process(state)
    assert result.status == "dispatched"
    assert result.dispatched_at is not None
```

#### test_verdict_gate.py
```python
def test_verdict_pass_closes_task():
    state = TaskState(executor="@alice", reviewer="@bob", verdict="pass")
    result = VerdictGate().process(state)
    assert result.status == "done"

def test_verdict_rejects_same_reviewer():
    state = TaskState(executor="@alice", reviewer="@alice")
    with pytest.raises(FourEyesViolation):
        VerdictGate().process(state)
```

### 3. Services (`tests/unit/test_services/`)

#### test_agent_selector.py
```python
def test_selector_prefers_high_success_rate():
    agents = [
        AgentFactory(id="@fast", success_rate=0.6),
        AgentFactory(id="@reliable", success_rate=0.95)
    ]
    task = TaskFactory(risk="high")
    selected = AgentSelector().select(task, agents)
    assert selected.id == "@reliable"

def test_selector_matches_tier_to_risk():
    agents = [
        AgentFactory(id="@expensive", effort="high"),
        AgentFactory(id="@cheap", effort="low", success_rate=0.9)
    ]
    task = TaskFactory(risk="low")
    selected = AgentSelector().select(task, agents)
    assert selected.id == "@cheap"
```

## Frontend Unit Tests

### 1. Components (`src/components/__tests__/`)

#### TaskCard.test.tsx
```typescript
import { render, screen } from '@testing-library/react'
import { TaskCard } from '../TaskCard'

describe('TaskCard', () => {
  it('renders task title', () => {
    render(<TaskCard task={{ id: 'T-001', title: 'Fix bug', status: 'todo' }} />)
    expect(screen.getByText('Fix bug')).toBeInTheDocument()
  })

  it('shows status badge', () => {
    render(<TaskCard task={{ id: 'T-001', title: 'Test', status: 'dispatched' }} />)
    expect(screen.getByText('dispatched')).toHaveClass('bg-yellow-500')
  })
})
```

### 2. Hooks (`src/lib/__tests__/`)

#### useStore.test.ts
```typescript
import { renderHook, act } from '@testing-library/react'
import { useStore } from '../store'

describe('useStore', () => {
  it('toggles dark mode', () => {
    const { result } = renderHook(() => useStore())
    expect(result.current.darkMode).toBe(true)
    
    act(() => result.current.toggleDarkMode())
    expect(result.current.darkMode).toBe(false)
  })
})
```

### 3. API Client (`src/lib/__tests__/api.test.ts`)
```typescript
import { api, ApiError } from '../api'
import { server } from '../../test/setup'
import { http, HttpResponse } from 'msw'

describe('api client', () => {
  it('fetches tasks', async () => {
    const tasks = await api.get('/tasks')
    expect(tasks).toHaveLength(1)
    expect(tasks[0].id).toBe('T-001')
  })

  it('throws ApiError on 404', async () => {
    server.use(
      http.get('/api/tasks', () => HttpResponse.json({ detail: 'Not found' }, { status: 404 }))
    )
    await expect(api.get('/tasks')).rejects.toThrow(ApiError)
  })
})
```

## Coverage Requirements

| Layer | Target | Critical Paths |
|-------|--------|----------------|
| Backend Unit | 70% | Gates, State, Services |
| Frontend Unit | 60% | Components, Hooks, API |

## Acceptance Criteria
- [ ] AC1: All gate tests pass
- [ ] AC2: State/model tests with edge cases
- [ ] AC3: Service tests với mocked dependencies
- [ ] AC4: Component tests với React Testing Library
- [ ] AC5: Hook tests với renderHook
- [ ] AC6: API client tests với MSW
- [ ] AC7: `pytest tests/unit/ --cov` shows 70%+
- [ ] AC8: `npm test -- --coverage` shows 60%+
