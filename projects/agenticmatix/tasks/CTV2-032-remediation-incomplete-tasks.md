---
id: CTV2-032
title: "Remediation: Fix placeholder implementations"
status: done
priority: critical
risk: high
deadline: 2026-07-28
executor: "@gemini-2.5-pro"
reviewer: "@claude-opus"
dispatched: 2026-07-26
depends_on: []
files:
  - backend/app/services/command_router.py
  - backend/app/workers/agent_runner.py
  - backend/app/api/dispatch.py
  - backend/app/api/stream.py
  - docker-compose.yml
  - backend/tests/integration/test_api_dispatch.py
tests:
  - /pm command actually creates task in DB
  - /dispatch command actually queues to Dramatiq
  - Redis container runs
  - Worker container runs
  - pytest tests have real assertions
created: 2026-07-26
updated: 2026-07-26
predicted_success: medium
prediction_factors:
  score: 0.6
  deductions:
    - "previous_failures: agents created placeholders (-0.3)"
    - "complexity: multiple files need real implementation (-0.1)"
---

# CTV2-032: Remediation - Fix Placeholder Implementations

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Context

Các task CTV2-030, 031, 024, 026 được marked done nhưng code là placeholder:
- Handlers chỉ parse, không execute
- Tests chỉ có `assert True`
- docker-compose thiếu redis + worker

## Tiêu chí nghiệm thu (AC)

### CTV2-030 Command Router
- [ ] AC1: `_handle_create_task()` tạo task trong DB + run Spec Gate
- [ ] AC2: `_handle_dispatch_task()` queue task vào Dramatiq
- [ ] AC3: `_handle_get_status()` return task state từ DB
- [ ] AC4: `_handle_verdict()` update task status + enforce four-eyes

### CTV2-031 Agent Runner
- [ ] AC5: `docker-compose.yml` có redis service (port 6379)
- [ ] AC6: `docker-compose.yml` có worker service chạy dramatiq
- [ ] AC7: `run_agent()` thực sự spawn subprocess với command
- [ ] AC8: Output được publish qua Redis pub/sub
- [ ] AC9: SSE endpoint stream realtime output

### Tests
- [ ] AC10: `test_api_dispatch.py` có assertions kiểm tra response
- [ ] AC11: `test_command_router.py` test tất cả commands
- [ ] AC12: Tất cả tests PHẢI FAIL nếu implementation sai

## Verification

```bash
# 1. Start system
docker compose up -d --build

# 2. Test command router
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"thread_id": "test", "message": "/pm Test task --project control-tower-v2"}'
# Expected: task created in DB

# 3. Test dispatch
curl -X POST http://localhost:8001/api/dispatch \
  -d '{"task_id": "CTV2-XXX", "agent_id": "@gemini-3.6-flash"}'
# Expected: job queued to Redis

# 4. Verify Redis + Worker running
docker compose ps | grep -E "redis|worker"
# Expected: both running

# 5. Run tests
docker exec control_tower_backend pytest tests/ -v
# Expected: all pass with real assertions
```

## Plan

### Phase 1: Docker Infrastructure (AC5, AC6)

1. **Update docker-compose.yml**
   ```yaml
   services:
     redis:
       image: redis:7-alpine
       ports: ["6379:6379"]
       healthcheck:
         test: ["CMD", "redis-cli", "ping"]
     
     worker:
       build: ./backend
       command: dramatiq app.workers.agent_runner
       depends_on: [redis, db]
       environment:
         - REDIS_URL=redis://redis:6379/0
       volumes:
         - /home/lupca/projects:/home/lupca/projects:rw
   ```

### Phase 2: Command Router Handlers (AC1-AC4)

2. **command_router.py - _handle_create_task()**
   ```python
   async def _handle_create_task(self, args: str, session_id: str) -> dict:
       project = self._extract_flag(args, "--project") or "default"
       title = self._remove_flags(args)
       
       # Create task in DB
       task = Task(
           id=generate_task_id(project),
           project=project,
           title=title,
           status="todo"
       )
       self.db.add(task)
       self.db.commit()
       
       return {"action": "created", "task_id": task.id}
   ```

3. **command_router.py - _handle_dispatch_task()**
   ```python
   async def _handle_dispatch_task(self, args: str, session_id: str) -> dict:
       parts = args.split()
       task_id, agent_id = parts[0], parts[1]
       
       # Queue to Dramatiq
       from app.workers.agent_runner import run_agent
       run_agent.send(task_id, agent_id, command, repo_root)
       
       # Update task status
       task.status = "dispatched"
       task.executor = agent_id
       self.db.commit()
       
       return {"action": "dispatched", "task_id": task_id}
   ```

4. **command_router.py - _handle_get_status()**
   ```python
   async def _handle_get_status(self, args: str, session_id: str) -> dict:
       task_id = args.strip()
       task = self.db.query(Task).filter(Task.id == task_id).first()
       if not task:
           return {"error": f"Task {task_id} not found"}
       return {"task_id": task.id, "status": task.status, "executor": task.executor}
   ```

### Phase 3: Agent Runner Full Implementation (AC7-AC9)

5. **agent_runner.py - Full subprocess with streaming**
   ```python
   @dramatiq.actor(max_retries=3, min_backoff=30000)
   def run_agent(run_id: str, task_id: str, command: str, repo_root: str):
       process = subprocess.Popen(
           command, shell=True, cwd=repo_root,
           stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
           stdin=subprocess.DEVNULL, text=True, bufsize=1
       )
       
       for line in process.stdout:
           redis_client.publish(f"run:{run_id}", line)
       
       exit_code = process.wait()
       redis_client.publish(f"run:{run_id}", f"__DONE__{exit_code}")
   ```

6. **stream.py - SSE with Redis subscription**
   ```python
   @router.get("/runs/{run_id}/stream")
   async def stream_output(run_id: str):
       async def generator():
           pubsub = redis_client.pubsub()
           pubsub.subscribe(f"run:{run_id}")
           for msg in pubsub.listen():
               if msg["type"] == "message":
                   yield f"data: {msg['data']}\\n\\n"
       return StreamingResponse(generator(), media_type="text/event-stream")
   ```

### Phase 4: Real Tests (AC10-AC12)

7. **test_api_dispatch.py - Real assertions**
   ```python
   def test_dispatch_creates_run():
       response = client.post("/api/dispatch", json={...})
       assert response.status_code == 200
       data = response.json()
       assert "run_id" in data
       assert data["status"] == "queued"
       
       # Verify in DB
       run = db.query(AgentRun).filter(AgentRun.id == data["run_id"]).first()
       assert run is not None
   ```

8. **test_command_router.py - Test all commands**
   ```python
   def test_handle_create_task():
       result = await router._handle_create_task("Test task --project test", "s1")
       assert result["action"] == "created"
       assert "task_id" in result
       
       # Verify task in DB
       task = db.query(Task).filter(Task.id == result["task_id"]).first()
       assert task.title == "Test task"
   ```

## Sub-tasks

- [ ] Fix command_router.py handlers (4 methods)
- [ ] Add redis + worker to docker-compose.yml
- [ ] Implement full run_agent() with subprocess
- [ ] Implement SSE streaming
- [ ] Write real test assertions
