import re
from datetime import datetime
from typing import Tuple, Optional, Dict, Any
from app.graph.builder import get_graph
from app.graph.state import TaskState, GateType, FourEyesViolation

COMMANDS = {
    "/pm": "create_task",
    "/dispatch": "dispatch_task",
    "/review-order": "review_order",
    "/verdict": "verdict",
    "/status": "get_status",
    "/help": "show_help",
}


def format_command_result(result: Dict[str, Any]) -> str:
    """Format command result dictionary into human-readable chat response text."""
    if "error" in result:
        return f"❌ Error: {result['error']}"

    action = result.get("action")
    if action == "task_created":
        ac_str = "\n".join(f"- {ac}" for ac in result.get("acceptance_criteria", []))
        ac_section = f"\nAcceptance Criteria:\n{ac_str}" if ac_str else ""
        return (
            f"✅ Task created: {result.get('task_id')} - {result.get('title')}\n"
            f"Gate: {result.get('current_gate')}{ac_section}"
        )
    elif action == "dispatched":
        return (
            f"🚀 Task {result.get('task_id')} dispatched to {result.get('executor')}\n"
            f"Status: {result.get('status')}"
        )
    elif action == "review_ordered":
        return (
            f"🔍 Review requested for task {result.get('task_id')} by {result.get('reviewer')}\n"
            f"Status: {result.get('status')}"
        )
    elif action == "verdict_recorded":
        return (
            f"📋 Verdict recorded for task {result.get('task_id')}: {result.get('verdict')}\n"
            f"Status: {result.get('status')}"
        )
    elif action == "status":
        return (
            f"📊 Task {result.get('task_id')} Status:\n"
            f"Project: {result.get('project')}\n"
            f"Title: {result.get('title')}\n"
            f"Status: {result.get('status')}\n"
            f"Gate: {result.get('current_gate')}\n"
            f"Executor: {result.get('executor') or 'None'}\n"
            f"Reviewer: {result.get('reviewer') or 'None'}\n"
            f"Verdict: {result.get('verdict') or 'None'}"
        )
    elif action == "help":
        cmds = result.get("commands", {})
        cmds_str = "\n".join(f"• `{cmd}`: {desc}" for cmd, desc in cmds.items())
        return f"Available commands:\n{cmds_str}"

    return str(result)


