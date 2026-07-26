import uuid
from datetime import datetime, date
from sqlalchemy import (
    Column, String, Text, Date, DateTime, Integer, Float, Boolean, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.db.base import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    repo_root = Column(String(255), nullable=True)
    task_prefix = Column(String(10), nullable=True)
    task_dir = Column(String(255), nullable=True)
    graph_status = Column(Text, nullable=True, default="pending")
    embed_status = Column(String(50), nullable=True, default="pending")
    graph_embedded = Column(Text, nullable=True)
    daemon_status = Column(String(50), nullable=True, default="stopped")
    daemon_watch = Column(Text, nullable=True)
    node_count = Column(Integer, default=0)
    edge_count = Column(Integer, default=0)
    patterns_exportable = Column(Boolean, default=False)
    status = Column(String(20), default="active")
    done_count = Column(Integer, default=0)
    total_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Agent(Base):
    __tablename__ = "agents"

    id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=True)
    role = Column(Text, nullable=True)
    type = Column(String(20), nullable=False, default="ai")
    status = Column(String(20), default="active")
    model = Column(String(100), nullable=True)
    effort = Column(String(10), nullable=True)
    cli = Column(String(20), nullable=True)
    total_tasks_executed = Column(Integer, default=0)
    total_tasks_reviewed = Column(Integer, default=0)
    success_rate = Column(Float, default=1.0)
    avg_review_rounds = Column(Float, default=1.0)
    strengths = Column(JSON, default=list)
    weaknesses = Column(JSON, default=list)
    recent_trend = Column(String(20), nullable=True)
    superseded_by = Column(JSON, default=list)
    last_active = Column(Date, nullable=True)
    system_prompt = Column(Text, nullable=True)
    file_path = Column(String(255), nullable=True)
    stats = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(50), primary_key=True)
    project = Column(String(50), nullable=False, index=True)
    title = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="todo", index=True)
    priority = Column(String(10), nullable=True)
    risk = Column(String(10), nullable=True)
    executor = Column(String(50), nullable=True)
    reviewer = Column(String(50), nullable=True)
    acceptance_criteria = Column(JSON, default=list)
    files = Column(JSON, default=list)
    tests = Column(JSON, default=list)
    flows = Column(JSON, default=list)
    plan = Column(Text, nullable=True)
    result_ref = Column(String(255), nullable=True)
    findings = Column(JSON, default=list)
    verdict = Column(String(20), nullable=True)
    predicted_success = Column(String(20), nullable=True)
    prediction_factors = Column(JSON, nullable=True)
    deadline = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    dispatched_at = Column(DateTime, nullable=True)
    in_review_at = Column(DateTime, nullable=True)
    done_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    body = Column(Text, nullable=True)
    file_path = Column(String(255), nullable=True)
    depends_on = Column(JSON, default=list)

    sessions = relationship("Session", back_populates="task", cascade="all, delete-orphan")


class Knowledge(Base):
    __tablename__ = "knowledge"

    id = Column(String(255), primary_key=True)
    title = Column(String(255), nullable=True)
    category = Column(String(50), nullable=True, index=True)
    path = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    metadata_info = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String(50), ForeignKey("tasks.id"), nullable=True, index=True)
    thread_id = Column(String(100), nullable=True)
    current_gate = Column(String(20), nullable=True)
    mode = Column(String(20), nullable=True)
    state = Column(JSON, default=dict)
    messages = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    task = relationship("Task", back_populates="sessions")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(100), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    actor = Column(String(100), nullable=True)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
