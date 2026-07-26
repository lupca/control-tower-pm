from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class SessionBase(BaseModel):
    task_id: Optional[str] = None
    thread_id: Optional[str] = None
    current_gate: Optional[str] = None
    messages: List[Dict[str, Any]] = Field(default_factory=list)


class SessionCreate(SessionBase):
    pass


class SessionResponse(SessionBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
