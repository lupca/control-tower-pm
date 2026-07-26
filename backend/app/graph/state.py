from enum import Enum
from typing import Literal, Optional, List
from pydantic import BaseModel, Field


class GateType(str, Enum):
    SPEC = "spec"
    PLAN = "plan"
    DISPATCH = "dispatch"
    REVIEW_ORDER = "review_order"
    VERDICT = "verdict"


class Mode(str, Enum):
    PLAN_ONLY = "plan-only"
    SUPERVISED = "supervised"
    BYPASS = "bypass"


class FourEyesViolation(Exception):
    """Raised when reviewer is the same as executor."""
    pass


class TaskState(BaseModel):
    # Input
    raw_input: str = ""

    # Task identity
    task_id: Optional[str] = None
    project: Optional[str] = None
    title: Optional[str] = None

    # Workflow
    current_gate: GateType = GateType.SPEC
    status: Literal["todo", "dispatched", "in-review", "done", "changes-requested"] = "todo"
    mode: Mode = Mode.SUPERVISED

    # Gate outputs
    acceptance_criteria: List[str] = Field(default_factory=list)
    files: List[str] = Field(default_factory=list)
    tests: List[str] = Field(default_factory=list)
    plan: Optional[str] = None

    # Actors
    executor: Optional[str] = None
    reviewer: Optional[str] = None

    # Review
    result_ref: Optional[str] = None
    findings: List[str] = Field(default_factory=list)
    verdict: Optional[Literal["pass", "changes"]] = None

    # Human-in-loop
    awaiting_approval: bool = False
    approval_prompt: Optional[str] = None
    approval: Optional[str] = None

    # Error
    error: Optional[str] = None
