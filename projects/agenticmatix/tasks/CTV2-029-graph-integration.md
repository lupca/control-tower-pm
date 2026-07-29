---
id: CTV2-029
title: "Code-review-graph integration"
status: done
priority: medium
risk: low
executor: "@gemini-3.6-flash"
reviewer: "@claude-opus"
deadline: 2026-07-31
created: 2026-07-26
depends_on: [CTV2-025]
files:
  - backend/app/services/graph_client.py
  - backend/app/api/projects.py
tests:
  - Build graph for project
  - Query affected flows
  - Update graph_status in DB
---

# CTV2-029: Code-Review-Graph Integration

## Context
V2 design có graph_status, embed_status trong projects table.
Cần integrate với code-review-graph MCP server.

## Features

### 1. Project Graph Status
```python
@router.post("/api/projects/{id}/build-graph")
def build_project_graph(id: str, db: Session):
    """
    Trigger code-review-graph build for project.
    Updates: graph_status, node_count, edge_count
    """
    project = get_project(id)
    result = graph_client.build_graph(project.repo_root)
    
    project.graph_status = "ready"
    project.node_count = result["nodes"]
    project.edge_count = result["edges"]
    db.commit()
```

### 2. Task File Analysis
```python
def analyze_task_files(task: Task) -> dict:
    """
    Use graph to:
    1. Find affected flows
    2. Identify high-coupling files
    3. Predict complexity/risk
    """
    return graph_client.get_affected_flows(
        repo_root=project.repo_root,
        files=task.files
    )
```

### 3. Spec Gate Enhancement
```python
# In spec gate, auto-populate files/flows from graph
if project.graph_status == "ready":
    context = graph_client.get_minimal_context(
        repo_root=project.repo_root,
        query=task.raw_input
    )
    task.files = context["files"]
    task.flows = context["flows"]
```

## Acceptance Criteria
- [ ] AC1: `/api/projects/{id}/build-graph` endpoint
- [ ] AC2: graph_status tracking in projects table
- [ ] AC3: Spec gate uses graph for file discovery
- [ ] AC4: Plan gate uses graph for impact analysis
- [ ] AC5: Dashboard shows graph status per project
