from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession

from app.db.base import get_db
from app.db.models import Session as SessionModel
from app.services.command_router import CommandRouter, format_command_result

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = "default"
    task_id: Optional[str] = None


class ChatResponse(BaseModel):
    type: str  # "command" or "chat"
    message: str
    result: Optional[Dict[str, Any]] = None


def get_or_create_session(thread_id: str, db: DBSession) -> SessionModel:
    db_session = getattr(db, "session", db)
    try:
        session = db_session.query(SessionModel).filter(SessionModel.thread_id == thread_id).first()
        if not session:
            session = SessionModel(thread_id=thread_id, messages=[])
            db_session.add(session)
            db_session.commit()
            db_session.refresh(session)
        return session
    except Exception:
        # Fallback if DB query fails
        return SessionModel(thread_id=thread_id, messages=[])


def save_message(session: SessionModel, role: str, content: str, db: DBSession):
    if not session or not hasattr(session, "thread_id"):
        return
    db_session = getattr(db, "session", db)
    try:
        messages = list(session.messages or [])
        messages.append({"role": role, "content": content})
        session.messages = messages
        if hasattr(session, "id") and session.id:
            db_session.add(session)
            db_session.commit()
    except Exception:
        pass


@router.post("", response_model=ChatResponse)
@router.post("/", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest, db: DBSession = Depends(get_db)):
    thread_id = req.thread_id or "default"
    db_session = get_or_create_session(thread_id, db)

    cmd_router = CommandRouter(db)
    command, args = cmd_router.parse(req.message)

    if command:
        result = await cmd_router.execute(command, args, thread_id)

        if "error" in result:
            response_text = f"❌ Error: {result['error']}"
        else:
            response_text = format_command_result(result)

        save_message(db_session, "user", req.message, db)
        save_message(db_session, "assistant", response_text, db)

        return ChatResponse(type="command", result=result, message=response_text)

    # Regular chat (no slash command)
    response_text = f"Received: {req.message}"
    save_message(db_session, "user", req.message, db)
    save_message(db_session, "assistant", response_text, db)

    return ChatResponse(type="chat", result=None, message=response_text)
