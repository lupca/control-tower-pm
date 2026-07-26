---
id: CTV2-024
title: "Integration Tests (API + LangGraph)"
status: done
priority: high
risk: medium
executor: "@gemini-3.6-high"
reviewer: "@gpt-5.6-sol"
deadline: 2026-07-30
created: 2026-07-26
depends_on: [CTV2-022, CTV2-021]
files:
  - backend/tests/integration/
tests:
  - pytest tests/integration/ passes
  - Full gate flow works
  - API CRUD verified
---

# CTV2-024: Integration Tests

## Scope
Test full round-trip: HTTP → API → Service → DB → Response

## Test Structure

```
backend/tests/integration/
├── test_api_tasks.py        # CRUD + status transitions
├── test_api_projects.py     # Projects CRUD + stats
├── test_api_agents.py       # Agents CRUD + performance
├── test_api_stats.py        # Aggregation endpoints
├── test_graph_flow.py       # LangGraph state machine
└── test_four_eyes.py        # Constraint enforcement
```

## API Integration Tests

### test_api_tasks.py
```python
def test_create_task(client, db_session):
    response = client.post("/api/tasks", json={
        "id": "T-INT-001",
        "project": "test",
        "title": "Integration test task"
    })
    assert response.status_code == 201
    
    # Verify in DB
    task = db_session.query(Task).filter_by(id="T-INT-001").first()
    assert task is not None
    assert task.status == "todo"
    assert task.current_gate == "spec"

def test_update_task_status(client, db_session):
    # Create task
    TaskFactory.create(id="T-INT-002", session=db_session)
    db_session.commit()
    
    # Update
    response = client.patch("/api/tasks/T-INT-002", json={
        "status": "dispatched",
        "executor": "@alice"
    })
    assert response.status_code == 200
    
    # Verify timestamps
    task = response.json()
    assert task["dispatched_at"] is not None

def test_list_tasks_with_filters(client, db_session):
    TaskFactory.create_batch(5, status="todo", session=db_session)
    TaskFactory.create_batch(3, status="done", session=db_session)
    db_session.commit()
    
    response = client.get("/api/tasks?status=todo")
    assert len(response.json()) == 5

def test_delete_task_cascades_sessions(client, db_session):
    task = TaskFactory.create(id="T-DEL", session=db_session)
    SessionFactory.create(task_id="T-DEL", session=db_session)
    db_session.commit()
    
    response = client.delete("/api/tasks/T-DEL")
    assert response.status_code == 204
    
    # Session should be deleted too
    assert db_session.query(Session).filter_by(task_id="T-DEL").count() == 0
```

### test_api_stats.py
```python
def test_stats_overview_aggregation(client, db_session):
    TaskFactory.create_batch(3, status="todo", session=db_session)
    TaskFactory.create_batch(2, status="done", session=db_session)
    TaskFactory.create(status="dispatched", session=db_session)
    db_session.commit()
    
    response = client.get("/api/stats/overview")
    data = response.json()
    
    assert data["total_tasks"] == 6
    assert data["done_tasks"] == 2
    assert data["active_tasks"] == 4
    assert data["by_status"]["todo"] == 3

def test_stats_by_project(client, db_session):
    TaskFactory.create_batch(2, project="proj-a", session=db_session)
    TaskFactory.create_batch(3, project="proj-b", session=db_session)
    db_session.commit()
    
    response = client.get("/api/stats/projects")
    data = response.json()
    
    proj_a = next(p for p in data if p["project_id"] == "proj-a")
    assert proj_a["total_tasks"] == 2
```

## LangGraph Integration Tests

### test_graph_flow.py
```python
@pytest.fixture
def graph_runner(db_session):
    """Initialize LangGraph with test DB."""
    from app.graph.builder import build_graph
    return build_graph(checkpointer=SqlCheckpointer(db_session))

def test_full_task_lifecycle(graph_runner, db_session):
    """Test complete flow: spec → plan → dispatch → review → verdict"""
    
    # 1. Spec Gate
    state = graph_runner.invoke({
        "raw_input": "Add user authentication",
        "project": "test-proj"
    })
    assert state["current_gate"] == "plan"
    assert len(state["acceptance_criteria"]) > 0
    
    # 2. Plan Gate (in supervised mode, requires approval)
    assert state["awaiting_approval"] == True
    
    # 3. Simulate approval
    state = graph_runner.invoke({
        **state,
        "awaiting_approval": False,
        "executor": "@alice"
    })
    assert state["current_gate"] == "dispatch"
    
    # 4. Dispatch Gate
    state = graph_runner.invoke(state)
    assert state["status"] == "dispatched"
    assert state["dispatched_at"] is not None
    
    # 5. Review Order Gate
    state = graph_runner.invoke({
        **state,
        "result_ref": "PR#123",
        "reviewer": "@bob"
    })
    assert state["current_gate"] == "verdict"
    
    # 6. Verdict Gate
    state = graph_runner.invoke({
        **state,
        "verdict": "pass",
        "findings": []
    })
    assert state["status"] == "done"
    assert state["completed_at"] is not None

def test_changes_requested_loop(graph_runner):
    """Test verdict=changes loops back correctly."""
    state = TaskState(
        current_gate=GateType.VERDICT,
        executor="@alice",
        reviewer="@bob",
        verdict="changes",
        findings=["Bug in line 42"]
    )
    
    result = graph_runner.invoke(state.dict())
    assert result["status"] == "changes-requested"
    assert result["current_gate"] == "dispatch"  # Back to executor
```

### test_four_eyes.py
```python
def test_db_constraint_blocks_same_actor(db_session):
    """Four-eyes enforced at DB level."""
    task = Task(
        id="T-4E-001",
        project="test",
        title="Test",
        executor="@alice",
        reviewer="@alice"  # Violation!
    )
    db_session.add(task)
    
    with pytest.raises(IntegrityError):
        db_session.commit()

def test_api_rejects_same_actor(client):
    """Four-eyes enforced at API level."""
    response = client.post("/api/tasks", json={
        "id": "T-4E-002",
        "project": "test",
        "title": "Test",
        "executor": "@alice",
        "reviewer": "@alice"
    })
    assert response.status_code == 422
    assert "four-eyes" in response.json()["detail"].lower()

def test_verdict_gate_rejects_same_actor(graph_runner):
    """Four-eyes enforced at gate level."""
    state = TaskState(
        current_gate=GateType.VERDICT,
        executor="@alice",
        reviewer="@alice",
        verdict="pass"
    )
    
    with pytest.raises(FourEyesViolation):
        graph_runner.invoke(state.dict())
```

## Acceptance Criteria
- [ ] AC1: CRUD tests cho tasks, projects, agents APIs
- [ ] AC2: Stats aggregation tests
- [ ] AC3: Full LangGraph flow test (spec → done)
- [ ] AC4: Changes-requested loop test
- [ ] AC5: Four-eyes constraint tests (DB + API + Gate levels)
- [ ] AC6: Cascade delete tests
- [ ] AC7: Filter/pagination tests
- [ ] AC8: All tests use isolated test DB (no prod data)
