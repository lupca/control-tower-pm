import pytest


def test_create_and_get_task_api(client):
    payload = {
        "id": "API-001",
        "project": "api_test",
        "title": "API task title",
        "priority": "high",
        "risk": "low"
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "API-001"
    assert data["status"] == "todo"

    response = client.get("/tasks/API-001")
    assert response.status_code == 200
    assert response.json()["title"] == "API task title"


def test_list_and_update_task_api(client):
    client.post("/tasks", json={"id": "API-002", "project": "proj", "title": "Title 2"})

    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.json()) >= 1

    patch_resp = client.patch("/tasks/API-002", json={"status": "dispatched", "executor": "@alice"})
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "dispatched"
    assert patch_resp.json()["executor"] == "@alice"


def test_delete_task_api(client):
    client.post("/tasks", json={"id": "API-003", "project": "proj", "title": "Title 3"})

    del_resp = client.delete("/tasks/API-003")
    assert del_resp.status_code == 204

    get_resp = client.get("/tasks/API-003")
    assert get_resp.status_code == 404
