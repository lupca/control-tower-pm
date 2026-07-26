from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from sqlalchemy.orm import Session as DBSession

from app.db.base import get_db
from app.db.models import AuditLog

router = APIRouter(prefix="/audit", tags=["audit"])


class AuditLogResponse(BaseModel):
    id: int
    task_id: Optional[str] = None
    action: str
    actor: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


@router.get("", response_model=List[AuditLogResponse])
def list_audit_logs(task_id: Optional[str] = None, db: DBSession = Depends(get_db)):
    query = db.query(AuditLog)
    if task_id:
        query = query.filter(AuditLog.task_id == task_id)
    return query.all()
