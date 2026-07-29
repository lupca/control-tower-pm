---
id: CTV2-207
title: "Add sequence-based output streaming with replay"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: high
risk: normal
deadline: null
executor: "@gpt-5.6-luna"
reviewer: "@claude-sonnet-medium"
result_ref: "28f33f5..e378d31"
depends_on: []
files:
  - backend/app/db/models.py
  - backend/app/api/stream.py
  - frontend/src/lib/sse/
flows: []
tests:
  - backend/tests/integration/test_full_flow.py
dispatched: 2026-07-29
in_review: null
predicted_success: high
prediction_factors:
  score: 0.7
  deductions:
    - "frontend: SSE reconnect logic (-0.2)"
    - "api: new endpoint (-0.1)"
confidence_interval: [0.6, 0.8]
created: 2026-07-29
updated: 2026-07-29
---

# CTV2-207: Add sequence-based output streaming with replay

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Context

Redis PubSub loses messages on disconnect. AgentOutputChunk exists but frontend can't replay from a sequence number on reconnect.

## Tiêu chí nghiệm thu (AC)

- [ ] Ensure AgentOutputChunk.chunk_index is strictly sequential per run
- [ ] Add GET /api/runs/{run_id}/output?after_seq={n} endpoint for replay
- [ ] Update SSE streaming to include seq in each chunk event
- [ ] Frontend: on reconnect, fetch missed chunks via REST then resume SSE
- [ ] Consider batching chunks (4-16KB) to reduce PostgreSQL write pressure

## Verification

- `pytest backend/tests/integration/test_full_flow.py -v` → 100% pass
- Manual: disconnect/reconnect during streaming, verify no lost chunks

## Plan

*(filled in at Plan Gate)*

## Sub-tasks

- [ ] Add replay endpoint
- [ ] Update SSE to include seq
- [ ] Update frontend reconnect logic
- [ ] Add chunk batching (optional)
- [ ] Add tests
