---
id: CTV2-005
title: "MCP Integration - code-review-graph Client"
status: done
priority: medium
risk: medium
deadline: 2026-08-14
executor: "@antigravity-3.6-high"
reviewer: "@antigravity"
result_ref: "f41e472"
depends_on:
  - CTV2-003
files:
  - backend/app/services/mcp.py
  - backend/app/services/graph_client.py
flows: []
tests:
  - backend/tests/test_mcp.py
dispatched: 2026-07-26
in_review: 2026-07-26
predicted_success: medium
prediction_factors:
  score: 0.7
  deductions:
    - "MCP protocol complexity (-0.15)"
    - "Existing MCP server available (+0.1)"
    - "Network/subprocess handling (-0.1)"
created: 2026-07-26
updated: 2026-07-26
---

# CTV2-005: MCP Integration - code-review-graph Client

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Tiêu chí nghiệm thu (AC)

- [x] MCP client có thể connect tới code-review-graph server
- [x] Wrapper functions cho: `get_impact_radius`, `semantic_search`, `query_graph`
- [x] Async support (graph queries có thể slow)
- [x] Timeout handling (30s default)
- [x] Cache layer cho repeated queries (optional, TTL 5min)
- [x] Fallback: nếu MCP fail, return empty list (không block flow)

## MCP Tools cần wrap

```python
async def get_impact_radius(repo_root: str, file: str) -> list[str]:
    """Get files affected by changes to given file."""
    
async def semantic_search(repo_root: str, query: str, limit: int = 10) -> list[dict]:
    """Search nodes by semantic similarity."""
    
async def query_tests_for(repo_root: str, target: str) -> list[str]:
    """Find test files covering a target file/function."""
    
async def get_affected_flows(repo_root: str, files: list[str]) -> list[str]:
    """Get business flows affected by file changes."""
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│                LangGraph Node                   │
│                                                 │
│  async def query_graph_node(state):             │
│      client = MCPClient(repo_root)              │
│      files = await client.get_impact_radius()  │
│      return {"files": files}                   │
│                                                 │
└───────────────────────┬─────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│              MCPClient (subprocess)             │
│                                                 │
│  - Spawn code-review-graph process              │
│  - JSON-RPC over stdio                          │
│  - Connection pooling                           │
└─────────────────────────────────────────────────┘
```

## Plan

1. Research MCP client patterns (langchain-mcp-adapters hoặc raw subprocess)
2. Implement basic MCPClient class
3. Add timeout + retry logic
4. Wrap specific tools needed for gates
5. Add caching layer (in-memory hoặc Redis)
6. Test với real code-review-graph server

## Verification

```python
client = MCPClient(repo_root="/home/lupca/projects/topvnsport")
files = await client.get_impact_radius("src/App.tsx")
assert isinstance(files, list)
```
