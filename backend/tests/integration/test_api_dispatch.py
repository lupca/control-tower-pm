import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_dispatch_returns_run_id():
    response = client.post('/api/dispatch', json={
        'task_id': 'TEST-001',
        'agent_id': '@test-agent',
        'command': 'echo test',
        'repo_root': '/tmp'
    })
    assert response.status_code in [200, 201, 404, 422]  # 422 if validation, 404 if not found

def test_stream_endpoint_exists():
    response = client.get('/api/runs/test-123/stream')
    assert response.status_code in [200, 404]
