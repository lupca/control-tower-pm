import pytest
from app.db.models import AuditLog


def test_audit_api(client, db):
    audit = AuditLog(task_id="AUD-001", action="gate_pass", actor="@user", details={"gate": "spec"})
    db.add(audit)

    res = client.get("/audit")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1

    res_filtered = client.get("/audit?task_id=AUD-001")
    assert res_filtered.status_code == 200
    assert len(res_filtered.json()) == 1
    assert res_filtered.json()[0]["action"] == "gate_pass"
