#!/usr/bin/env python3
"""Build (but never execute) the CLI command used by /dispatch."""

import argparse
import json
import re
import shlex
import sys
import tempfile
from datetime import date
from pathlib import Path

from ct_common import fm_get, fm_set, find_task_file, rebuild, split_frontmatter


REPO_ROOT = Path(__file__).resolve().parent.parent
SPAWN_GUIDE = REPO_ROOT / "knowledge" / "guides" / "spawn-patterns.md"


def fail(message, **extra):
    print(json.dumps({"ok": False, "error": message, **extra}, ensure_ascii=False, indent=2))
    raise SystemExit(1)


def normalize_agent(agent_id):
    if not agent_id:
        return None
    return agent_id if agent_id.startswith("@") else f"@{agent_id}"


def strip_cell(value):
    return value.strip().strip("`").strip()


def project_repo_root(project):
    """Read the project's absolute repo_root from the PROJECT REGISTRY table."""
    index_path = REPO_ROOT / "index.md"
    if not index_path.is_file():
        fail(f"PROJECT REGISTRY not found at {index_path}")

    for raw_line in index_path.read_text(encoding="utf-8").splitlines():
        if not raw_line.lstrip().startswith("|"):
            continue
        cells = [strip_cell(cell) for cell in raw_line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[0] == project:
            root = cells[1]
            if not root.startswith("/"):
                fail(f"registry repo_root for {project} is not absolute: {root!r}")
            return Path(root)
    fail(f"project {project!r} not found in PROJECT REGISTRY")


def load_agent(agent_id):
    agent_id = normalize_agent(agent_id)
    profile_path = REPO_ROOT / "knowledge" / "agents" / f"{agent_id}.md"
    if not profile_path.is_file():
        fail(f"agent profile not found for {agent_id}: {profile_path}")
    lines, _ = split_frontmatter(profile_path.read_text(encoding="utf-8"), profile_path, fail)
    model, _ = fm_get(lines, "model")
    effort, _ = fm_get(lines, "effort")
    if not model:
        fail(f"agent profile {agent_id} has no model")
    return agent_id, model, effort


def cli_for_model(model):
    model_lower = model.lower()
    if model_lower.startswith("claude-"):
        return "claude"
    if model_lower.startswith("gemini-") or model_lower.startswith("antigravity"):
        return "agy"
    if model_lower.startswith("gpt-"):
        return "codex"
    fail(f"cannot infer CLI for model {model!r}")


def validate_spawn_guide(cli):
    """Fail closed if the canonical spawn guide no longer documents this CLI."""
    if not SPAWN_GUIDE.is_file():
        fail(f"spawn-patterns guide not found at {SPAWN_GUIDE}")
    guide = SPAWN_GUIDE.read_text(encoding="utf-8")
    required = {
        "claude": "claude --model",
        "agy": "agy --model",
        "codex": "codex exec -m",
    }[cli]
    if required not in guide:
        fail(f"spawn-patterns guide does not document {cli}: {required}")


def double_quote(value):
    """Quote a prompt in the same readable form as spawn-patterns.md."""
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_prompt(role, task_path, result_ref=None, review_sheet=None):
    if role == "execute":
        return f"Execute task at {task_path}"
    prompt = f"Review task at {task_path}."
    if result_ref:
        prompt += f" Result ref: {result_ref}."
    if review_sheet:
        prompt += f" Review sheet: {review_sheet}."
    return prompt


def build_command(repo_root, cli, model, effort, prompt):
    root = shlex.quote(str(repo_root))
    quoted_prompt = double_quote(prompt)
    if cli == "claude":
        return f"cd {root} && claude --model {shlex.quote(model)} -p {quoted_prompt} --dangerously-skip-permissions"
    if cli == "agy":
        return f"cd {root} && agy --model {shlex.quote(model)} --print {quoted_prompt} --dangerously-skip-permissions"
    effort = effort or "medium"
    return (
        f"cd {root} && codex exec -m {shlex.quote(model)} "
        f"-c model_reasoning_effort={shlex.quote(effort)} "
        f"--dangerously-bypass-approvals-and-sandbox {quoted_prompt}"
    )


def atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def transactional_write_all(pending_writes):
    backups = {path: path.read_text(encoding="utf-8") if path.exists() else None for path, _ in pending_writes}
    written = []
    try:
        for path, content in pending_writes:
            atomic_write(path, content)
            written.append(path)
    except Exception as exc:
        for path in reversed(written):
            original = backups[path]
            if original is None:
                path.unlink(missing_ok=True)
            else:
                atomic_write(path, original)
        fail(f"transactional write failed: {exc}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("task_id")
    parser.add_argument("--role", choices=["execute", "review"], default="execute")
    parser.add_argument("--reviewer")
    parser.add_argument("--print-only", action="store_true")
    args = parser.parse_args()

    task_path = find_task_file(args.task_id, REPO_ROOT)
    if not task_path:
        fail(f"no task file found for {args.task_id}")
    task_text = task_path.read_text(encoding="utf-8")
    lines, body = split_frontmatter(task_text, task_path, fail)
    status, _ = fm_get(lines, "status")
    executor, _ = fm_get(lines, "executor")
    reviewer, _ = fm_get(lines, "reviewer")

    if args.role == "execute":
        if status not in ("todo", "changes-requested"):
            fail(f"task status is {status!r}, not dispatchable for execution", task=args.task_id)
        agent_id = normalize_agent(executor)
        if not agent_id:
            fail("executor is required for execute dispatch")
    else:
        if status != "in-review":
            fail(f"task status is {status!r}, not dispatchable for review", task=args.task_id)
        agent_id = normalize_agent(args.reviewer or reviewer)
        if not agent_id:
            fail("--reviewer or task reviewer is required for review dispatch")

    agent_id, model, effort = load_agent(agent_id)
    cli = cli_for_model(model)
    validate_spawn_guide(cli)
    repo_root = project_repo_root(task_path.parent.parent.name)
    absolute_task = task_path.resolve()
    sheet_path = task_path.parent.parent / "reviews" / f"{args.task_id}-review.md"
    result_ref, _ = fm_get(lines, "result_ref")
    prompt = build_prompt(args.role, absolute_task, result_ref, sheet_path.resolve())
    command = build_command(repo_root, cli, model, effort, prompt)

    if not args.print_only:
        today = date.today().isoformat()
        if args.role == "execute":
            fm_set(lines, "status", "dispatched")
            fm_set(lines, "executor", agent_id, quote=True)
            fm_set(lines, "dispatched", today)
            fm_set(lines, "updated", today)
        else:
            fm_set(lines, "reviewer", agent_id, quote=True)
            fm_set(lines, "updated", today)
        transactional_write_all([(task_path, rebuild(lines, body))])

    print(command)


if __name__ == "__main__":
    main()
