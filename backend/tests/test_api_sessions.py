import pytest


def test_sessions_api(client):
    # Health check
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "healthy"

    # Create session
    payload = {
        "task_id": "API-001",
        "thread_id": "thread-123",
        "current_gate": "spec",
        "messages": [{"role": "user", "content": "hello"}]
    }
    res = client.post("/sessions", json=payload)
    assert res.status_code == 201
    session_id = res.json()["id"]

    # Get session
    get_res = client.get(f"/sessions/{session_id}")
    assert get_res.status_code == 200
    assert get_res.json()["thread_id"] == "thread-123"

    # List sessions
    list_res = client.get("/sessions")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1
