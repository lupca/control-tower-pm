#!/usr/bin/env python3
"""Tests for scripts/migrate_md_to_db.py and scripts/parse_frontmatter.py."""

import pytest
from pathlib import Path
from parse_frontmatter import parse_frontmatter_and_body, parse_file
from migrate_md_to_db import (
    parse_projects,
    parse_tasks,
    parse_agents,
    parse_knowledge,
    parse_audit_log,
    run_migration,
    normalize_status,
    to_list,
    REPO_ROOT,
)


def test_parse_frontmatter():
    text = """---
id: TEST-001
title: "Test Task"
status: done
files: ["a.py", "b.py"]
---

# Test Body
Content here.
"""
    fm, body = parse_frontmatter_and_body(text)
    assert fm["id"] == "TEST-001"
    assert fm["title"] == "Test Task"
    assert fm["status"] == "done"
    assert fm["files"] == ["a.py", "b.py"]
    assert "# Test Body" in body


def test_normalize_status():
    assert normalize_status("completed") == "done"
    assert normalize_status("pass") == "done"
    assert normalize_status("in-review") == "in_review"
    assert normalize_status("in_review") == "in_review"
    assert normalize_status("todo") == "todo"
    assert normalize_status("dispatched") == "dispatched"
    assert normalize_status(None) == "todo"


def test_to_list():
    assert to_list(None) == []
    assert to_list(["a", "b"]) == ["a", "b"]
    assert to_list("file.py") == ["file.py"]
    assert to_list("[a, b]") == ["a", "b"]


def test_parse_projects():
    projects, warnings = parse_projects(REPO_ROOT)
    assert len(projects) == 10
    project_ids = {p["id"] for p in projects}
    assert "topvnsport-pmi" in project_ids
    assert "control-tower-v2" in project_ids
    assert len(warnings) == 0


def test_parse_tasks():
    tasks, warnings = parse_tasks(REPO_ROOT)
    assert len(tasks) >= 130
    task_ids = {t["id"] for t in tasks}
    assert "CTV2-014" in task_ids or "CTV2-001" in task_ids
    assert len(warnings) == 0


def test_parse_agents():
    agents, warnings = parse_agents(REPO_ROOT)
    assert len(agents) == 19
    agent_ids = {a["id"] for a in agents}
    assert "@antigravity" in agent_ids
    assert "@claude-opus" in agent_ids
    assert len(warnings) == 0


def test_parse_knowledge():
    k_items, warnings = parse_knowledge(REPO_ROOT)
    assert len(k_items) >= 25
    k_ids = {k["id"] for k in k_items}
    assert "knowledge/decisions/ADR-001-file-over-api" in k_ids
    assert len(warnings) == 0


def test_parse_audit_log():
    logs, warnings = parse_audit_log(REPO_ROOT)
    assert len(logs) >= 300
    assert len(warnings) == 0


def test_dry_run_migration():
    result = run_migration("sqlite:///:memory:", dry_run=True)
    assert result["dry_run"] is True
    assert result["counts"]["projects"] == 10
    assert result["counts"]["tasks"] >= 130
    assert result["counts"]["agents"] == 19
    assert result["counts"]["knowledge"] >= 25
    assert result["counts"]["audit_log"] >= 300
