import pytest
from app.graph.state import FourEyesViolation, GateType, Mode


def test_full_flow_happy_path(graph, db):
    # 1. Create task
    result = graph.invoke({"raw_input": "/pm add tests --project demo"})
    assert result["task_id"] == "DEMO-001"
    assert result["current_gate"] == GateType.SPEC

    # 2. Approve spec
    result = graph.invoke({"approval": "approve"})
    assert result["current_gate"] == GateType.PLAN

    # 3. Approve plan
    result = graph.invoke({"approval": "approve"})
    assert result["current_gate"] == GateType.DISPATCH

    # 4. Dispatch
    result = graph.invoke({"executor": "@gemini-3.6"})
    assert result["status"] == "dispatched"

    # 5. Simulate executor done
    db.update_task("DEMO-001", result_ref="abc123")

    # 6. Review order
    result = graph.invoke({"raw_input": "/review-order DEMO-001"})
    assert result["status"] == "in-review"

    # 7. Verdict pass
    result = graph.invoke({
        "verdict": "pass",
        "reviewer": "@antigravity"  # different from executor
    })
    assert result["status"] == "done"


def test_four_eyes_blocked(graph):
    # Set executor to @alice
    graph.invoke({"raw_input": "/pm four eyes task --project test", "mode": Mode.BYPASS, "executor": "@alice"})

    # Try verdict with same reviewer @alice
    with pytest.raises(FourEyesViolation):
        graph.invoke({
            "verdict": "pass",
            "reviewer": "@alice",  # same as executor!
            "executor": "@alice"
        })


def test_bypass_mode_no_approvals(graph):
    result = graph.invoke({
        "raw_input": "/pm quick fix --project demo",
        "mode": Mode.BYPASS
    })

    # Should go straight to dispatched without pausing
    assert result["status"] == "dispatched"
    assert result["awaiting_approval"] is False


def test_verdict_changes_requested(graph, db):
    # Dispatch task
    result = graph.invoke({"raw_input": "/pm retry test --project demo", "mode": Mode.BYPASS})
    assert result["status"] == "dispatched"

    # Review order
    result = graph.invoke({"raw_input": "/review-order DEMO-001"})
    assert result["status"] == "in-review"

    # Verdict changes
    result = graph.invoke({
        "verdict": "changes",
        "reviewer": "@antigravity",
        "executor": "@gemini-3.6"
    })
    assert result["status"] == "changes-requested"
