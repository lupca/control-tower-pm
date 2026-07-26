---
id: CTV2-065
title: "Implement Headroom Compression for MCP Responses"
repo_root: /home/lupca/projects/control-tower-v2
status: completed
priority: high
risk: high
deadline: null
executor: "@claude-opus"
reviewer: "@antigravity"
result_ref: "96097f4"
depends_on: []
files:
  - backend/app/services/graph_client.py
  - backend/app/core/config.py
  - backend/requirements.txt
  - backend/tests/test_graph_client_compression.py
flows: []
tests:
  - backend/tests/test_graph_client_compression.py
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: high
prediction_factors:
  score: 1.0
  deductions: []
created: 2026-07-27
updated: 2026-07-27
rejections: 1
---

# CTV2-065: Implement Headroom Compression for MCP Responses

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Tiêu chí nghiệm thu (AC)
- [x] `headroom-ai` package added to requirements.txt
- [x] Config flag `HEADROOM_COMPRESSION_ENABLED` in config.py (default: False)
- [x] All 4 graph_client functions wrap output qua `headroom.compress()` khi enabled
- [x] Compression chỉ áp dụng cho responses > 1000 chars (skip short responses)
- [x] Unit tests verify: compressed output vẫn chứa đủ file paths, test names, flow names
- [x] Unit tests verify: compression ratio > 50% trên large JSON (100+ items)
- [x] Integration test: full gate flow với compression enabled vẫn pass

## Verification
- `pip install -r requirements.txt` → headroom-ai installed
- `HEADROOM_COMPRESSION_ENABLED=true pytest tests/test_graph_client_compression.py` → 100% pass
- `HEADROOM_COMPRESSION_ENABLED=false pytest` → existing tests still pass (no regression)

## Plan

### Phase 1: Setup
1. Add `headroom-ai` to `backend/requirements.txt`
2. Add `HEADROOM_COMPRESSION_ENABLED: bool = False` to `backend/app/core/config.py`

### Phase 2: Compression Wrapper
3. Create `compress_mcp_output(data: Any) -> Any` in `graph_client.py`:
   - Check `settings.HEADROOM_COMPRESSION_ENABLED`
   - Skip if data serialized < 1000 chars
   - Call `headroom.compress()` for JSON data
   - Return compressed or original based on config

### Phase 3: Integration
4. Wrap return values in all 4 functions:
   - `get_impact_radius()` → compress file list
   - `semantic_search()` → compress node list
   - `query_tests_for()` → compress test list
   - `get_affected_flows()` → compress flow list

### Phase 4: Testing (Critical)
5. Create `backend/tests/test_graph_client_compression.py`:
   - Test: compressed output still contains all original file paths
   - Test: compressed output still contains all test names
   - Test: compressed output still contains all flow names
   - Test: compression ratio > 50% on 100+ item lists
   - Test: short responses bypass compression
6. Integration test: run spec_gate with compression enabled, verify AC extraction still works

## Sub-tasks
- [x] Add headroom-ai to requirements.txt
- [x] Add HEADROOM_COMPRESSION_ENABLED config flag
- [x] Create compress_if_enabled() wrapper function
- [x] Wrap get_impact_radius() return with compression
- [x] Wrap semantic_search() return with compression
- [x] Wrap query_tests_for() return with compression
- [x] Wrap get_affected_flows() return with compression
- [x] Write unit tests for compression (data integrity + ratio)
- [x] Write integration test for gate flow with compression

## Findings từ reviewer
- [x] graph_client.py not modified
- [x] Pydantic config needs extra=ignore
- [x] Missing integration test
