---
id: CTV2-007
title: "Streamlit Task Dashboard"
status: done
priority: medium
risk: low
deadline: 2026-08-18
executor: "@antigravity-3.6-high"
reviewer: "@antigravity"
result_ref: "f41e472"
depends_on:
  - CTV2-002
files:
  - frontend/dashboard/app.py
  - frontend/dashboard/components.py
  - frontend/dashboard/Dockerfile
flows: []
tests: []
dispatched: 2026-07-26
in_review: 2026-07-26
predicted_success: high
prediction_factors:
  score: 0.85
  deductions:
    - "Streamlit very simple (+0.1)"
    - "View-only, no complex state (+0.05)"
created: 2026-07-26
updated: 2026-07-26
---

# CTV2-007: Streamlit Task Dashboard

> Dự án: [[projects/control-tower-v2/control-tower-v2]]

## Tiêu chí nghiệm thu (AC)

- [x] Dashboard chạy trên port 8501
- [x] Hiển thị tất cả tasks từ database
- [x] Filter by: status, project, priority
- [x] Sort by: created, updated, deadline
- [x] Task detail view (click để xem full info)
- [x] Auto-refresh mỗi 30s
- [x] Responsive layout
- [x] Docker container build thành công

## UI Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  Control Tower Dashboard                           [Refresh]    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Filters:                                                       │
│  [Status ▼] [Project ▼] [Priority ▼]                           │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ ID       │ Title              │ Status     │ Executor       ││
│  ├─────────────────────────────────────────────────────────────┤│
│  │ CTV2-001 │ Database Schema    │ 🟡 todo    │ -              ││
│  │ CTV2-002 │ FastAPI CRUD       │ 🟡 todo    │ -              ││
│  │ PMI-023  │ Fix inventory sync │ 🔵 dispatch│ @gemini-3.6    ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  Stats: 45 todo │ 12 dispatched │ 3 in-review │ 89 done        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Code

```python
import streamlit as st
import httpx
from datetime import datetime

st.set_page_config(
    page_title="Control Tower Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Fetch tasks from API
@st.cache_data(ttl=30)
def fetch_tasks(status=None, project=None):
    params = {}
    if status: params["status"] = status
    if project: params["project"] = project
    
    r = httpx.get(f"{API_URL}/api/tasks", params=params)
    return r.json()

# Filters
col1, col2, col3 = st.columns(3)
status = col1.selectbox("Status", ["all", "todo", "dispatched", "in-review", "done"])
project = col2.selectbox("Project", ["all"] + get_projects())
priority = col3.selectbox("Priority", ["all", "high", "medium", "low"])

# Table
tasks = fetch_tasks(
    status=None if status == "all" else status,
    project=None if project == "all" else project
)
st.dataframe(tasks, use_container_width=True)

# Stats
stats = {s: len([t for t in tasks if t["status"] == s]) for s in ["todo", "dispatched", "in-review", "done"]}
st.markdown(f"**Stats:** {stats['todo']} todo │ {stats['dispatched']} dispatched │ {stats['in-review']} in-review │ {stats['done']} done")
```

## Plan

1. Install streamlit: `pip install streamlit httpx`
2. Create basic app.py với data fetching
3. Add filter controls
4. Add stats row
5. Add task detail expander
6. Build Docker image

## Verification

```bash
streamlit run app.py --server.port 8501
# Browser: localhost:8501
# Should see task table with filters
```
