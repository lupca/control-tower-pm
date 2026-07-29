---
id: CTV2-118
title: "Research: Frontend Refactor Strategy - Splitting, Performance, Cleanup, Reusable Components"
repo_root: /home/lupca/projects/control-tower-v2
status: done
priority: normal
risk: normal
deadline: null
executor: "@claude-opus"
reviewer: null
result_ref: f5f242e2d278ef35ee860bd65281705fa13b73da
depends_on: []
files:
  - frontend/src/components/chat/ChatPanel.tsx
  - frontend/src/pages/ProjectDetail.tsx
  - frontend/src/components/tasks/TaskTable.tsx
  - frontend/src/pages/Dashboard.tsx
  - frontend/src/pages/AgentDetail.tsx
  - frontend/src/pages/Agents.tsx
  - frontend/src/pages/Projects.tsx
  - frontend/src/components/task/TaskSpec.tsx
flows: []
tests: []
dispatched: 2026-07-28
in_review: null
predicted_success: high
prediction_factors:
  score: 0.9
  deductions:
    - "research task, no code changes (-0.0)"
    - "no existing tests for the audited pages/components — AgentsPage, AgentDetailPage, Dashboard, ProjectsPage, ProjectDetailPage, ChatPanel are untested hotspots per get_knowledge_gaps_tool (-0.1)"
confidence_interval: [0.75, 0.95]
created: 2026-07-28
updated: 2026-07-28
---

# CTV2-118: Research: Frontend Refactor Strategy - Splitting, Performance, Cleanup, Reusable Components

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Tiêu chí nghiệm thu (AC)

- [ ] Audit the frontend (`frontend/src/`) and list every page/component over ~250 lines as a splitting candidate, starting from the graph-confirmed hotspots: `ChatPanel.tsx` (546 lines), `ProjectDetail.tsx` (403), `TaskTable.tsx` (391), `Dashboard.tsx` (372), `AgentDetail.tsx` (368), `Agents.tsx` (329), `Projects.tsx` (346), `TaskSpec.tsx` (298) — for each, propose a concrete sub-component split (name + responsibility).
- [ ] Identify performance issues in these files: missing memoization (`useMemo`/`useCallback`/`React.memo`), avoidable re-renders, N+1-style sequential API calls (e.g. `ProjectDetail.tsx` fetching tasks after project load), unbounded lists without virtualization — list each with file:line and the concrete fix.
- [ ] Identify dead code / code smells: duplicated JSX/logic across pages (e.g. repeated stat-card/table patterns across `Agents.tsx`, `Projects.tsx`, `Dashboard.tsx`), inconsistent error handling (silently-swallowed try/catch in `ProjectDetail.tsx`/`Dashboard.tsx` per OCR pre-scan below), unused props/state — list each with file:line.
- [ ] Evaluate component-reuse strategy and give ONE explicit recommendation with tradeoffs: (a) extract a shared internal `components/ui/` primitives set (buttons, cards, tables, stat tiles) hand-built for this codebase's Tailwind setup, vs (b) adopt a full third-party component library (e.g. shadcn/ui, Radix UI, Mantine, Chakra) — cover migration cost, bundle size, Tailwind compatibility, and how it affects the splits proposed above.
- [ ] Produce a phased follow-up task breakdown: a numbered list of proposed CTV2 tasks (each touching ≤8 files, 1 PR-sized) that would implement the recommended refactor, ordered by dependency/risk.
- [ ] Research doc created at `docs/research/frontend-refactor-strategy.md` containing sections: `## Component Audit`, `## Performance Findings`, `## Code Smell Findings`, `## Component Reuse Recommendation`, `## Phased Refactor Plan`.
- [ ] Sub-task: recommend test coverage for the untested hotspots found (`AgentsPage`, `AgentDetailPage`, `Dashboard`, `ProjectsPage`, `ProjectDetailPage`, `ChatPanel` — 0 tests currently per `get_knowledge_gaps_tool`) as part of the Phased Refactor Plan, naming suggested test files (e.g. `frontend/src/pages/__tests__/Dashboard.test.tsx`).

## Verification

