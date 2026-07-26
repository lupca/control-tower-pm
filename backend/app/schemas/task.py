from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class TaskBase(BaseModel):
    project: str
    title: str
    priority: Optional[str] = None
    risk: Optional[str] = None
    executor: Optional[str] = None
    reviewer: Optional[str] = None
    acceptance_criteria: List[str] = Field(default_factory=list)
    files: List[str] = Field(default_factory=list)
    tests: List[str] = Field(default_factory=list)
    flows: List[str] = Field(default_factory=list)
    plan: Optional[str] = None
    result_ref: Optional[str] = None
    findings: List[str] = Field(default_factory=list)
    verdict: Optional[str] = None
    predicted_success: Optional[str] = None
    prediction_factors: Optional[Dict[str, Any]] = None
    deadline: Optional[date] = None


class TaskCreate(TaskBase):
    id: str


class TaskUpdate(BaseModel):
    project: Optional[str] = None
    title: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    risk: Optional[str] = None
    executor: Optional[str] = None
    reviewer: Optional[str] = None
    acceptance_criteria: Optional[List[str]] = None
    files: Optional[List[str]] = None
    tests: Optional[List[str]] = None
    flows: Optional[List[str]] = None
    plan: Optional[str] = None
    result_ref: Optional[str] = None
    findings: Optional[List[str]] = None
    verdict: Optional[str] = None
    predicted_success: Optional[str] = None
    prediction_factors: Optional[Dict[str, Any]] = None
    deadline: Optional[date] = None
    dispatched_at: Optional[datetime] = None
    in_review_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class TaskResponse(TaskBase):
    id: str
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    dispatched_at: Optional[datetime] = None
    in_review_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
