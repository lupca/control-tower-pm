from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session as DBSession

from app.db.base import get_db
from app.db.models import Project, Task
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.schemas.task import TaskResponse

router = APIRouter(prefix="/projects", tags=["projects"])


def _compute_project_stats(db: DBSession, project_id: str, project_name: Optional[str] = None) -> Dict[str, int]:
    query_filter = (Task.project == project_id)
    if project_name and project_name != project_id:
        query_filter = query_filter | (Task.project == project_name)

    counts = (
        db.query(Task.status, func.count(Task.id))
        .filter(query_filter)
        .group_by(Task.status)
        .all()
    )

    stats: Dict[str, int] = {"total": 0}
    for status_str, count in counts:
        stats[status_str] = count
        stats["total"] += count
    return stats


@router.get("", response_model=List[ProjectResponse])
def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: DBSession = Depends(get_db)
):
    projects = db.query(Project).offset(skip).limit(limit).all()
    res = []
    for proj in projects:
        stats_dict = _compute_project_stats(db, proj.id, proj.name)
        proj_resp = ProjectResponse.model_validate(proj)
        proj_resp.stats = stats_dict
        res.append(proj_resp)
    return res


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project_in: ProjectCreate, db: DBSession = Depends(get_db)):
    existing = db.query(Project).filter(Project.id == project_in.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Project ID already exists")

    project = Project(**project_in.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)

    stats_dict = _compute_project_stats(db, project.id, project.name)
    proj_resp = ProjectResponse.model_validate(project)
    proj_resp.stats = stats_dict
    return proj_resp


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, db: DBSession = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    stats_dict = _compute_project_stats(db, project.id, project.name)
    proj_resp = ProjectResponse.model_validate(project)
    proj_resp.stats = stats_dict
    return proj_resp


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: str, project_in: ProjectUpdate, db: DBSession = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = project_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)

    stats_dict = _compute_project_stats(db, project.id, project.name)
    proj_resp = ProjectResponse.model_validate(project)
    proj_resp.stats = stats_dict
    return proj_resp


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: str, db: DBSession = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()


@router.get("/{project_id}/tasks", response_model=List[TaskResponse])
def list_project_tasks(
    project_id: str,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: DBSession = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    query_filter = (Task.project == project.id)
    if project.name and project.name != project.id:
        query_filter = query_filter | (Task.project == project.name)

    query = db.query(Task).filter(query_filter)
    if status:
        query = query.filter(Task.status == status)

    return query.offset(skip).limit(limit).all()
