import pytest


def test_create_and_get_agent(client):
    payload = {
        "id": "@antigravity-3.6-high",
        "type": "ai",
        "status": "active",
        "model": "gemini-3.6-flash",
        "effort": "high",
        "cli": "agy",
        "strengths": ["python", "fastapi"]
    }
    res = client.post("/api/agents", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["id"] == "@antigravity-3.6-high"
    assert data["strengths"] == ["python", "fastapi"]
    assert data["success_rate"] == 1.0

    # Duplicate create
    dup_res = client.post("/api/agents", json=payload)
    assert dup_res.status_code == 400

    # Get detail
    get_res = client.get("/api/agents/@antigravity-3.6-high")
    assert get_res.status_code == 200
    assert get_res.json()["model"] == "gemini-3.6-flash"


def test_list_agents_and_performance_stats(client):
    client.post("/api/agents", json={"id": "@agent-exec", "type": "ai"})
    client.post("/api/agents", json={"id": "@agent-rev", "type": "human"})

    # Create task with executor and reviewer
    client.post("/api/tasks", json={
        "id": "AGT-001",
        "project": "demo",
        "title": "Agent Task",
        "executor": "@agent-exec",
        "reviewer": "@agent-rev"
    })
    client.patch("/api/tasks/AGT-001", json={"verdict": "pass"})

    list_res = client.get("/api/agents")
    assert list_res.status_code == 200
    agents = list_res.json()
    assert len(agents) >= 2

    exec_agent = next(a for a in agents if a["id"] == "@agent-exec")
    assert exec_agent["total_tasks_executed"] == 1
    assert exec_agent["success_rate"] == 1.0

    rev_agent = next(a for a in agents if a["id"] == "@agent-rev")
    assert rev_agent["total_tasks_reviewed"] == 1


def test_update_and_delete_agent(client):
    client.post("/api/agents", json={"id": "@agent-upd", "type": "ai"})

    # Patch
    patch_res = client.patch("/api/agents/@agent-upd", json={"status": "deprecated", "recent_trend": "declining"})
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "deprecated"
    assert patch_res.json()["recent_trend"] == "declining"

    # Delete
    del_res = client.delete("/api/agents/@agent-upd")
    assert del_res.status_code == 204

    # Verify deleted
    get_res = client.get("/api/agents/@agent-upd")
    assert get_res.status_code == 404
