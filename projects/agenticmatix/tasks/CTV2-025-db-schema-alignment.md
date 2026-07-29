---
id: CTV2-025
title: "DB Schema alignment với v2 design"
status: done
priority: critical
risk: medium
executor: "@gemini-3.6-flash"
reviewer: "@gpt-5.6-sol"
deadline: 2026-07-28
created: 2026-07-26
updated: 2026-07-26
depends_on: []
files:
  - backend/alembic/versions/003_schema_alignment.py
  - backend/app/db/models.py
  - backend/app/schemas/project.py
  - backend/app/schemas/agent.py
tests:
  - Migration runs without error
  - All CRITICAL fields exist
  - FK constraint works
  - Existing data preserved
  - API endpoints return new fields
---

# CTV2-025: DB Schema Alignment

## Context
Gap analysis phát hiện nhiều fields CRITICAL thiếu, block CTV2-031 (Agent Runner).

## Priority Levels

### 🔴 CRITICAL (Block CTV2-031)

```sql
-- 1. projects: cần repo_root để dispatch biết chạy ở đâu
ALTER TABLE projects ADD COLUMN repo_root VARCHAR(255);
ALTER TABLE projects ADD COLUMN task_prefix VARCHAR(10);

-- 2. agents: cần model, effort, cli để build dispatch command
ALTER TABLE agents ADD COLUMN type VARCHAR(10) NOT NULL DEFAULT 'ai';
ALTER TABLE agents ADD COLUMN model VARCHAR(100);
ALTER TABLE agents ADD COLUMN effort VARCHAR(10) DEFAULT 'medium';
ALTER TABLE agents ADD COLUMN cli VARCHAR(20);

-- 3. agents: performance stats cho agent selection
ALTER TABLE agents ADD COLUMN total_tasks_executed INTEGER DEFAULT 0;
ALTER TABLE agents ADD COLUMN total_tasks_reviewed INTEGER DEFAULT 0;
ALTER TABLE agents ADD COLUMN success_rate DECIMAL(3,2) DEFAULT 1.0;

-- 4. tasks: FK constraint
ALTER TABLE tasks 
  ADD CONSTRAINT fk_tasks_project 
  FOREIGN KEY (project) REFERENCES projects(id);

-- 5. tasks: missing timestamp
ALTER TABLE tasks ADD COLUMN in_review_at TIMESTAMP;
```

### 🟡 MODERATE (Agent Selection)

```sql
-- agents: advanced stats
ALTER TABLE agents ADD COLUMN avg_review_rounds DECIMAL(3,1) DEFAULT 1.0;
ALTER TABLE agents ADD COLUMN strengths JSONB DEFAULT '[]';
ALTER TABLE agents ADD COLUMN weaknesses JSONB DEFAULT '[]';
ALTER TABLE agents ADD COLUMN recent_trend VARCHAR(20);
ALTER TABLE agents ADD COLUMN last_active DATE;

-- projects: graph integration
ALTER TABLE projects ADD COLUMN graph_status VARCHAR(20) DEFAULT 'pending';
ALTER TABLE projects ADD COLUMN embed_status VARCHAR(20) DEFAULT 'pending';
ALTER TABLE projects ADD COLUMN node_count INTEGER DEFAULT 0;
ALTER TABLE projects ADD COLUMN edge_count INTEGER DEFAULT 0;
```

### 🟢 MINOR (Can defer)

```sql
-- agents: deprecation tracking
ALTER TABLE agents ADD COLUMN superseded_by JSONB DEFAULT '[]';

-- projects: extra
ALTER TABLE projects ADD COLUMN daemon_status VARCHAR(20) DEFAULT 'stopped';
ALTER TABLE projects ADD COLUMN patterns_exportable BOOLEAN DEFAULT FALSE;

-- knowledge: restructure (separate task)
-- audit_log: add session_id
```

## Alembic Migration