class CommandRouter:
    def __init__(self, db_session=None, graph=None):
        self.db = db_session
        self.graph = graph or get_graph()

    def parse(self, message: str) -> Tuple[Optional[str], str]:
        """
        Parse message for slash command.
        Returns: (command_name, args) or (None, original_message)
        """
        message = message.strip()
        if not message.startswith("/"):
            return None, message

        parts = message.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        if cmd in COMMANDS:
            return COMMANDS[cmd], args

        return None, message

    async def execute(self, command: str, args: str, session_id: str) -> dict:
        """Execute command and return result."""
        handler = getattr(self, f"_handle_{command}", None)
        if not handler:
            return {"error": f"Unknown command: {command}"}
        return await handler(args, session_id)

    def _extract_flag(self, args: str, flag: str) -> Optional[str]:
        pattern = rf"{re.escape(flag)}\s+([^\s]+)"
        match = re.search(pattern, args)
        return match.group(1) if match else None

    def _remove_flags(self, args: str) -> str:
        cleaned = re.sub(r"--\w+\s+[^\s]+", "", args)
        return cleaned.strip()

    def _generate_task_id(self, project: str) -> str:
        prefix = project.upper()
        if not self.db:
            return f"{prefix}-001"
        from app.db.models import Task
        db_session = getattr(self.db, "session", self.db)
        try:
            existing_ids = [
                t.id for t in db_session.query(Task.id).filter(Task.project.ilike(project)).all()
            ]
        except Exception:
            return f"{prefix}-001"

        max_num = 0
        pattern = re.compile(rf"^{re.escape(prefix)}-(\d+)$", re.IGNORECASE)
        for tid in existing_ids:
            match = pattern.match(tid)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
        return f"{prefix}-{max_num + 1:03d}"

    def _load_task_state(self, task_id: str) -> Optional[TaskState]:
        if not self.db:
            return None
        from app.db.models import Task
        db_session = getattr(self.db, "session", self.db)
        try:
            task = db_session.query(Task).filter(Task.id == task_id).first()
        except Exception:
            return None

        if not task:
            return None

        return TaskState(
            task_id=task.id,
            project=task.project,
            title=task.title,
            status=task.status or "todo",
            executor=task.executor,
            reviewer=task.reviewer,
            acceptance_criteria=task.acceptance_criteria or [],
            files=task.files or [],
            tests=task.tests or [],
            plan=task.plan,
            result_ref=task.result_ref,
            findings=task.findings or [],
            verdict=task.verdict,
        )

    def _save_or_update_task(self, task_id: str, updates: dict):
        if not self.db:
            return
        from app.db.models import Task
        db_session = getattr(self.db, "session", self.db)
        try:
            task = db_session.query(Task).filter(Task.id == task_id).first()
            if not task:
                task = Task(
                    id=task_id,
                    project=updates.get("project", "DEMO"),
                    title=updates.get("title", task_id),
                    status=updates.get("status", "todo"),
                    acceptance_criteria=updates.get("acceptance_criteria", []),
                    executor=updates.get("executor"),
                    reviewer=updates.get("reviewer"),
                    verdict=updates.get("verdict"),
                    plan=updates.get("plan"),
                )
                db_session.add(task)
            else:
                for k, v in updates.items():
                    if hasattr(task, k) and v is not None:
                        setattr(task, k, v)
            if hasattr(db_session, "commit"):
                db_session.commit()
        except Exception:
            pass

    async def _handle_create_task(self, args: str, session_id: str) -> dict:
        """
        /pm <task description> [--project <name>]
        Creates task and runs through Spec Gate.
        """
        project = self._extract_flag(args, "--project") or "DEMO"
        description = self._remove_flags(args)

        if not description:
            return {"error": "Usage: /pm <task description> [--project <name>]"}

        task_id = self._generate_task_id(project)
        state = TaskState(
            raw_input=f"/pm {description} --project {project}",
            project=project,
            title=description,
            task_id=task_id,
            current_gate=GateType.SPEC
        )

        result = await self.graph.ainvoke(
            state.model_dump(),
            config={"configurable": {"thread_id": session_id}}
        )

        res_task_id = result.get("task_id") or task_id
        res_title = result.get("title") or description
        res_project = result.get("project") or project
        res_ac = result.get("acceptance_criteria", [])

        self._save_or_update_task(
            res_task_id,
            {
                "project": res_project,
                "title": res_title,
                "status": result.get("status", "todo"),
                "acceptance_criteria": res_ac,
            }
        )

        return {
            "action": "task_created",
            "task_id": res_task_id,
            "title": res_title,
            "acceptance_criteria": res_ac,
            "current_gate": result.get("current_gate"),
            "awaiting_approval": result.get("awaiting_approval", False)
        }

    async def _handle_dispatch_task(self, args: str, session_id: str) -> dict:
        """
        /dispatch <task_id> @<agent>
        Runs task through Dispatch Gate.
        """
        parts = args.split()
        if len(parts) < 2:
            return {"error": "Usage: /dispatch <task_id> @<agent>"}

        task_id = parts[0]
        executor = parts[1]

        state = self._load_task_state(task_id)
        if not state:
            return {"error": f"Task {task_id} not found"}

        state.executor = executor
        state.current_gate = GateType.DISPATCH

        result = await self.graph.ainvoke(
            state.model_dump(),
            config={"configurable": {"thread_id": session_id}}
        )

        now_iso = datetime.utcnow().isoformat()
        res_status = result.get("status", "dispatched")

        self._save_or_update_task(
            task_id,
            {
                "executor": executor,
                "status": res_status,
                "dispatched_at": datetime.utcnow()
            }
        )

        return {
            "action": "dispatched",
            "task_id": task_id,
            "executor": executor,
            "status": res_status,
            "dispatched_at": result.get("dispatched_at") or now_iso
        }

    async def _handle_review_order(self, args: str, session_id: str) -> dict:
        """
        /review-order <task_id> [--ref <ref>] [--reviewer @<agent>]
        Runs task through Review Order Gate.
        """
        parts = args.split()
        if len(parts) < 1:
            return {"error": "Usage: /review-order <task_id> [--ref <ref>] [--reviewer @<agent>]"}

        task_id = parts[0]
        reviewer = self._extract_flag(args, "--reviewer") or "@antigravity"
        ref = self._extract_flag(args, "--ref")

        state = self._load_task_state(task_id)
        if not state:
            return {"error": f"Task {task_id} not found"}

        state.reviewer = reviewer
        if ref:
            state.result_ref = ref
        state.current_gate = GateType.REVIEW_ORDER
        state.raw_input = f"/review-order {task_id}"

        result = await self.graph.ainvoke(
            state.model_dump(),
            config={"configurable": {"thread_id": session_id}}
        )

        res_status = result.get("status", "in-review")
        res_reviewer = result.get("reviewer") or reviewer

        self._save_or_update_task(
            task_id,
            {
                "reviewer": res_reviewer,
                "status": res_status,
                "result_ref": ref,
                "in_review_at": datetime.utcnow()
            }
        )

        return {
            "action": "review_ordered",
            "task_id": task_id,
            "reviewer": res_reviewer,
            "status": res_status
        }

    async def _handle_verdict(self, args: str, session_id: str) -> dict:
        """
        /verdict <task_id> <pass|changes> [--reviewer @<agent>]
        Records review verdict.
        """
        parts = args.split()
        if len(parts) < 2:
            return {"error": "Usage: /verdict <task_id> <pass|changes> [--reviewer @<agent>]"}

        task_id = parts[0]
        verdict = parts[1].lower()
        reviewer = self._extract_flag(args, "--reviewer")

        if verdict not in ("pass", "changes"):
            return {"error": "Verdict must be 'pass' or 'changes'"}

        state = self._load_task_state(task_id)
        if not state:
            return {"error": f"Task {task_id} not found"}

        if reviewer:
            state.reviewer = reviewer

        state.verdict = verdict
        state.current_gate = GateType.VERDICT

        try:
            result = await self.graph.ainvoke(
                state.model_dump(),
                config={"configurable": {"thread_id": session_id}}
            )
        except FourEyesViolation as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

        if result.get("error"):
            return {"error": result["error"]}

        now_iso = datetime.utcnow().isoformat()
        res_status = result.get("status", "done" if verdict == "pass" else "changes-requested")

        self._save_or_update_task(
            task_id,
            {
                "reviewer": state.reviewer,
                "verdict": verdict,
                "status": res_status,
                "completed_at": datetime.utcnow()
            }
        )

        return {
            "action": "verdict_recorded",
            "task_id": task_id,
            "verdict": verdict,
            "status": res_status,
            "completed_at": result.get("completed_at") or now_iso
        }

    async def _handle_get_status(self, args: str, session_id: str) -> dict:
        """
        /status <task_id>
        Gets current task state.
        """
        parts = args.split()
        if len(parts) < 1:
            return {"error": "Usage: /status <task_id>"}

        task_id = parts[0]
        state = self._load_task_state(task_id)
        if not state:
            return {"error": f"Task {task_id} not found"}

        return {
            "action": "status",
            "task_id": state.task_id,
            "project": state.project,
            "title": state.title,
            "status": state.status,
            "current_gate": state.current_gate,
            "executor": state.executor,
            "reviewer": state.reviewer,
            "verdict": state.verdict
        }

    async def _handle_show_help(self, args: str, session_id: str) -> dict:
        """
        /help
        Shows available commands.
        """
        return {
            "action": "help",
            "commands": {
                "/pm <description> [--project <name>]": "Create a task and run Spec Gate",
                "/dispatch <task_id> @<agent>": "Dispatch task to executor",
                "/review-order <task_id> [--ref <ref>] [--reviewer @<agent>]": "Request code review",
                "/verdict <task_id> <pass|changes> [--reviewer @<agent>]": "Record review verdict",
                "/status <task_id>": "Get current task state",
                "/help": "Show available commands"
            }
        }
