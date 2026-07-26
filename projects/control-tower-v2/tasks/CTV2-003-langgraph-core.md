---
id: CTV2-003
title: "LangGraph Core - State + Nodes + Builder"
status: done
priority: high
risk: medium
deadline: 2026-08-10
executor: "@antigravity-3.6-high"
reviewer: "@antigravity"
result_ref: "f41e472"
depends_on:
  - CTV2-001
files:
  - backend/app/graph/state.py
  - backend/app/graph/nodes.py
  - backend/app/graph/builder.py
  - backend/app/graph/router.py
flows: []
tests:
  - backend/tests/test_graph_state.py
  - backend/tests/test_graph_nodes.py
dispatched: 2026-07-26
in_review: 2026-07-26
predicted_success: medium
prediction_factors:
  score: 0.7
  deductions:
    - "New framework (LangGraph) learning curve (-0.15)"
    - "Complex state management (-0.1)"
    - "Well-documented framework (+0.05)"
created: 2026-07-26
updated: 2026-07-26
---

# CTV2-003: LangGraph Core - State + Nodes + Builder

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Tiêu chí nghiệm thu (AC)

- [x] `TaskState` Pydantic model với tất cả fields
- [x] `GateType` enum: spec, plan, dispatch, review_order, verdict
- [x] Base node functions: `parse_input`, `sync_to_db`, `log_action`
- [x] Router function: route based on state, không cần LLM
- [x] `StateGraph` builder với nodes + edges
- [x] PostgresSaver checkpointer integration
- [x] Graph có thể compile và invoke với dummy state
- [x] Thread-based resume hoạt động

## State Schema

```python
from pydantic import BaseModel, Field
from typing import Literal
from enum import Enum
from datetime import datetime

class GateType(str, Enum):
    SPEC = "spec"
    PLAN = "plan"
    DISPATCH = "dispatch"
    REVIEW_ORDER = "review_order"
    VERDICT = "verdict"

class Mode(str, Enum):
    PLAN_ONLY = "plan-only"
    SUPERVISED = "supervised"
    BYPASS = "bypass"

class TaskState(BaseModel):
    # Input
    raw_input: str = ""
    
    # Task identity
    task_id: str | None = None
    project: str | None = None
    title: str | None = None
    
    # Workflow
    current_gate: GateType = GateType.SPEC
    status: Literal["todo", "dispatched", "in-review", "done", "changes-requested"] = "todo"
    mode: Mode = Mode.SUPERVISED
    
    # Gate outputs
    acceptance_criteria: list[str] = Field(default_factory=list)
    files: list[str] = Field(default_factory=list)
    tests: list[str] = Field(default_factory=list)
    plan: str | None = None
    
    # Actors
    executor: str | None = None
    reviewer: str | None = None
    
    # Review
    result_ref: str | None = None
    findings: list[str] = Field(default_factory=list)
    verdict: Literal["pass", "changes"] | None = None
    
    # Human-in-loop
    awaiting_approval: bool = False
    approval_prompt: str | None = None
    
    # Error
    error: str | None = None
```

## Graph Structure

```
START
  │
  ▼
parse_input ──▶ route_after_parse
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   spec_gate   (error)    (need_info)
        │
        ▼
   approval ──▶ route_after_approval
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   plan_gate   (rejected)  (waiting)
        │
        ▼
   ... (continue to dispatch, review, verdict)
        │
        ▼
   sync_to_db
        │
        ▼
   END
```

## Plan

1. Tạo `state.py` với Pydantic models
2. Tạo `nodes.py` với base node functions
3. Tạo `router.py` với routing logic (pure Python, no LLM)
4. Tạo `builder.py` với StateGraph construction
5. Setup PostgresSaver với connection string
6. Test compile + invoke với mock state
7. Test resume với thread_id

## Verification

```python
from app.graph.builder import build_graph

graph = build_graph()
config = {"configurable": {"thread_id": "test-1"}}

# First invoke
result = graph.invoke({"raw_input": "/pm test task"}, config)
assert result["task_id"] is not None

# Resume
result = graph.invoke(None, config)
```
