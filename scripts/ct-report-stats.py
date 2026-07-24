#!/usr/bin/env python3
"""
ct-report-stats.py — mechanical aggregation helper for the /report skill.

Scans projects/*/tasks/*.md, counts tasks by `status:` per project, and
(with --apply) rewrites each project's `## Tiến độ` and `## Tasks` blocks in
its `projects/<name>/<name>.md` file. Never touches task files themselves,
never edits `status:`, never touches index.md/log.md — those still need
human/LLM judgment (narrative notes, health-check warnings) and are left to
the coordinator.

Usage:
  scripts/ct-report-stats.py [--project NAME] [--apply]

Without --apply: prints JSON stats only (dry run).
With --apply: also rewrites the Tiến độ + Tasks blocks, and includes an
  "old_counts" field per project (parsed from the table that was replaced)
  so the caller can report what changed.
"""
import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STATUS_ORDER = ["done", "dispatched", "in-review", "changes-requested", "todo"]


def parse_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return {}
    fields = {}
    for line in m.group(1).splitlines():
        line = line.rstrip()
        km = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
        if not km:
            continue
        key, val = km.group(1), km.group(2).strip()
        if val.startswith('"') and val.endswith('"') and len(val) >= 2:
            val = val[1:-1]
        fields[key] = val
    return fields


def collect_tasks(project_dir):
    tasks = []
    tasks_dir = project_dir / "tasks"
    if not tasks_dir.is_dir():
        return tasks
    for f in sorted(tasks_dir.glob("*.md")):
        fm = parse_frontmatter(f.read_text(encoding="utf-8"))
        status = fm.get("status", "MISSING_STATUS")
        tasks.append({
            "id": fm.get("id", f.stem.split("-")[0]),
            "slug": f.stem,
            "title": fm.get("title", f.stem),
            "status": status,
        })
    return tasks


def counts_by_status(tasks):
    counts = {}
    for t in tasks:
        counts[t["status"]] = counts.get(t["status"], 0) + 1
    return counts


def ordered_status_rows(counts):
    rows = []
    for s in STATUS_ORDER:
        if s in counts:
            rows.append((s, counts[s]))
    for s in sorted(counts):
        if s not in STATUS_ORDER:
            rows.append((s, counts[s]))
    return rows


def render_tien_do_block(counts):
    lines = ["## Tiến độ", "| Trạng thái | Số task |", "|:---|---:|"]
    for status, n in ordered_status_rows(counts):
        lines.append(f"| {status} | {n} |")
    lines.append("*(Cập nhật bởi `/report`)*")
    return "\n".join(lines) + "\n"


def render_tasks_block(tasks):
    lines = [
        "## Tasks",
        "*(Cập nhật bởi `/report` — mỗi lần chạy sẽ regenerate lại toàn bộ danh sách này từ `tasks/*.md`)*",
    ]
    if not tasks:
        lines.append("*(chưa có task nào)*")
    for t in tasks:
        lines.append(f"- [[{t['slug']}]] — {t['title']} ({t['status']})")
    return "\n".join(lines) + "\n"


def parse_old_tien_do(text):
    m = re.search(r"## Tiến độ\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if not m:
        return {}
    old = {}
    for line in m.group(1).splitlines():
        rm = re.match(r"\|\s*([\w-]+)\s*\|\s*(\d+)\s*\|", line)
        if rm:
            old[rm.group(1)] = int(rm.group(2))
    return old


def replace_block(text, heading, new_block):
    pattern = re.compile(rf"{re.escape(heading)}\n.*?(?=\n## |\Z)", re.DOTALL)
    if pattern.search(text):
        replacement = new_block.rstrip("\n") + "\n"
        return pattern.sub(lambda _m: replacement, text, count=1)
    # Heading not present — insert before "## Tasks" if that exists, else append.
    tasks_idx = text.find("## Tasks")
    if heading != "## Tasks" and tasks_idx != -1:
        return text[:tasks_idx] + new_block + "\n" + text[tasks_idx:]
    return text.rstrip("\n") + "\n\n" + new_block


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=None)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    projects_root = REPO_ROOT / "projects"
    project_dirs = sorted(p for p in projects_root.iterdir() if p.is_dir())
    if args.project:
        project_dirs = [p for p in project_dirs if p.name == args.project]
        if not project_dirs:
            print(f"error: unknown project {args.project!r}", file=sys.stderr)
            sys.exit(1)

    result = []
    for pdir in project_dirs:
        tasks = collect_tasks(pdir)
        counts = counts_by_status(tasks)
        entry = {
            "project": pdir.name,
            "total": len(tasks),
            "counts": counts,
            "tasks": tasks,
        }

        md_path = pdir / f"{pdir.name}.md"
        if md_path.is_file():
            text = md_path.read_text(encoding="utf-8")
            entry["old_counts"] = parse_old_tien_do(text)
            if args.apply:
                text = replace_block(text, "## Tiến độ", render_tien_do_block(counts))
                text = replace_block(text, "## Tasks", render_tasks_block(tasks))
                md_path.write_text(text, encoding="utf-8")
                entry["applied_to"] = str(md_path.relative_to(REPO_ROOT))
        else:
            entry["warning"] = f"no {pdir.name}.md found"

        result.append(entry)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
