---
id: CTV2-019
title: "Frontend - Projects & Agents pages"
status: todo
priority: medium
risk: low
executor:
reviewer:
deadline: 2026-07-30
created: 2026-07-26
updated: 2026-07-26
depends_on: [CTV2-015, CTV2-012]
files:
  - frontend/src/pages/Projects.tsx
  - frontend/src/pages/ProjectDetail.tsx
  - frontend/src/pages/Agents.tsx
  - frontend/src/pages/AgentDetail.tsx
  - frontend/src/components/projects/ProjectCard.tsx
  - frontend/src/components/agents/AgentCard.tsx
  - frontend/src/components/agents/AgentStats.tsx
tests:
  - Projects page lists all projects
  - Project detail shows tasks
  - Agents page shows roster with stats
  - Agent detail shows performance history
---

# CTV2-019: Frontend Projects & Agents

## Reference
- control-tower-web `src/pages/projects/`
- control-tower-web `src/pages/agents.astro`

## Acceptance Criteria

### Projects
- [ ] AC1: Grid of project cards
- [ ] AC2: Each card: Name, Progress bar, Task counts, Repo path
- [ ] AC3: Click → Project detail page
- [ ] AC4: Project detail: Task table filtered by project

### Agents
- [ ] AC5: Agent roster grid
- [ ] AC6: Each card: ID, Type (AI/Human), Model, Status badge
- [ ] AC7: Performance stats: Success rate, Tasks executed/reviewed
- [ ] AC8: Strengths/Weaknesses tags
- [ ] AC9: Click → Agent detail page
- [ ] AC10: Agent detail: Full profile, Task history, Performance chart