```python
# backend/alembic/versions/003_schema_alignment.py
"""Schema alignment with v2 design - CRITICAL fixes

Revision ID: 003_schema_alignment
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '003_schema_alignment'
down_revision = '002_schema_v2'  # or latest
branch_labels = None
depends_on = None


def upgrade():
    # === CRITICAL: Projects ===
    op.add_column('projects', sa.Column('repo_root', sa.String(255)))
    op.add_column('projects', sa.Column('task_prefix', sa.String(10)))
    
    # === CRITICAL: Agents ===
    op.add_column('agents', sa.Column('type', sa.String(10), nullable=False, server_default='ai'))
    op.add_column('agents', sa.Column('model', sa.String(100)))
    op.add_column('agents', sa.Column('effort', sa.String(10), server_default='medium'))
    op.add_column('agents', sa.Column('cli', sa.String(20)))
    op.add_column('agents', sa.Column('total_tasks_executed', sa.Integer, server_default='0'))
    op.add_column('agents', sa.Column('total_tasks_reviewed', sa.Integer, server_default='0'))
    op.add_column('agents', sa.Column('success_rate', sa.Numeric(3, 2), server_default='1.0'))
    
    # === CRITICAL: Tasks FK ===
    # First ensure all project values exist in projects table
    op.execute("""
        INSERT INTO projects (id, name)
        SELECT DISTINCT project, project 
        FROM tasks 
        WHERE project NOT IN (SELECT id FROM projects)
        ON CONFLICT DO NOTHING
    """)
    
    op.create_foreign_key(
        'fk_tasks_project', 'tasks', 'projects',
        ['project'], ['id']
    )
    
    op.add_column('tasks', sa.Column('in_review_at', sa.DateTime(timezone=True)))
    
    # === MODERATE: Agent stats ===
    op.add_column('agents', sa.Column('avg_review_rounds', sa.Numeric(3, 1), server_default='1.0'))
    op.add_column('agents', sa.Column('strengths', postgresql.JSONB, server_default='[]'))
    op.add_column('agents', sa.Column('weaknesses', postgresql.JSONB, server_default='[]'))
    op.add_column('agents', sa.Column('recent_trend', sa.String(20)))
    op.add_column('agents', sa.Column('last_active', sa.Date))
    
    # === MODERATE: Projects graph ===
    op.add_column('projects', sa.Column('graph_status', sa.String(20), server_default='pending'))
    op.add_column('projects', sa.Column('embed_status', sa.String(20), server_default='pending'))
    op.add_column('projects', sa.Column('node_count', sa.Integer, server_default='0'))
    op.add_column('projects', sa.Column('edge_count', sa.Integer, server_default='0'))


def downgrade():
    # Remove in reverse order
    op.drop_column('projects', 'edge_count')
    op.drop_column('projects', 'node_count')
    op.drop_column('projects', 'embed_status')
    op.drop_column('projects', 'graph_status')
    
    op.drop_column('agents', 'last_active')
    op.drop_column('agents', 'recent_trend')
    op.drop_column('agents', 'weaknesses')
    op.drop_column('agents', 'strengths')
    op.drop_column('agents', 'avg_review_rounds')
    
    op.drop_column('tasks', 'in_review_at')
    op.drop_constraint('fk_tasks_project', 'tasks', type_='foreignkey')
    
    op.drop_column('agents', 'success_rate')
    op.drop_column('agents', 'total_tasks_reviewed')
    op.drop_column('agents', 'total_tasks_executed')
    op.drop_column('agents', 'cli')
    op.drop_column('agents', 'effort')
    op.drop_column('agents', 'model')
    op.drop_column('agents', 'type')
    
    op.drop_column('projects', 'task_prefix')
    op.drop_column('projects', 'repo_root')
```

## Model Updates

```python
# backend/app/db/models.py updates

class Project(Base):
    __tablename__ = "projects"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    repo_root = Column(String(255), nullable=True)        # NEW
    task_prefix = Column(String(10), nullable=True)       # NEW
    status = Column(String(20), nullable=False, default="active")
    
    # Graph integration
    graph_status = Column(String(20), default="pending")  # NEW
    embed_status = Column(String(20), default="pending")  # NEW
    node_count = Column(Integer, default=0)               # NEW
    edge_count = Column(Integer, default=0)               # NEW
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tasks = relationship("Task", back_populates="project_rel")


class Agent(Base):
    __tablename__ = "agents"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=True)             # Keep for display
    type = Column(String(10), nullable=False, default="ai")  # NEW: ai, human
    status = Column(String(20), nullable=False, default="active")
    
    # Model config (CRITICAL for dispatch)
    model = Column(String(100), nullable=True)            # NEW
    effort = Column(String(10), default="medium")         # NEW
    cli = Column(String(20), nullable=True)               # NEW: agy, codex, claude
    
    # Performance stats
    total_tasks_executed = Column(Integer, default=0)     # NEW
    total_tasks_reviewed = Column(Integer, default=0)     # NEW
    success_rate = Column(Numeric(3, 2), default=1.0)     # NEW
    avg_review_rounds = Column(Numeric(3, 1), default=1.0)# NEW
    
    # Characteristics
    strengths = Column(JSON, default=list)                # NEW
    weaknesses = Column(JSON, default=list)               # NEW
    recent_trend = Column(String(20), nullable=True)      # NEW
    last_active = Column(Date, nullable=True)             # NEW
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Task(Base):
    # ... existing fields ...
    
    # Update project to be FK
    project = Column(String(50), ForeignKey('projects.id'), nullable=False, index=True)
    
    # Add missing timestamp
    in_review_at = Column(DateTime(timezone=True), nullable=True)  # NEW
    
    # Relationship
    project_rel = relationship("Project", back_populates="tasks")
```

## Acceptance Criteria

- [ ] AC1: Migration runs: `alembic upgrade head`
- [ ] AC2: CRITICAL fields exist: repo_root, model, effort, cli
- [ ] AC3: FK constraint works: inserting task with invalid project fails
- [ ] AC4: Existing data preserved (test with current DB)
- [ ] AC5: models.py updated with new columns
- [ ] AC6: Pydantic schemas updated (ProjectResponse, AgentResponse)
- [ ] AC7: API returns new fields: GET /api/projects/{id} shows repo_root
- [ ] AC8: Agent create/update accepts model, effort, cli
