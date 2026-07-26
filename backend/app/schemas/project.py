from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    repo_root: Optional[str] = None
    task_prefix: Optional[str] = None
    graph_status: Optional[str] = "pending"
    embed_status: Optional[str] = "pending"
    daemon_status: Optional[str] = "stopped"
    node_count: Optional[int] = 0
    edge_count: Optional[int] = 0
    patterns_exportable: Optional[bool] = False


class ProjectCreate(ProjectBase):
    id: str


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    repo_root: Optional[str] = None
    task_prefix: Optional[str] = None
    graph_status: Optional[str] = None
    embed_status: Optional[str] = None
    daemon_status: Optional[str] = None
    node_count: Optional[int] = None
    edge_count: Optional[int] = None
    patterns_exportable: Optional[bool] = None


class ProjectResponse(ProjectBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    stats: Optional[Dict[str, int]] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)
