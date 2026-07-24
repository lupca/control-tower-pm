#!/usr/bin/env python3
"""Shared YAML-frontmatter and task-file helpers for control-tower scripts."""

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
FM_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)


def split_frontmatter(text, path, error_handler=None):
    """Return normalized frontmatter lines and the document body."""
    text = text.replace("\r\n", "\n")
    match = FM_RE.match(text)
    if not match:
        message = f"{path}: no frontmatter block found"
        if error_handler is not None:
            return error_handler(message)
        raise ValueError(message)
    return match.group(1).split("\n"), text[match.end():]


def rebuild(lines, body):
    """Rebuild a document from frontmatter lines and its body."""
    return "---\n" + "\n".join(lines) + "\n---\n" + body


def fm_get(lines, key):
    """Return a frontmatter value and its line index, or ``(None, -1)``."""
    for i, line in enumerate(lines):
        match = re.match(rf"^{re.escape(key)}:\s*(.*)$", line)
        if match:
            value = match.group(1).strip()
            if value.startswith('"') and value.endswith('"') and len(value) >= 2:
                value = value[1:-1]
            return value, i
    return None, -1


def fm_set(lines, key, value, quote=False):
    """Set or append one frontmatter key and return the mutated lines."""
    rendered = f'"{value}"' if quote else str(value)
    newline = f"{key}: {rendered}"
    _, index = fm_get(lines, key)
    if index == -1:
        lines.append(newline)
    else:
        lines[index] = newline
    return lines


def fm_get_inline_list(lines, key):
    """Parse a simple inline YAML list into trimmed string items."""
    value, _ = fm_get(lines, key)
    if not value or value == "[]":
        return []
    inner = value.strip("[]")
    return [item.strip() for item in inner.split(",") if item.strip()]


def find_task_file(task_id, repo_root=None):
    """Find the first task file matching an ID across project task folders."""
    root = Path(repo_root) if repo_root is not None else REPO_ROOT
    matches = sorted((root / "projects").glob(f"*/tasks/{task_id}-*.md"))
    return matches[0] if matches else None


def parse_frontmatter(text):
    """Parse scalar frontmatter fields into a dictionary for reporting."""
    try:
        lines, _ = split_frontmatter(text, "frontmatter")
    except ValueError:
        return {}

    fields = {}
    for line in lines:
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line.rstrip())
        if not match:
            continue
        key, value = match.group(1), match.group(2).strip()
        if value.startswith('"') and value.endswith('"') and len(value) >= 2:
            value = value[1:-1]
        fields[key] = value
    return fields
