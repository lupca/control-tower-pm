from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.tasks import router as tasks_router
from app.api.sessions import router as sessions_router
from app.api.audit import router as audit_router
from app.api.projects import router as projects_router
from app.api.agents import router as agents_router

app = FastAPI(title="Control Tower V2 Backend", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks_router)
app.include_router(tasks_router, prefix="/api")

app.include_router(sessions_router)
app.include_router(sessions_router, prefix="/api")

app.include_router(audit_router)
app.include_router(audit_router, prefix="/api")

app.include_router(projects_router)
app.include_router(projects_router, prefix="/api")

app.include_router(agents_router)
app.include_router(agents_router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "control-tower-v2-backend"}

