---
id: CTV2-027
title: "Knowledge reuse for context efficiency"
status: done
priority: medium
risk: low
executor: "@gemini-3.6-flash"
reviewer: "@gpt-5.6-sol"
deadline: 2026-07-30
created: 2026-07-26
depends_on: [CTV2-025]
files:
  - backend/app/services/knowledge_service.py
  - backend/app/graph/gates/spec.py
  - backend/app/graph/gates/plan.py
tests:
  - Spec gate queries relevant knowledge
  - Plan gate includes patterns from knowledge
  - No duplicate context generation
---

# CTV2-027: Knowledge Reuse

## Context
Thay vì generate context mỗi lần, reuse knowledge đã có:
- Patterns → Plan gate
- Conventions → Spec gate
- Decisions (ADRs) → Both gates

## Design

```python
class KnowledgeService:
    def get_relevant(self, task: Task, gate: str) -> list[Knowledge]:
        """
        Query knowledge by:
        1. project (task.project)
        2. tags matching files/domain
        3. type appropriate for gate
        """
        filters = [
            or_(
                Knowledge.project == task.project,
                Knowledge.project.is_(None)  # cross-project
            )
        ]
        
        if gate == "spec":
            filters.append(Knowledge.type.in_(["convention", "decision"]))
        elif gate == "plan":
            filters.append(Knowledge.type.in_(["pattern", "guide", "decision"]))
            
        return db.query(Knowledge).filter(*filters).all()
```

## Integration Points
1. **Spec Gate**: Include conventions/decisions in AC validation
2. **Plan Gate**: Include patterns in plan generation
3. **Dispatch Gate**: Include relevant guides in executor prompt

## Acceptance Criteria
- [ ] AC1: KnowledgeService với `get_relevant()` method
- [ ] AC2: Spec gate queries and includes conventions
- [ ] AC3: Plan gate queries and includes patterns
- [ ] AC4: Knowledge injection giảm duplicate context
- [ ] AC5: Measure: context tokens saved per task
