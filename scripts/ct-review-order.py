#!/usr/bin/env python3
"""Mechanically move a completed task into review and create its review sheet."""

import argparse
import json
import re
import sys
import tempfile
from datetime import date
from pathlib import Path

from ct_common import fm_get, fm_get_inline_list, fm_set, find_task_file, rebuild, split_frontmatter


REPO_ROOT = Path(__file__).resolve().parent.parent


def fail(message, **extra):
    print(json.dumps({"ok": False, "error": message, **extra}, ensure_ascii=False, indent=2))
    raise SystemExit(1)


def normalize_agent(agent_id):
    if not agent_id:
        return None
    return agent_id if agent_id.startswith("@") else f"@{agent_id}"


def registry_repo_root(project):
    index_path = REPO_ROOT / "index.md"
    if not index_path.is_file():
        fail(f"PROJECT REGISTRY not found at {index_path}")
    for raw_line in index_path.read_text(encoding="utf-8").splitlines():
        if not raw_line.lstrip().startswith("|"):
            continue
        cells = [cell.strip().strip("`").strip() for cell in raw_line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[0] == project:
            root = cells[1]
            if not root.startswith("/"):
                fail(f"registry repo_root for {project} is not absolute: {root!r}")
            return root
    fail(f"project {project!r} not found in PROJECT REGISTRY")


def section(body, heading):
    lines = body.splitlines()
    start = next((i for i, line in enumerate(lines) if re.match(rf"^##\s+{re.escape(heading)}", line)), None)
    if start is None:
        fail(f"task is missing section {heading!r}")
    end = next((i for i in range(start + 1, len(lines)) if re.match(r"^##\s+", lines[i])), len(lines))
    return "\n".join(lines[start:end]).rstrip()


def list_field(lines, key):
    items = fm_get_inline_list(lines, key)
    if items:
        return items
    _, index = fm_get(lines, key)
    if index < 0:
        return []
    for line in lines[index + 1:]:
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*:", line):
            break
        match = re.match(r"^\s*-\s*(.+?)\s*$", line)
        if match:
            items.append(match.group(1).strip().strip('"'))
    return items


def review_sheet_path(task_path, task_id):
    return task_path.parent.parent / "reviews" / f"{task_id}-review.md"


def make_sheet(task_path, task_id, lines, ac_block, reviewer, result_ref, issued):
    project = task_path.parent.parent.name
    title, _ = fm_get(lines, "title")
    executor, _ = fm_get(lines, "executor")
    tests = list_field(lines, "tests")
    test_lines = "\n".join(f"- `{test}`" for test in tests) or "- *(none recorded in task frontmatter)*"
    task_rel = task_path.relative_to(REPO_ROOT)
    repo_root = registry_repo_root(project)
    frontmatter = "\n".join([
        "---",
        f"id: {task_id}",
        f"task_path: {task_rel}",
        f"project: {project}",
        f"result_ref: {result_ref}",
        f"executor: {executor or 'null'}",
        f"reviewer: {reviewer}",
        "status: pending",
        f"issued: {issued}",
        "verdict: null",
        "verdict_date: null",
        "---",
    ])
    return (
        f"{frontmatter}\n\n"
        f"# Phiếu Review: {task_id} — {title or ''}\n\n"
        f"- Dự án: {project} (`{repo_root}`)\n"
        f"- Task gốc: `{task_rel}`\n"
        f"- Result-ref: {result_ref}\n"
        f"- Executor: {executor or 'null'}\n"
        f"- Reviewer: {reviewer}\n"
        f"- Ngày phát phiếu: {issued}\n\n"
        "## Acceptance Criteria cần verify\n"
        f"{ac_block}\n\n"
        "## Definition of Done (AGENTS.md mục 3)\n"
        "- [ ] Toàn bộ AC pass\n"
        f"- [ ] Test liên quan xanh 100%: {', '.join(tests) if tests else '(none recorded)'}\n"
        "- [ ] Không regression (test khác trong module vẫn xanh)\n"
        f"- [ ] Reviewer khác executor (xác nhận reviewer {reviewer} ≠ executor {executor or 'null'})\n\n"
        "## Test gợi ý chạy trong repo code\n"
        f"{test_lines}\n\n"
        "## Câu hỏi rủi ro (từ code-review-graph, tĩnh — không thay thế việc tự đọc diff)\n"
        "- *(LLM/coordinator bổ sung từ graph nếu có; script không đọc diff và không gọi graph.)*\n\n"
        "## Review Toolchain\n"
        "Chạy theo toolchain của repo đích; preflight các tool đã đăng ký trước khi review.\n\n"
        "## Trả kết quả\n"
        f"`/verdict {task_id} <pass|changes> --reviewer {reviewer} [--commit <hash>] [--notes \"...\"]`\n"
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
    parser.add_argument("--ref", required=True)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    task_path = find_task_file(args.task_id, REPO_ROOT)
    if not task_path:
        fail(f"no task file found for {args.task_id}")
    task_text = task_path.read_text(encoding="utf-8")
    lines, body = split_frontmatter(task_text, task_path, fail)
    status, _ = fm_get(lines, "status")
    if status != "dispatched":
        fail(f"task status is {status!r}, not 'dispatched' — refusing", task=args.task_id)

    executor, _ = fm_get(lines, "executor")
    reviewer = normalize_agent(args.reviewer)
    executor_normalized = normalize_agent(executor)
    if reviewer == executor_normalized:
        fail("reviewer == executor — four-eyes violation, refusing", task=args.task_id)

    issued = date.today().isoformat()
    ac_block = section(body, "Tiêu chí nghiệm thu (AC)")
    sheet_path = review_sheet_path(task_path, args.task_id)
    fm_set(lines, "status", "in-review")
    fm_set(lines, "result_ref", args.ref, quote=True)
    fm_set(lines, "reviewer", reviewer, quote=True)
    fm_set(lines, "in_review", issued)
    fm_set(lines, "updated", issued)
    sheet = make_sheet(task_path, args.task_id, lines, ac_block, reviewer, args.ref, issued)

    result = {
        "ok": True,
        "dry_run": args.dry_run,
        "task": args.task_id,
        "task_path": str(task_path.relative_to(REPO_ROOT)),
        "status": "in-review",
        "result_ref": args.ref,
        "executor": executor_normalized,
        "reviewer": reviewer,
        "review_sheet": str(sheet_path.relative_to(REPO_ROOT)),
        "writes": [] if args.dry_run else [str(task_path.relative_to(REPO_ROOT)), str(sheet_path.relative_to(REPO_ROOT))],
    }
    if not args.dry_run:
        transactional_write_all([(task_path, rebuild(lines, body)), (sheet_path, sheet)])
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
