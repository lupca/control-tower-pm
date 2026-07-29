---
id: CTV2-026
title: "Agent selection algorithm (token efficiency)"
status: done
priority: high
risk: medium
executor: "@gemini-3.6-flash"
reviewer: "@claude-opus"
deadline: 2026-07-30
created: 2026-07-26
depends_on: [CTV2-025]
files:
  - backend/app/services/agent_selector.py
  - backend/app/graph/gates/dispatch.py
tests:
  - Agent với success_rate cao được ưu tiên
  - Task risk cao → agent experienced
  - Task simple → agent fast tier
---

# CTV2-026: Agent Selection Algorithm

## Context
Mục tiêu v2: "bảo đảm tốn ít token hơn và kết quả task tốt hơn".
Cần algorithm chọn agent tối ưu dựa trên:
1. Agent performance stats (success_rate, avg_review_rounds)
2. Task characteristics (risk, complexity, domain)
3. Agent capabilities (strengths, model tier)

## Algorithm Design

```python
def select_agent(task: Task, available_agents: list[Agent]) -> Agent:
    """
    Token efficiency scoring:
    - success_rate ↑ → fewer review rounds → less tokens
    - matching strengths → faster completion
    - appropriate tier → not overpaying for simple tasks
    """
    scores = []
    for agent in available_agents:
        score = 0
        
        # Base: success rate (0-100)
        score += agent.success_rate * 100
        
        # Penalty: more review rounds = more tokens
        score -= (agent.avg_review_rounds - 1) * 20
        
        # Match task risk to agent experience
        if task.risk == "high" and agent.total_tasks_executed > 10:
            score += 30
        
        # Match strengths to task files/domain
        if any(s in task.files for s in agent.strengths):
            score += 25
            
        # Tier efficiency: don't use expensive model for simple tasks
        if task.risk == "low" and agent.effort == "low":
            score += 15
            
        scores.append((score, agent))
    
    return max(scores, key=lambda x: x[0])[1]
```

## Acceptance Criteria
- [ ] AC1: `AgentSelector` service với scoring algorithm
- [ ] AC2: Dispatch gate sử dụng selector khi không có executor explicit
- [ ] AC3: API endpoint `/api/agents/recommend?task_id=X`
- [ ] AC4: Log selection reasoning cho audit
- [ ] AC5: Test với mock data showing optimal selection
