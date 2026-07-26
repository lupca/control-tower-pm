import pytest
from app.db.models import Project, Agent, Task
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.schemas.agent import AgentCreate, AgentResponse, AgentUpdate


def test_project_model_and_schemas():
    project_data = {
        "id": "PROJ-V2",
        "name": "V2 Control Tower",
        "description": "Schema alignment test",
        "repo_root": "/home/user/repo",
        "task_prefix": "CTV2",
        "graph_status": "active",
        "embed_status": "ready",
        "node_count": 42,
        "edge_count": 10
    }
    proj_create = ProjectCreate(**project_data)
    assert proj_create.repo_root == "/home/user/repo"
    assert proj_create.task_prefix == "CTV2"
    assert proj_create.graph_status == "active"

    proj = Project(**proj_create.model_dump())
    assert proj.repo_root == "/home/user/repo"
    assert proj.task_prefix == "CTV2"
    assert proj.graph_status == "active"
    assert proj.node_count == 42

    proj_resp = ProjectResponse.model_validate(proj)
    assert proj_resp.repo_root == "/home/user/repo"
    assert proj_resp.task_prefix == "CTV2"
    assert proj_resp.node_count == 42


def test_agent_model_and_schemas():
    agent_data = {
        "id": "AGENT-V2",
        "name": "Gemini Flash",
        "type": "ai",
        "model": "gemini-3.6-flash",
        "effort": "high",
        "cli": "agy",
        "total_tasks_executed": 15,
        "total_tasks_reviewed": 5,
        "success_rate": 0.95,
        "avg_review_rounds": 1.2,
        "strengths": ["fast", "accurate"],
        "weaknesses": []
    }
    ag_create = AgentCreate(**agent_data)
    assert ag_create.model == "gemini-3.6-flash"
    assert ag_create.effort == "high"
    assert ag_create.cli == "agy"
    assert ag_create.total_tasks_executed == 15
    assert ag_create.success_rate == 0.95

    agent = Agent(**ag_create.model_dump())
    assert agent.model == "gemini-3.6-flash"
    assert agent.effort == "high"
    assert agent.cli == "agy"

    ag_resp = AgentResponse.model_validate(agent)
    assert ag_resp.model == "gemini-3.6-flash"
    assert ag_resp.cli == "agy"
    assert ag_resp.total_tasks_executed == 15


def test_api_projects_and_agents_new_fields(client, db):
    # Create project via API
    p_resp = client.post("/projects", json={
        "id": "proj-align",
        "name": "Alignment Project",
        "repo_root": "/path/to/repo",
        "task_prefix": "ALIGN",
        "graph_status": "done"
    })
    assert p_resp.status_code == 201
    p_data = p_resp.json()
    assert p_data["repo_root"] == "/path/to/repo"
    assert p_data["task_prefix"] == "ALIGN"

    # Get project via API
    get_p = client.get("/projects/proj-align")
    assert get_p.status_code == 200
    assert get_p.json()["repo_root"] == "/path/to/repo"

    # Create agent via API
    a_resp = client.post("/agents", json={
        "id": "agent-align",
        "type": "ai",
        "model": "gpt-5.6-sol",
        "effort": "high",
        "cli": "codex"
    })
    assert a_resp.status_code == 201
    a_data = a_resp.json()
    assert a_data["model"] == "gpt-5.6-sol"
    assert a_data["effort"] == "high"
    assert a_data["cli"] == "codex"

    # Update agent via API
    patch_a = client.patch("/agents/agent-align", json={
        "effort": "low",
        "total_tasks_executed": 3
    })
    assert patch_a.status_code == 200
    assert patch_a.json()["effort"] == "low"
    assert patch_a.json()["total_tasks_executed"] == 3
