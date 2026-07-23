---
id: CTW-009
title: "Agent Roster load dynamic data từ knowledge/agents/"
status: done
priority: high
risk: normal
deadline: null
executor: "@gpt-5.6-luna-high"
reviewer: "@claude-sonnet-high"
result_ref: "07dd19c"
depends_on: []
files:
  - src/components/AgentRoster.tsx
  - src/lib/data.ts
flows: []
tests: []
dispatched: 2026-07-23
in_review: 2026-07-24
predicted_success: high
prediction_factors:
  score: 0.85
  deductions:
    - "no_tests: -0.1"
    - "ui_component: -0.05"
rejections: 0
created: 2026-07-23
updated: 2026-07-23
---

# CTW-009: Agent Roster load dynamic data từ knowledge/agents/

> Dự án: [[projects/control-tower-web/control-tower-web]]

## Problem

Agent Roster & Performance Analytics đang hiển thị data cứng (hardcoded), tất cả agents đều giống nhau. Cần đọc data thực từ `control-tower/knowledge/agents/*.md`.

## Tiêu chí nghiệm thu (AC)

- [x] **AC1:** Agent Roster đọc tất cả file `knowledge/agents/@*.md` từ control-tower repo
- [x] **AC2:** Hiển thị đúng stats từ frontmatter: total_tasks_executed, total_tasks_reviewed, success_rate, strengths
- [x] **AC3:** Performance chart/metrics phản ánh data thực

## Plan

1. Update `loadControlTowerData()` in `src/lib/data.ts` to read agent files
2. Parse agent frontmatter (agent_id, type, stats, strengths)
3. Update AgentRoster component to use dynamic data
4. Test with real agent files
