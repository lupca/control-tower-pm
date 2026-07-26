---
id: CTV2-059
title: "Research: Kiến trúc Data Manipulation cho User Chat"
status: done
priority: high
risk: normal
deadline: 2026-08-03
executor: "@claude-opus"
reviewer: "@gemini-2.5-pro"
result_ref: "964a9a9"
depends_on: []
files: []
flows: []
tests: []
dispatched: 2026-07-27
in_review: 2026-07-27
predicted_success: high
prediction_factors:
  score: 0.9
  deductions:
    - "research task, no code blast radius (-0.0)"
    - "greenfield project, no existing patterns to conflict (-0.0)"
    - "no tests required for research (-0.1)"
created: 2026-07-27
updated: 2026-07-27
planned: 2026-07-27
---

# CTV2-059: Research: Kiến trúc Data Manipulation cho User Chat

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Context

Mục tiêu cao nhất của control-tower-v2:
1. Ưu tiên chất lượng đầu ra khi agent làm task
2. Giảm token, tránh lãng phí

Mục tiêu gần: User thao tác với dữ liệu qua chat (agentic OS) thay vì UI — tạo task, tạo project, query context ngoài flow phát triển hiện tại.

Vấn đề hiện tại: Khi hỏi "Có những project nào?", AI trả lời hệ thống không có project nào — thiếu context về data hiện có.

## Tiêu chí nghiệm thu (AC)

- [x] AC1: Tổng hợp tài liệu LangGraph về state management, memory, và persistence patterns
- [x] AC2: Phân tích các kiến trúc agentic OS hiện có (LangGraph, AutoGen, CrewAI) về cách expose data cho user chat
- [x] AC3: Đề xuất 2-3 architecture options cho việc user query/manipulate data qua chat:
  - Option phải cover: list projects, list tasks, create task, create project
  - Option phải giải quyết: context awareness (AI biết data hiện có)
  - Option phải balance: quality output vs token efficiency
- [x] AC4: So sánh trade-offs giữa các options (token cost, latency, complexity, quality)
- [x] AC5: Đề xuất architecture được recommend với lý do cụ thể

## Verification

- Research deliverable có trong `projects/control-tower-v2/docs/` hoặc trong task body `## Research Output`
- Mỗi AC có section tương ứng trong output
- Options có diagrams/pseudo-code minh họa
- Trade-offs có bảng so sánh định lượng (nếu có thể)

## Research Scope

### Sources cần đọc
- LangGraph docs: https://langchain-ai.github.io/langgraph/
  - State management
  - Memory & persistence
  - Tool calling patterns
- Agentic OS architectures:
  - LangGraph Studio patterns
  - AutoGen multi-agent patterns
  - CrewAI task delegation patterns

### Questions cần trả lời
1. Làm sao để AI biết về projects/tasks hiện có mà không load toàn bộ vào context?
2. Tool-based approach vs RAG-based approach vs hybrid?
3. Cách tối ưu token khi user query repeatedly trong 1 session?
4. Cách handle CRUD operations qua chat một cách an toàn?

## Plan

### Phase 1: LangGraph Deep Dive (AC1)
1. Đọc LangGraph docs về:
   - State management patterns (StateGraph, MessageState)
   - Memory persistence (checkpointing, threads)
   - Tool calling và integration patterns
2. Ghi chú key patterns relevant cho data manipulation

### Phase 2: Agentic OS Survey (AC2)
1. Survey LangGraph Studio architecture
2. Survey AutoGen multi-agent patterns (data sharing between agents)
3. Survey CrewAI task delegation (how agents access shared state)
4. Extract common patterns và anti-patterns

### Phase 3: Architecture Options Design (AC3)
1. **Option A**: Tool-based approach
   - Mỗi operation (list_projects, create_task) là 1 tool
   - LLM decide khi nào call tool
   - Pros: explicit, controllable
   - Cons: token per tool call

2. **Option B**: RAG-based approach
   - Index projects/tasks vào vector store
   - Query via semantic search
   - Pros: natural language queries
   - Cons: indexing overhead, stale data

3. **Option C**: Hybrid (Tool + Structured State)
   - State snapshot injected vào system prompt (summary)
   - Tools cho mutations (create, update)
   - Read operations via state

### Phase 4: Trade-off Analysis (AC4)
1. Định lượng token cost cho mỗi option (estimate)
2. Latency analysis
3. Complexity assessment
4. Quality comparison (accuracy of responses)

### Phase 5: Recommendation (AC5)
1. Chọn recommended approach
2. Justify với criteria từ project goals
3. Outline next steps cho implementation

## Sub-tasks

- [x] Đọc LangGraph docs về state/memory/persistence
- [x] Survey agentic OS architectures (3 frameworks)
- [x] Draft architecture options
- [x] Viết comparison table
- [x] Chọn recommended approach + viết justification

## Research Output

Full research document: [[control-tower-v2/docs/CTV2-059-chat-data-architecture-research.md]]

### Summary

**Recommended Architecture: Option C (Hybrid - Structured State Snapshot + Tools)**

| Approach | Tokens/50-turn session | Data Freshness | Complexity |
|----------|------------------------|----------------|------------|
| A: Pure Tools | ~60,000 | Real-time | Low |
| B: RAG-based | ~100,000 | May be stale | High |
| **C: Hybrid** | **~15,000** | Real-time | Medium |

**Key insight**: Inject compact state snapshot into system prompt for reads (cacheable, near-zero cost), use tools only for mutations.

**Token savings**: 74% reduction vs pure tool-based approach.

**Next implementation steps**:
1. Implement `build_context_snapshot()` function  
2. Integrate into coordinator's system prompt  
3. Add refresh logic after mutations  
4. Test with real sessions, measure savings
