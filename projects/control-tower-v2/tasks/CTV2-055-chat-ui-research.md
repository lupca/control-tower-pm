---
id: CTV2-055
title: "Research: Chat UI với Hierarchical Context + Multi-Session"
status: done
priority: high
risk: normal
deadline: null
executor: "@claude-opus"
reviewer: null
result_ref: "9c357fe"
depends_on: [CTV2-053]
files:
  - backend/app/db/models.py
  - backend/app/services/context_hierarchy.py
  - frontend/src/components/chat/ChatPanel.tsx
  - frontend/src/components/chat/ChatPanelManager.tsx
  - frontend/src/pages/TaskDetail.tsx
  - frontend/src/pages/ProjectDetail.tsx
flows: []
tests: []
dispatched: 2026-07-26
in_review: null
predicted_success: high
prediction_factors:
  score: 0.8
  deductions:
    - "research task, no code changes (-0.1)"
    - "depends on CTV2-053 context hierarchy (-0.1)"
created: 2026-07-26
updated: 2026-07-26
confidence_interval: [0.7, 0.9]
---

# CTV2-055: Research: Chat UI với Hierarchical Context + Multi-Session

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Bối cảnh

Hiện tại chat chỉ available trong TaskDetail page. User cần:
1. Chat ở Global level (bất kỳ đâu)
2. Chat ở Project level (trong ProjectDetail)
3. Chat ở Task level (trong TaskDetail) - đã có nhưng thiếu session management

Mỗi level cần hỗ trợ multiple sessions với history.

## Tiêu chí nghiệm thu (AC)

- [ ] **Architecture Document** (`docs/chat-ui-architecture.md`):
  - Mô tả 3-level chat: Global → Project → Task
  - Session lifecycle và context inheritance
  - Component hierarchy (ChatProvider, ChatSidebar, ChatPanel)
  
- [ ] **DB Schema Proposal** (trong architecture doc):
  - Session model changes để support hierarchical context
  - Relationship: Session → (Global | Project | Task)
  - Index strategy cho query sessions by context
  
- [ ] **Wireframes/Mockups**:
  - Global chat floating button + sidebar
  - Project page với chat panel
  - Task page với chat panel (update từ hiện tại)
  - Session tabs UI trong mỗi chat panel
  
- [ ] **Token Caching Strategy**:
  - Phân tích cache behavior của Anthropic API
  - Thiết kế message order để maximize cache hits
  - Estimate token savings với hierarchical caching

## Verification

- `docs/chat-ui-architecture.md` tồn tại và có đủ 4 sections trên
- Wireframes as images hoặc ASCII diagrams trong doc
- Token caching section có concrete numbers/estimates

## Plan

### Phase 1: Current State Analysis
1. Read `backend/app/db/models.py` - Session, Project, Task relationships
2. Read `frontend/src/components/chat/*` - ChatPanel, ChatPanelManager
3. Read `frontend/src/pages/*` - where chat is/should be integrated
4. Document gaps vs requirements

### Phase 2: Token Caching Research
1. Research Anthropic prompt caching (cache_control, TTL, cache hits)
2. Analyze current `context_hierarchy.py` implementation
3. Design message ordering for maximum cache reuse
4. Calculate expected savings with multi-session

### Phase 3: DB Schema Design
1. Design Session model changes:
   - Add `context_level: enum('global', 'project', 'task')`
   - Add `project_id: FK(projects.id), nullable`
   - Keep `task_id` for task-level sessions
2. Design indexes for efficient queries by context
3. Consider session archiving strategy

### Phase 4: UI/UX Design
1. **Global Chat**: 
   - Floating button (bottom-right, always visible)
   - Collapsible sidebar khi click
   - Session tabs at top
2. **Project Chat**:
   - Panel trong ProjectDetail page (right sidebar)
   - Auto-select project context
   - Show child tasks as quick-switch options
3. **Task Chat**:
   - Update existing ChatPanelManager
   - Add session tabs
   - Pre-select project + task context

### Phase 5: Documentation
1. Write `docs/chat-ui-architecture.md`
2. Include wireframes (ASCII or images)
3. Include DB schema changes
4. Include token caching strategy with numbers

## Sub-tasks

- [ ] Analyze current Session model và ChatPanel props
- [ ] Research Anthropic prompt caching behavior
- [ ] Design DB schema cho hierarchical sessions
- [ ] Create wireframes cho 3 chat levels
- [ ] Design session tab UI
- [ ] Document token caching strategy
- [ ] Write architecture document

## Current State Analysis

### DB: Session model (backend/app/db/models.py:168-184)
```python
class Session(Base):
    id = Column(String(36), primary_key=True)
    task_id = Column(String(20), ForeignKey("tasks.id"), nullable=True)
    thread_id = Column(String(100), nullable=True)
    messages = Column(JSON, default=list)
    # ... selected_model, selected_provider
```

**Gap**: Session chỉ có `task_id`, không có `project_id` hay `context_level`.

### Frontend: ChatPanelManager
- 3 modes: docked, floating, collapsed
- Chỉ dùng trong TaskDetailPage
- Không có session switching

### Context Hierarchy (từ CTV2-053)
- Global → Project → Task context injection
- cache_control markers tại tier boundaries
- 25KB cap cho project context
