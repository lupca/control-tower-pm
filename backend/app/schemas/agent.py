from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class AgentBase(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    type: str = "ai"
    status: Optional[str] = "active"
    model: Optional[str] = None
    effort: Optional[str] = "medium"
    cli: Optional[str] = None
    total_tasks_executed: Optional[int] = 0
    total_tasks_reviewed: Optional[int] = 0
    success_rate: Optional[float] = 1.0
    avg_review_rounds: Optional[float] = 1.0
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    recent_trend: Optional[str] = None
    superseded_by: List[str] = Field(default_factory=list)
    last_active: Optional[date] = None
    system_prompt: Optional[str] = None
    file_path: Optional[str] = None


class AgentCreate(AgentBase):
    id: str


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    model: Optional[str] = None
    effort: Optional[str] = None
    cli: Optional[str] = None
    total_tasks_executed: Optional[int] = None
    total_tasks_reviewed: Optional[int] = None
    success_rate: Optional[float] = None
    avg_review_rounds: Optional[float] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    recent_trend: Optional[str] = None
    superseded_by: Optional[List[str]] = None
    last_active: Optional[date] = None
    system_prompt: Optional[str] = None
    file_path: Optional[str] = None


class AgentResponse(AgentBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
