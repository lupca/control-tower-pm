---
id: CTV2-006
title: "Chainlit Chat UI Integration"
status: done
priority: medium
risk: low
deadline: 2026-08-16
executor: "@antigravity-3.6-high"
reviewer: "@antigravity"
result_ref: "f41e472"
depends_on:
  - CTV2-003
  - CTV2-004
files:
  - frontend/chat/app.py
  - frontend/chat/handlers.py
  - frontend/chat/router.py
  - frontend/chat/Dockerfile
flows: []
tests:
  - frontend/chat/tests/test_chat.py
dispatched: 2026-07-26
in_review: 2026-07-26
predicted_success: high
prediction_factors:
  score: 0.8
  deductions:
    - "Chainlit well-documented (+0.05)"
    - "LangGraph native integration (+0.1)"
    - "UI customization may need work (-0.1)"
created: 2026-07-26
updated: 2026-07-26
---

# CTV2-006: Chainlit Chat UI Integration

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Tiêu chí nghiệm thu (AC)

- [x] Chainlit app chạy trên port 8080
- [x] Chat session linked với LangGraph thread
- [x] Commands (`/pm`, `/lint`, etc.) route tới pipeline (0 tokens)
- [x] Questions route tới Claude với state context
- [x] Streaming responses hoạt động
- [x] Session persistence (refresh không mất history)
- [x] Docker container build thành công

## Router Logic

```python
def route_message(message: str) -> Literal["pipeline", "chat"]:
    # Commands
    if message.startswith("/"):
        return "pipeline"
    
    # Approval keywords
    if message.lower() in ["approve", "reject", "pass", "changes", "y", "n"]:
        return "pipeline"
    
    # Questions (có dấu ?)
    if "?" in message:
        return "chat"
    
    # Default to chat
    return "chat"
```

## Chat Handler

```python
import chainlit as cl
from app.graph.builder import build_graph

@cl.on_chat_start
async def start():
    graph = build_graph()
    cl.user_session.set("graph", graph)
    cl.user_session.set("thread_id", str(uuid4()))

@cl.on_message
async def main(message: cl.Message):
    thread_id = cl.user_session.get("thread_id")
    config = {"configurable": {"thread_id": thread_id}}
    
    route = route_message(message.content)
    
    if route == "pipeline":
        # No LLM tokens
        graph = cl.user_session.get("graph")
        result = await graph.ainvoke({"raw_input": message.content}, config)
        await cl.Message(content=format_result(result)).send()
    else:
        # Chat with context
        state = graph.get_state(config)
        response = await chat_with_context(message.content, state.values)
        await cl.Message(content=response).send()
```

## Plan

1. Install chainlit: `pip install chainlit`
2. Create basic app.py với on_chat_start, on_message
3. Implement router logic
4. Connect tới LangGraph với shared thread_id
5. Add streaming support
6. Build Docker image
7. Test full flow

## Verification

```bash
chainlit run app.py --port 8080
# Browser: localhost:8080
# Type: /pm test task
# Expect: "Created CTV2-XXX. Awaiting Spec Gate."
```
