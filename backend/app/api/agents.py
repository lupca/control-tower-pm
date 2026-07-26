from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session as DBSession

from app.db.base import get_db
from app.db.models import Agent, Task
from app.schemas.agent import AgentCreate, AgentResponse, AgentUpdate

router = APIRouter(prefix="/agents", tags=["agents"])


def _enrich_agent_stats(db: DBSession, agent: Agent) -> AgentResponse:
    executed_count = db.query(func.count(Task.id)).filter(Task.executor == agent.id).scalar() or 0
    reviewed_count = db.query(func.count(Task.id)).filter(Task.reviewer == agent.id).scalar() or 0

    agent_resp = AgentResponse.model_validate(agent)
    if executed_count > 0:
        agent_resp.total_tasks_executed = max(agent.total_tasks_executed or 0, executed_count)
        passed_count = (
            db.query(func.count(Task.id))
            .filter(Task.executor == agent.id, Task.verdict == "pass")
            .scalar() or 0
        )
        agent_resp.success_rate = round(passed_count / executed_count, 2)
    if reviewed_count > 0:
        agent_resp.total_tasks_reviewed = max(agent.total_tasks_reviewed or 0, reviewed_count)

    return agent_resp


@router.get("", response_model=List[AgentResponse])
def list_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: DBSession = Depends(get_db)
):
    agents = db.query(Agent).offset(skip).limit(limit).all()
    return [_enrich_agent_stats(db, ag) for ag in agents]


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
def create_agent(agent_in: AgentCreate, db: DBSession = Depends(get_db)):
    existing = db.query(Agent).filter(Agent.id == agent_in.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Agent ID already exists")

    agent = Agent(**agent_in.model_dump())
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return _enrich_agent_stats(db, agent)


@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: str, db: DBSession = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return _enrich_agent_stats(db, agent)


@router.patch("/{agent_id}", response_model=AgentResponse)
def update_agent(agent_id: str, agent_in: AgentUpdate, db: DBSession = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    update_data = agent_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)

    db.commit()
    db.refresh(agent)
    return _enrich_agent_stats(db, agent)


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(agent_id: str, db: DBSession = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    db.delete(agent)
    db.commit()
