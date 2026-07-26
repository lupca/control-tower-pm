import os
from typing import Tuple
from app.db.models import Task, Agent


def build_dispatch_command(task: Task, agent: Agent) -> Tuple[str, str, str]:
    """
    Build execution command, repo_root, and cli for dispatching a task to an agent.
    Returns: (command, repo_root, cli)
    """
    cli = agent.cli or "agy"
    repo_root = "/tmp"
    if task.project_rel and task.project_rel.repo_root:
        repo_root = task.project_rel.repo_root
    elif task.project:
        candidate = f"/home/lupca/projects/{task.project.lower()}"
        if os.path.exists(candidate):
            repo_root = candidate

    command = f"{cli} exec --task-id {task.id}"
    return command, repo_root, cli
