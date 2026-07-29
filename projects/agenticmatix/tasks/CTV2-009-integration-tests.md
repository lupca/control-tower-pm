---
id: CTV2-009
title: "Integration Tests - Full Flow"
status: done
priority: high
risk: medium
deadline: 2026-08-22
executor: "@antigravity-3.6-high"
reviewer: "@antigravity"
result_ref: "f41e472"
depends_on:
  - CTV2-004
  - CTV2-008
files:
  - backend/tests/integration/test_full_flow.py
  - backend/tests/integration/test_gates_e2e.py
  - backend/tests/conftest.py
flows: []
tests:
  - backend/tests/integration/
dispatched: 2026-07-26
in_review: 2026-07-26
predicted_success: medium
prediction_factors:
  score: 0.7
  deductions:
    - "E2E tests complex (-0.15)"
    - "LLM mocking needed (-0.1)"
created: 2026-07-26
updated: 2026-07-26
---

# CTV2-009: Integration Tests - Full Flow

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Tiêu chí nghiệm thu (AC)

- [x] Test fixture: fresh DB per test
- [x] Test: create task → spec gate → plan gate → dispatch
- [x] Test: dispatch → review-order → verdict pass → done
- [x] Test: verdict changes → changes-requested → re-dispatch
- [x] Test: four-eyes violation blocked
- [x] Test: bypass mode skips approvals
- [x] Test: supervised mode pauses at gates
- [x] Mock LLM responses để tests deterministic
- [x] CI integration (GitHub Actions)
- [x] Coverage > 80%

## Test Scenarios

### Happy Path
```python
def test_full_flow_happy_path(graph, db):
    # Create task
    result = graph.invoke({"raw_input": "/pm add tests --project demo"})
    assert result["task_id"] == "DEMO-001"
    assert result["current_gate"] == "spec"
    
    # Approve spec
    result = graph.invoke({"approval": "approve"})
    assert result["current_gate"] == "plan"
    
    # Approve plan
    result = graph.invoke({"approval": "approve"})
    assert result["current_gate"] == "dispatch"
    
    # Dispatch
    result = graph.invoke({"executor": "@gemini-3.6"})
    assert result["status"] == "dispatched"
    
    # Simulate executor done
    db.update_task("DEMO-001", result_ref="abc123")
    
    # Review order
    result = graph.invoke({"raw_input": "/review-order DEMO-001"})
    assert result["status"] == "in-review"
    
    # Verdict pass
    result = graph.invoke({
        "verdict": "pass",
        "reviewer": "@antigravity"  # different from executor
    })
    assert result["status"] == "done"
```

### Four-Eyes Violation
```python
def test_four_eyes_blocked(graph):
    # Setup: task with executor @alice
    setup_task(executor="@alice")
    
    # Try verdict with same reviewer
    with pytest.raises(FourEyesViolation):
        graph.invoke({
            "verdict": "pass",
            "reviewer": "@alice"  # same as executor!
        })
```

### Mode Bypass
```python
def test_bypass_mode_no_approvals(graph):
    result = graph.invoke({
        "raw_input": "/pm quick fix --project demo",
        "mode": "bypass"
    })
    
    # Should go straight to dispatched without pausing
    assert result["status"] == "dispatched"
    assert result["awaiting_approval"] == False
```

## Fixtures

```python
@pytest.fixture
def db():
    """Fresh test database."""
    engine = create_engine("postgresql://ct:test@localhost/ct_test")
    Base.metadata.create_all(engine)
    yield Session(engine)
    Base.metadata.drop_all(engine)

@pytest.fixture
def graph(db):
    """LangGraph with mocked LLM."""
    with patch("app.services.claude.call") as mock:
        mock.return_value = {"acceptance_criteria": ["AC1", "AC2"]}
        yield build_graph(checkpointer=MemorySaver())

@pytest.fixture
def mock_llm():
    """Deterministic LLM responses."""
    return {
        "spec": {"acceptance_criteria": ["Test AC"], "risk": "low"},
        "plan": {"plan": "1. Do this\n2. Do that"}
    }
```

## Plan

1. Setup test database container
2. Create pytest fixtures
3. Implement happy path test
4. Implement error case tests
5. Add LLM mocking
6. Setup GitHub Actions workflow
7. Add coverage reporting

## Verification

```bash
# Run with test DB
docker-compose -f docker-compose.test.yml up -d db
pytest backend/tests/integration/ -v --cov=app --cov-report=html
# Check coverage > 80%
```
