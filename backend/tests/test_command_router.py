import pytest
from app.services.command_router import CommandRouter, COMMANDS
from app.db.models import Task, Session


def test_command_router_parse():
    router = CommandRouter()

    # Known commands
    cmd, args = router.parse("/pm Add user authentication --project demo")
    assert cmd == "create_task"
    assert args == "Add user authentication --project demo"

    cmd, args = router.parse("/dispatch TASK-001 @gemini")
    assert cmd == "dispatch_task"
    assert args == "TASK-001 @gemini"

    cmd, args = router.parse("/verdict TASK-001 pass --reviewer @claude")
    assert cmd == "verdict"
    assert args == "TASK-001 pass --reviewer @claude"

    cmd, args = router.parse("/status TASK-001")
    assert cmd == "get_status"
    assert args == "TASK-001"

    cmd, args = router.parse("/help")
    assert cmd == "show_help"
    assert args == ""

    # Regular message
    cmd, args = router.parse("Hello assistant")
    assert cmd is None
    assert args == "Hello assistant"

    # Unknown command
    cmd, args = router.parse("/unknown command")
    assert cmd is None
    assert args == "/unknown command"


@pytest.mark.asyncio
async def test_handle_create_task(db, graph):
    router = CommandRouter(db_session=db, graph=graph)
    res = await router.execute("create_task", "Build auth module --project demo", "thread-1")

    assert res["action"] == "task_created"
    assert "DEMO" in res["task_id"]
    assert res["title"] == "Build auth module"
    assert res["current_gate"] == "spec"
    assert len(res["acceptance_criteria"]) > 0

    # Verify task in DB
    task = db.session.query(Task).filter(Task.id == res["task_id"]).first()
    assert task is not None
    assert task.title == "Build auth module"


@pytest.mark.asyncio
async def test_handle_dispatch_task(db, graph):
    router = CommandRouter(db_session=db, graph=graph)

    # First create task
    create_res = await router.execute("create_task", "Test task --project demo", "thread-1")
    task_id = create_res["task_id"]

    # Dispatch task
    res = await router.execute("dispatch_task", f"{task_id} @gemini-3.6", "thread-1")
    assert res["action"] == "dispatched"
    assert res["task_id"] == task_id
    assert res["executor"] == "@gemini-3.6"
    assert res["status"] == "dispatched"

    # Verify in DB
    task = db.session.query(Task).filter(Task.id == task_id).first()
    assert task.executor == "@gemini-3.6"
    assert task.status == "dispatched"


@pytest.mark.asyncio
async def test_handle_verdict_task(db, graph):
    router = CommandRouter(db_session=db, graph=graph)

    # Create & Dispatch
    create_res = await router.execute("create_task", "Verdict task --project demo", "thread-1")
    task_id = create_res["task_id"]
    await router.execute("dispatch_task", f"{task_id} @gemini-3.6", "thread-1")

    # Record verdict with different reviewer (pass)
    res = await router.execute("verdict", f"{task_id} pass --reviewer @claude-sonnet", "thread-1")
    assert res["action"] == "verdict_recorded"
    assert res["verdict"] == "pass"
    assert res["status"] == "done"

    # Four eyes violation check: reviewer == executor
    await router.execute("dispatch_task", f"{task_id} @same-agent", "thread-1")
    err_res = await router.execute("verdict", f"{task_id} pass --reviewer @same-agent", "thread-1")
    assert "error" in err_res
    assert "Four-eyes violation" in err_res["error"]


@pytest.mark.asyncio
async def test_handle_status_and_help(db, graph):
    router = CommandRouter(db_session=db, graph=graph)

    # Create task
    create_res = await router.execute("create_task", "Status test --project demo", "thread-1")
    task_id = create_res["task_id"]

    # Get status
    status_res = await router.execute("get_status", task_id, "thread-1")
    assert status_res["action"] == "status"
    assert status_res["task_id"] == task_id
    assert status_res["title"] == "Status test"

    # Help command
    help_res = await router.execute("show_help", "", "thread-1")
    assert help_res["action"] == "help"
    assert "/pm <description> [--project <name>]" in help_res["commands"]


def test_chat_api_endpoint(client):
    # 1. Create task via /chat
    resp = client.post("/chat", json={"message": "/pm Create endpoint test --project API", "thread_id": "t1"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "command"
    assert "✅ Task created:" in data["message"]
    task_id = data["result"]["task_id"]

    # 2. Dispatch via /chat
    resp = client.post("/chat", json={"message": f"/dispatch {task_id} @agent1", "thread_id": "t1"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "command"
    assert "🚀 Task" in data["message"]

    # 3. Four eyes violation via /chat
    resp = client.post("/chat", json={"message": f"/verdict {task_id} pass --reviewer @agent1", "thread_id": "t1"})
    assert resp.status_code == 200
    data = resp.json()
    assert "❌ Error: Four-eyes violation" in data["message"]

    # 4. Valid verdict via /chat
    resp = client.post("/chat", json={"message": f"/verdict {task_id} pass --reviewer @agent2", "thread_id": "t1"})
    assert resp.status_code == 200
    data = resp.json()
    assert "📋 Verdict recorded" in data["message"]

    # 5. Get status via /chat
    resp = client.post("/chat", json={"message": f"/status {task_id}", "thread_id": "t1"})
    assert resp.status_code == 200
    data = resp.json()
    assert "📊 Task" in data["message"]

    # 6. Help via /chat
    resp = client.post("/chat", json={"message": "/help", "thread_id": "t1"})
    assert resp.status_code == 200
    data = resp.json()
    assert "Available commands:" in data["message"]

    # 7. Regular chat via /chat
    resp = client.post("/chat", json={"message": "Hello general message", "thread_id": "t1"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "chat"
    assert data["message"] == "Received: Hello general message"
