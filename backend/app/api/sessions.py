from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.db.base import get_db
from app.db.models import Session
from app.schemas.session import SessionCreate, SessionResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("", response_model=List[SessionResponse])
def list_sessions(db: DBSession = Depends(get_db)):
    return db.query(Session).all()


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(session_in: SessionCreate, db: DBSession = Depends(get_db)):
    session = Session(**session_in.model_dump())
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, db: DBSession = Depends(get_db)):
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