- `ls docs/research/frontend-refactor-strategy.md` → file exists.
- Doc contains all 5 required `##` sections listed above, each non-empty.
- `## Phased Refactor Plan` names at least 3 follow-up tasks, each listing its own bounded file set (≤8 files).

## Context

`/pm` graph queries against `repo_root=/home/lupca/projects/control-tower-v2` show:
- `get_minimal_context_tool`: 1393 nodes / 15458 edges / 160 files, overall repo risk `medium (0.55)`, 7 test gaps.
- `find_large_functions_tool`: the 8 files above are the largest frontend components (site-wide, only `ChatPanel.tsx` also appears among the top 15 largest nodes in the whole repo, backend included).
- `get_impact_radius_tool` on these 8 files: 500 nodes / 120 files impacted within 2 hops — risk `high`. This is why the task is scoped as **research only** (no code changes) rather than a direct refactor: touching all 120 files in one task would violate the `reasonable-scope` verifier rule (blast radius > 8). The Phased Refactor Plan this task produces is how the actual refactor gets split into ≤8-file tasks.
- `get_knowledge_gaps_tool`: `AgentsPage` (degree 75), `AgentDetailPage` (67), `Dashboard` (66), `ProjectsPage` (65), `ProjectDetailPage` (61), `ChatPanel` (59) are all listed as **untested hotspots** — high fan-out, zero test coverage.
- `get_hub_nodes_tool` / `get_bridge_nodes_tool`: `ModelSelector.tsx` and `ChatPanel.tsx` are architectural bridge nodes in the frontend — any split touching them needs extra care not to break `ChatMessage`/`ModelSelector` tests that already exist.

### Pre-scan findings (OCR)

`ocr scan` ran clean (health check passed) against the 8 files above: 36 comments found. Representative findings (not exhaustive — full list should be reviewed during research):
- `ChatPanel.tsx:221-235` (maintainability, medium): model-switch error handling can leave UI in an inconsistent state on partial failure.
- `ProjectDetail.tsx:203-207` (**security, high**): project description rendered without sanitization — potential XSS if descriptions ever contain untrusted input.
- `ProjectDetail.tsx:46-52` (bug, medium): task-fetch failures are silently swallowed (console.warn only), causing incomplete data with no user-visible error.
- `ProjectDetail.tsx:192` (bug, medium): `created_at` falls back to `Date.now()` instead of a placeholder, showing a misleading date.
- `AgentDetail.tsx:82-83` (bug, high): task filtering doesn't guard against null/undefined `id`.
- `AgentDetail.tsx:114-116` (bug, high + maintainability, medium): agent capabilities aren't validated and fall back to a hardcoded list, which can silently diverge from real agent capabilities.
- `Dashboard.tsx:133` (maintainability, medium): API errors only logged to console, no user-facing recovery path.

The research doc should fold the security (XSS) and high-severity bug findings into the Phased Refactor Plan as near-term fixes, not just cleanup nice-to-haves.

## Plan

1. Read all 8 files in full; for each, map current responsibilities and propose a component split (name, props, what moves where).
2. Grep the frontend for repeated JSX/logic patterns across pages (stat cards, tables, forms, error banners) to size the component-reuse opportunity.
3. Check `frontend/package.json` for what's already installed (Tailwind version, any headless UI libs) before recommending a library.
4. Spot-check for missing memoization / sequential awaits that could be parallelized or cached (React Query is already in the stack per `control-tower-v2.md` tech stack — check if it's underused).
5. Weigh "extract own components" vs "adopt a library" against migration cost and existing Tailwind investment; make one recommendation.
6. Write `docs/research/frontend-refactor-strategy.md` with the 5 required sections.
7. Break the recommendation into a phased list of ≤8-file follow-up tasks (candidate task titles + rough file sets), for a later `/pm` hand-off per task.

## Sub-tasks

- [ ] Recommend test coverage for untested hotspots (`AgentsPage`, `AgentDetailPage`, `Dashboard`, `ProjectsPage`, `ProjectDetailPage`, `ChatPanel`) as part of the Phased Refactor Plan — knowledge gap, see `get_knowledge_gaps_tool` above.
