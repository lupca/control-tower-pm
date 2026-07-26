import pytest


def test_create_and_get_project(client):
    # Test Create
    payload = {
        "id": "proj-test",
        "name": "Test Project",
        "description": "A test project description",
        "repo_root": "/tmp/test-repo",
        "task_prefix": "TST"
    }
    res = client.post("/api/projects", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["id"] == "proj-test"
    assert data["name"] == "Test Project"
    assert "stats" in data
    assert data["stats"]["total"] == 0

    # Test Duplicate Create
    dup_res = client.post("/api/projects", json=payload)
    assert dup_res.status_code == 400

    # Test Get Detail
    get_res = client.get("/api/projects/proj-test")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Test Project"


def test_list_projects_and_stats(client):
    # Create project
    client.post("/api/projects", json={"id": "proj-stats", "name": "Stats Project"})

    # Create tasks associated with proj-stats
    client.post("/api/tasks", json={"id": "TST-001", "project": "proj-stats", "title": "Task 1"})
    client.post("/api/tasks", json={"id": "TST-002", "project": "proj-stats", "title": "Task 2"})
    client.patch("/api/tasks/TST-002", json={"status": "done"})

    # List Projects
    list_res = client.get("/api/projects")
    assert list_res.status_code == 200
    projects = list_res.json()
    assert len(projects) >= 1

    matched = next((p for p in projects if p["id"] == "proj-stats"), None)
    assert matched is not None
    assert matched["stats"]["total"] == 2
    assert matched["stats"]["todo"] == 1
    assert matched["stats"]["done"] == 1


def test_project_tasks_endpoint(client):
    client.post("/api/projects", json={"id": "proj-tasks", "name": "Tasks Project"})
    client.post("/api/tasks", json={"id": "TSK-101", "project": "proj-tasks", "title": "T1"})
    client.post("/api/tasks", json={"id": "TSK-102", "project": "proj-tasks", "title": "T2"})
    client.patch("/api/tasks/TSK-102", json={"status": "dispatched"})

    # Get tasks for project
    res = client.get("/api/projects/proj-tasks/tasks")
    assert res.status_code == 200
    tasks = res.json()
    assert len(tasks) == 2

    # Filter by status
    res_filtered = client.get("/api/projects/proj-tasks/tasks?status=dispatched")
    assert res_filtered.status_code == 200
    assert len(res_filtered.json()) == 1
    assert res_filtered.json()[0]["id"] == "TSK-102"

    # Non-existent project
    res_404 = client.get("/api/projects/non-existent/tasks")
    assert res_404.status_code == 404


def test_update_and_delete_project(client):
    client.post("/api/projects", json={"id": "proj-upd", "name": "Old Name"})

    # Patch
    patch_res = client.patch("/api/projects/proj-upd", json={"name": "New Name", "graph_status": "ready"})
    assert patch_res.status_code == 200
    assert patch_res.json()["name"] == "New Name"
    assert patch_res.json()["graph_status"] == "ready"

    # Delete
    del_res = client.delete("/api/projects/proj-upd")
    assert del_res.status_code == 204

    # Verify deleted
    get_res = client.get("/api/projects/proj-upd")
    assert get_res.status_code == 404
