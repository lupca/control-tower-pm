---
id: CTV2-043
title: "Research: Agent-Task Matching Service + Chat UI Actions"
status: in-review
priority: high
risk: low
deadline: 2026-07-30
executor: "@gpt-5.6-luna-high"
reviewer: "@gpt-5.6-sol"
dispatched: 2026-07-26
result_ref: cd45531
in_review: 2026-07-26
reviewer:
files:
  - backend/app/services/agent_matcher.py
  - backend/app/api/agents.py
  - frontend/src/components/task/DispatchButton.tsx
  - frontend/src/components/chat/QuickActions.tsx
  - knowledge/agents/*.md
tests:
  - API returns ranked agent suggestions for task
  - DispatchButton shows agent dropdown with scores
  - Chat has clickable action buttons
created: 2026-07-26
effort: 6h
---

# CTV2-043: Agent-Task Matching + Chat Quick Actions

## Problem

1. **Hardcoded agent selection**: `const agentId = task.executor || '@gpt-5.6-luna-high'` — không có logic chọn agent phù hợp.
2. **Chat UX kém**: User phải nhớ và gõ `/dispatch`, `/status`, `/verdict`... thay vì click.

## Scope

### Part 1: Agent-Task Matching Service

**Backend:**
```python
# backend/app/services/agent_matcher.py
class AgentMatcher:
    def suggest_agents(self, task: Task, top_n: int = 3) -> List[AgentSuggestion]:
        # Factors:
        # - skill_match: task tags vs agent specialties
        # - past_performance: success_rate on similar tasks
        # - current_load: running tasks count
        # - cost_tier: budget consideration
        return ranked_suggestions
```

**API:**
```
GET /api/tasks/{id}/suggested-agents
Response: [
  { agent_id: "@gpt-5.6-luna-high", score: 0.92, reason: "High success rate on frontend tasks" },
  { agent_id: "@gemini-3.6-flash", score: 0.78, reason: "Fast, low cost" },
  ...
]
```

**Frontend DispatchButton:**
- Fetch suggestions on mount
- Show dropdown with scores + reasons
- Default to top suggestion
- User can override

### Part 2: Chat Quick Actions

**Current:**
```
[Quick] _________________ [Send]
```

**Proposed:**
```
[Dispatch ▾] [Status] [Review] [Verdict ▾] | [Quick] _______ [Send]
```

**Context-aware visibility:**
- `todo`: Show [Dispatch]
- `dispatched`: Show [Status], [Cancel]
- `in-review`: Show [Verdict ▾]
- `done`: Hide all

**Implementation:**
```typescript
// frontend/src/components/chat/QuickActions.tsx
const QuickActions: React.FC<{ task: Task }> = ({ task }) => {
  const actions = getActionsForStatus(task.status);
  return (
    <div className="flex gap-2">
      {actions.map(action => (
        <ActionButton key={action.id} action={action} task={task} />
      ))}
    </div>
  );
};
```

## AC

- [ ] AC1: `GET /api/tasks/{id}/suggested-agents` returns ranked list
- [ ] AC2: AgentMatcher considers skill match + past performance
- [ ] AC3: DispatchButton shows suggestions with scores
- [ ] AC4: Chat has Quick Actions bar with context-aware buttons
- [ ] AC5: Clicking action button triggers corresponding command

## Research Questions

1. How to score skill match? (tags, embeddings, keyword overlap?)
2. Where to store agent performance history? (new table? aggregate from runs?)
3. Should suggestions be cached? (task-level, session-level?)
4. Mobile-friendly action bar design?

## References

- `knowledge/agents/*.md` — agent profiles with specialties
- `knowledge/metrics/agent-performance.md` — success rates
