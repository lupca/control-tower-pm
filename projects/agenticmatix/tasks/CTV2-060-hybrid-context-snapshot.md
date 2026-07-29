---
id: CTV2-060
title: "Implement Hybrid Context Snapshot for User Chat"
status: done
verdict: pass
verdict_date: 2026-07-27
priority: high
risk: normal
deadline: 2026-08-10
executor: "@gpt-5.6-luna-high"
reviewer: "@claude-opus"
result_ref: "2fef62b"
depends_on: [CTV2-059]
files:
  - backend/app/graph/context.py
  - backend/app/graph/coordinator.py
  - backend/app/api/chat.py
  - backend/app/api/projects.py
  - backend/app/api/tasks.py
flows: [chat-session, coordinator-invoke]
tests:
  - tests/unit/test_context_snapshot.py
  - tests/integration/test_chat_context.py
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: high
prediction_factors:
  score: 0.85
  deductions:
    - "depends_on completed research (-0.0)"
    - "touches coordinator core (-0.1)"
    - "needs new tests (-0.05)"
created: 2026-07-27
updated: 2026-07-27
planned: 2026-07-27
---

# CTV2-060: Implement Hybrid Context Snapshot for User Chat

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Context

Triển khai Option C (Hybrid) từ research CTV2-059: inject compact state snapshot vào system prompt cho reads, dùng tools chỉ cho mutations. Target: 74% token savings so với pure tool-based approach.

## Tiêu chí nghiệm thu (AC)

- [ ] AC1: Implement `build_context_snapshot(session: Session) -> str` function
  - List active projects với task count
  - List recent tasks (last 5) của current project scope
  - Output format compact, human-readable
- [ ] AC2: Integrate context snapshot vào coordinator's system prompt
  - Snapshot inject trước tool schemas
  - Support prompt caching (stable prefix)
- [ ] AC3: Implement refresh logic sau mutations
  - Snapshot rebuild khi create/update project/task
  - Cache invalidation đúng scope
- [ ] AC4: User chat responses chính xác khi hỏi về projects/tasks
  - "Có những project nào?" → trả về đúng danh sách
  - "Task nào đang dispatched?" → trả về đúng filtered list
- [ ] AC5: Token savings measurable (target: >50% reduction vs baseline)

## Verification

- `pytest tests/unit/test_context_snapshot.py` → 100% pass
- `pytest tests/integration/test_chat_context.py` → 100% pass
- Manual test: chat session với 10 turns, verify token count
- Compare token usage: before/after implementation

## Technical Design (from CTV2-059)

```python
def build_context_snapshot(session: Session) -> str:
    """Generate compact state summary for system prompt."""
    projects = db.query(Project).filter(Project.status == "active").all()
    
    lines = ["## Current Context", f"Projects ({len(projects)}):"]
    for p in projects:
        task_count = db.query(Task).filter(Task.project == p.id).count()
        lines.append(f"- {p.id}: {p.name} ({p.status}, {task_count} tasks)")
    
    if session.project_id:
        recent_tasks = (
            db.query(Task)
            .filter(Task.project == session.project_id)
            .order_by(Task.updated_at.desc())
            .limit(5)
            .all()
        )
        lines.append(f"\nRecent tasks in {session.project_id}:")
        for t in recent_tasks:
            lines.append(f"- {t.id}: {t.title[:40]} ({t.status})")
    
    return "\n".join(lines)
```

## Plan

### Phase 1: Context Snapshot Builder (AC1)
1. Create `app/graph/context.py`:
   - `build_context_snapshot(session: Session, db: Session) -> str`
   - Query active projects với task counts
   - Query recent tasks (limit 5) cho current project scope
   - Format output compact, ~300-500 tokens max

### Phase 2: Coordinator Integration (AC2)
1. Update `app/graph/coordinator.py`:
   - Import context builder
   - Call `build_context_snapshot()` khi building system prompt
   - Place snapshot BEFORE tool schemas (stable prefix for caching)
2. Ensure system prompt structure:
   ```
   [Base instructions] + [Context Snapshot] + [Tool Schemas]
   ```

### Phase 3: Cache Invalidation (AC3)
1. Add hooks trong `app/api/` sau mutations:
   - `POST /projects` → invalidate
   - `POST /tasks`, `PATCH /tasks/{id}` → invalidate
2. Strategy: rebuild snapshot on next chat turn (lazy invalidation)

### Phase 4: Testing (AC4, AC5)
1. Unit tests:
   - Snapshot format correctness
   - Empty state handling
   - Large dataset pagination
2. Integration tests:
   - Chat session với context queries
   - Verify responses accurate
3. Token measurement:
   - Baseline: pure tool-based session (10 turns)
   - After: hybrid session (10 turns)
   - Calculate savings %

## Sub-tasks

- [ ] Create `app/graph/context.py` với `build_context_snapshot()`
- [ ] Update coordinator system prompt injection
- [ ] Add cache invalidation hooks sau mutations
- [ ] Write unit tests cho snapshot builder
- [ ] Write integration tests cho chat context awareness
- [ ] Measure và document token savings

