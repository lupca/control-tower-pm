# Database Design V2 - Control Tower

## Overview
Migrate từ File-Over-API (Markdown) sang PostgreSQL với full data model.

## Entity Relationship

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│  projects   │──────<│    tasks    │──────<│  sessions   │
└─────────────┘       └─────────────┘       └─────────────┘
                            │
                            │
                      ┌─────┴─────┐
                      │           │
                ┌─────────┐ ┌─────────────┐
                │ agents  │ │  audit_log  │
                └─────────┘ └─────────────┘
                      
┌─────────────┐
│  knowledge  │  (standalone)
└─────────────┘
```

## Tables

### 1. projects
```sql
CREATE TABLE projects (
    id VARCHAR(50) PRIMARY KEY,           -- slug: topvnsport-pmi
    name VARCHAR(100) NOT NULL,           -- TopVNSport - PMI
    description TEXT,
    repo_root VARCHAR(255),               -- /home/lupca/projects/topvnsport
    task_prefix VARCHAR(10),              -- PMI, OMS, CT
    
    -- Code Review Graph status
    graph_status VARCHAR(20) DEFAULT 'pending',  -- pending, building, ready
    embed_status VARCHAR(20) DEFAULT 'pending',
    daemon_status VARCHAR(20) DEFAULT 'stopped',
    node_count INTEGER DEFAULT 0,
    edge_count INTEGER DEFAULT 0,
    
    patterns_exportable BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 2. tasks (expanded)
```sql
CREATE TABLE tasks (
    id VARCHAR(20) PRIMARY KEY,           -- PMI-001, CT-019
    project_id VARCHAR(50) REFERENCES projects(id),
    
    title TEXT NOT NULL,
    body TEXT,                            -- Full markdown content
    status VARCHAR(20) DEFAULT 'todo',    -- todo, ready, dispatched, in-review, changes-requested, done
    priority VARCHAR(10),                 -- low, medium, high, critical
    risk VARCHAR(10),                     -- low, medium, high
    
    -- Assignment
    executor VARCHAR(50),                 -- @antigravity-3.6-high
    reviewer VARCHAR(50),                 -- @antigravity
    
    -- Spec & Plan
    acceptance_criteria JSONB DEFAULT '[]',
    files JSONB DEFAULT '[]',
    tests JSONB DEFAULT '[]',
    flows JSONB DEFAULT '[]',
    plan TEXT,
    
    -- Review
    result_ref VARCHAR(255),              -- branch/commit/PR
    findings JSONB DEFAULT '[]',
    verdict VARCHAR(20),                  -- pass, changes
    
    -- Prediction (from code-review-graph)
    predicted_success VARCHAR(10),
    prediction_factors JSONB,
    
    -- Dates
    deadline DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    dispatched_at TIMESTAMP,
    in_review_at TIMESTAMP,
    done_at TIMESTAMP,
    
    -- Chat session
    session_id VARCHAR(36)
);

CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_executor ON tasks(executor);
```

### 3. agents (NEW)
```sql
CREATE TABLE agents (
    id VARCHAR(50) PRIMARY KEY,           -- @antigravity-3.6-high
    type VARCHAR(10) NOT NULL,            -- ai, human
    status VARCHAR(20) DEFAULT 'active',  -- active, deprecated
    
    -- Model config (for AI agents)
    model VARCHAR(100),                   -- gemini-3.6-flash, claude-opus-4-5
    effort VARCHAR(10),                   -- low, medium, high
    cli VARCHAR(20),                      -- agy, claude, codex
    
    -- Performance stats
    total_tasks_executed INTEGER DEFAULT 0,
    total_tasks_reviewed INTEGER DEFAULT 0,
    success_rate DECIMAL(3,2) DEFAULT 1.0,
    avg_review_rounds DECIMAL(3,1) DEFAULT 1.0,
    
    -- Characteristics
    strengths JSONB DEFAULT '[]',
    weaknesses JSONB DEFAULT '[]',
    recent_trend VARCHAR(20),             -- improving, stable, declining
    
    -- Deprecation
    superseded_by JSONB DEFAULT '[]',     -- list of agent IDs
    
    last_active DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 4. knowledge (NEW)
```sql
CREATE TABLE knowledge (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(100) UNIQUE NOT NULL,    -- adr-001-langgraph
    type VARCHAR(30) NOT NULL,            -- decision, guide, research, metric, tool, pattern, convention
    
    title VARCHAR(255) NOT NULL,
    content TEXT,                         -- Full markdown
    summary TEXT,                         -- Short description
    
    tags JSONB DEFAULT '[]',
    project_id VARCHAR(50) REFERENCES projects(id),  -- NULL = cross-project
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_knowledge_type ON knowledge(type);
CREATE INDEX idx_knowledge_project ON knowledge(project_id);
```

### 5. sessions (existing, minor changes)
```sql
CREATE TABLE sessions (
    id VARCHAR(36) PRIMARY KEY,
    task_id VARCHAR(20) REFERENCES tasks(id),
    thread_id VARCHAR(100),
    
    current_gate VARCHAR(20),             -- spec, plan, dispatch, review, verdict
    mode VARCHAR(20) DEFAULT 'supervised', -- plan-only, supervised, bypass
    
    messages JSONB DEFAULT '[]',
    state JSONB DEFAULT '{}',             -- LangGraph state snapshot
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 6. audit_log (existing)
```sql
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(20),
    session_id VARCHAR(36),
    
    action VARCHAR(50) NOT NULL,          -- gate:spec:pass, dispatch:execute, verdict:pass
    actor VARCHAR(50),                    -- @antigravity, @user
    details JSONB,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_task ON audit_log(task_id);
CREATE INDEX idx_audit_action ON audit_log(action);
```

## API Endpoints (new/updated)

```
# Projects
GET    /api/projects              # List all projects with stats
GET    /api/projects/{id}         # Project detail
POST   /api/projects              # Create project
PATCH  /api/projects/{id}         # Update project
GET    /api/projects/{id}/tasks   # Tasks in project

# Tasks (existing + enhanced)
GET    /api/tasks                 # List with filters (?project=X&status=Y)
GET    /api/tasks/{id}            # Task detail
POST   /api/tasks                 # Create task
PATCH  /api/tasks/{id}            # Update task
GET    /api/tasks/{id}/messages   # Chat history
GET    /api/tasks/{id}/audit      # Audit trail

# Agents
GET    /api/agents                # List all agents
GET    /api/agents/{id}           # Agent detail with stats
POST   /api/agents                # Create agent
PATCH  /api/agents/{id}           # Update agent

# Knowledge
GET    /api/knowledge             # List with filters (?type=X)
GET    /api/knowledge/{slug}      # Knowledge item
POST   /api/knowledge             # Create
PATCH  /api/knowledge/{slug}      # Update

# Stats (for dashboard)
GET    /api/stats/overview        # KPIs: total tasks, done, active, by status
GET    /api/stats/projects        # Per-project breakdown
GET    /api/stats/agents          # Agent performance

# Chat
POST   /api/chat                  # Send message (SSE streaming)
```

## Migration Strategy

1. Create new tables with Alembic migration
2. Script to parse markdown files:
   - `projects/*/tasks/*.md` → tasks table
   - `knowledge/agents/@*.md` → agents table
   - `knowledge/**/*.md` → knowledge table
   - `index.md` PROJECT REGISTRY → projects table
3. Verify data integrity
4. Update LangGraph to use new schema
