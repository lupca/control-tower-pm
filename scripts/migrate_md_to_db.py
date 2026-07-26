#!/usr/bin/env python3
"""CTV2-014: Migration script Markdown → PostgreSQL / Database.

Imports:
- index.md (PROJECT REGISTRY table) → projects table
- projects/*/tasks/*.md → tasks table
- knowledge/agents/@*.md → agents table
- knowledge/**/*.md (non-agents) → knowledge table
- log.md → audit_log table
"""

import sys
import os
import re
import argparse
from pathlib import Path
from datetime import datetime, date, timezone
from typing import Dict, Any, List, Optional, Tuple

import yaml
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "backend"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from parse_frontmatter import parse_file, parse_frontmatter_and_body

try:
    from app.db.models import Project, Task, Agent, Knowledge, AuditLog
    from app.db.base import Base
except ImportError:
    from sqlalchemy import Column, String, Text, Date, DateTime, Integer, Float, Boolean, ForeignKey, JSON
    from sqlalchemy.orm import declarative_base

    Base = declarative_base()

    class Project(Base):
        __tablename__ = "projects"
        id = Column(String(50), primary_key=True)
        name = Column(String(100), nullable=True)
        repo_root = Column(String(255), nullable=False)
        task_dir = Column(String(255), nullable=True)
        graph_status = Column(String(100), nullable=True)
        graph_embedded = Column(String(255), nullable=True)
        daemon_watch = Column(String(255), nullable=True)
        patterns_exportable = Column(Boolean, default=False)
        status = Column(String(20), default="active")
        done_count = Column(Integer, default=0)
        total_count = Column(Integer, default=0)
        created_at = Column(DateTime, default=datetime.now(timezone.utc).replace(tzinfo=None))
        updated_at = Column(DateTime, default=datetime.now(timezone.utc).replace(tzinfo=None), onupdate=datetime.now(timezone.utc).replace(tzinfo=None))

    class Agent(Base):
        __tablename__ = "agents"
        id = Column(String(50), primary_key=True)
        name = Column(String(100), nullable=True)
        role = Column(String(100), nullable=True)
        type = Column(String(20), nullable=True)
        model = Column(String(100), nullable=True)
        system_prompt = Column(Text, nullable=True)
        file_path = Column(String(255), nullable=True)
        stats = Column(JSON, default=dict)
        created_at = Column(DateTime, default=datetime.now(timezone.utc).replace(tzinfo=None))
        updated_at = Column(DateTime, default=datetime.now(timezone.utc).replace(tzinfo=None), onupdate=datetime.now(timezone.utc).replace(tzinfo=None))

    class Task(Base):
        __tablename__ = "tasks"
        id = Column(String(20), primary_key=True)
        project = Column(String(50), nullable=False, index=True)
        title = Column(Text, nullable=False)
        status = Column(String(20), nullable=False, default="todo", index=True)
        priority = Column(String(10), nullable=True)
        risk = Column(String(10), nullable=True)
        executor = Column(String(50), nullable=True)
        reviewer = Column(String(50), nullable=True)
        acceptance_criteria = Column(JSON, default=list)
        files = Column(JSON, default=list)
        tests = Column(JSON, default=list)
        flows = Column(JSON, default=list)
        plan = Column(Text, nullable=True)
        result_ref = Column(String(100), nullable=True)
        findings = Column(JSON, default=list)
        verdict = Column(String(10), nullable=True)
        predicted_success = Column(String(10), nullable=True)
        prediction_factors = Column(JSON, nullable=True)
        deadline = Column(Date, nullable=True)
        created_at = Column(DateTime, default=datetime.now(timezone.utc).replace(tzinfo=None))
        updated_at = Column(DateTime, default=datetime.now(timezone.utc).replace(tzinfo=None), onupdate=datetime.now(timezone.utc).replace(tzinfo=None))
        dispatched_at = Column(DateTime, nullable=True)
        in_review_at = Column(DateTime, nullable=True)
        done_at = Column(DateTime, nullable=True)
        completed_at = Column(DateTime, nullable=True)
        body = Column(Text, nullable=True)
        file_path = Column(String(255), nullable=True)
        depends_on = Column(JSON, default=list)

    class Knowledge(Base):
        __tablename__ = "knowledge"
        id = Column(String(150), primary_key=True)
        title = Column(String(255), nullable=True)
        category = Column(String(50), nullable=True, index=True)
        path = Column(String(255), nullable=False)
        content = Column(Text, nullable=True)
        metadata_info = Column(JSON, default=dict)
        created_at = Column(DateTime, default=datetime.now(timezone.utc).replace(tzinfo=None))
        updated_at = Column(DateTime, default=datetime.now(timezone.utc).replace(tzinfo=None), onupdate=datetime.now(timezone.utc).replace(tzinfo=None))

    class AuditLog(Base):
        __tablename__ = "audit_log"
        id = Column(Integer, primary_key=True, autoincrement=True)
        task_id = Column(String(20), nullable=True, index=True)
        action = Column(String(50), nullable=False)
        actor = Column(String(50), nullable=True)
        details = Column(JSON, nullable=True)
        created_at = Column(DateTime, default=datetime.now(timezone.utc).replace(tzinfo=None))


def to_list(val: Any) -> List[Any]:
    if val is None:
        return []
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        val = val.strip()
        if not val or val == "[]":
            return []
        if val.startswith("[") and val.endswith("]"):
            try:
                parsed = yaml.safe_load(val)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
            items = val[1:-1].split(",")
            return [i.strip() for i in items if i.strip()]
        return [val]
    return [val]


def parse_dt(val: Any) -> Optional[datetime]:
    if not val:
        return None
    if isinstance(val, datetime):
        return val
    if isinstance(val, date):
        return datetime.combine(val, datetime.min.time())
    if isinstance(val, str):
        val = val.strip()
        clean = val.split("+")[0].split("Z")[0].strip()
        for fmt in (
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
        ):
            try:
                return datetime.strptime(clean, fmt)
            except ValueError:
                continue
    return None


def parse_d(val: Any) -> Optional[date]:
    dt = parse_dt(val)
    return dt.date() if dt else None


def normalize_status(status_str: Any) -> str:
    if not status_str:
        return "todo"
    s = str(status_str).strip().lower()
    if s in ("completed", "pass"):
        return "done"
    if s == "in-review":
        return "in_review"
    if s in ("todo", "dispatched", "in_review", "done", "cancelled", "archived", "failed"):
        return s
    return "todo"


def extract_acceptance_criteria(body: str, fm_ac: Any) -> List[Any]:
    ac_list = to_list(fm_ac)
    if ac_list:
        return ac_list

    # Extract checkboxes from markdown body
    extracted = []
    lines = body.splitlines()
    in_ac_section = False
    for line in lines:
        if re.match(r"^##\s+.*(Acceptance Criteria|Tiêu chí nghiệm thu)", line, re.IGNORECASE):
            in_ac_section = True
            continue
        elif in_ac_section and line.startswith("## "):
            in_ac_section = False
            continue
        if in_ac_section and re.match(r"^\s*-\s*\[([ xX])\]\s*(.*)$", line):
            m = re.match(r"^\s*-\s*\[([ xX])\]\s*(.*)$", line)
            checked = m.group(1).lower() == "x"
            text = m.group(2).strip()
            extracted.append({"text": text, "done": checked})
    return extracted


def extract_plan(body: str, fm_plan: Any) -> Optional[str]:
    if fm_plan and str(fm_plan).strip():
        return str(fm_plan).strip()

    plan_lines = []
    lines = body.splitlines()
    in_plan = False
    for line in lines:
        if re.match(r"^##\s+.*(Plan|Kế hoạch)", line, re.IGNORECASE):
            in_plan = True
            continue
        elif in_plan and line.startswith("## "):
            break
        if in_plan:
            plan_lines.append(line)

    res = "\n".join(plan_lines).strip()
    return res if res else None


def parse_projects(root: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
    warnings = []
    index_file = root / "index.md"
    if not index_file.exists():
        warnings.append(f"index.md not found at {index_file}")
        return [], warnings

    content = index_file.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Section 2: PROJECT REGISTRY
    sec2_start = False
    registry = []
    for line in lines:
        if "## 2. PROJECT REGISTRY" in line:
            sec2_start = True
            continue
        if sec2_start and line.startswith("## "):
            sec2_start = False
            continue
        if sec2_start and line.strip().startswith("|"):
            cols = [c.strip() for c in line.strip().split("|")[1:-1]]
            if len(cols) >= 7 and not cols[0].startswith(":") and not "Project (" in cols[0]:
                p_id = re.sub(r"[`*]", "", cols[0]).strip()
                repo_root = re.sub(r"[`*]", "", cols[1]).strip()
                task_dir_raw = cols[2]
                task_dir_m = re.search(r"`([^`]+)`", task_dir_raw)
                task_dir = task_dir_m.group(1) if task_dir_m else task_dir_raw
                graph_status = cols[3]
                graph_embedded = cols[4]
                daemon_watch = cols[5]
                patterns_exportable = "true" in cols[6].lower()
                registry.append({
                    "id": p_id,
                    "repo_root": repo_root,
                    "task_dir": task_dir,
                    "graph_status": graph_status,
                    "graph_embedded": graph_embedded,
                    "daemon_watch": daemon_watch,
                    "patterns_exportable": patterns_exportable,
                })

    # Section 3: Project Map
    sec3_start = False
    project_map = {}
    for line in lines:
        if "## 3. BẢN ĐỒ TIẾN ĐỘ DỰ ÁN" in line:
            sec3_start = True
            continue
        if sec3_start and line.startswith("## "):
            sec3_start = False
            continue
        if sec3_start and line.strip().startswith("|"):
            cols = [c.strip() for c in line.strip().split("|")[1:-1]]
            if len(cols) >= 6 and not cols[0].startswith(":") and not "Dự án" in cols[0]:
                name = re.sub(r"[`*]", "", cols[0]).strip()
                dir_raw = re.sub(r"[`*]", "", cols[1]).strip()
                status_raw = cols[2].strip()
                status = "completed" if "Hoàn thành" in status_raw else "active"
                prog_raw = cols[3].strip()
                done_count, total_count = 0, 0
                m = re.search(r"(\d+)\s*/\s*(\d+)", prog_raw)
                if m:
                    done_count = int(m.group(1))
                    total_count = int(m.group(2))
                project_map[dir_raw] = {
                    "name": name,
                    "status": status,
                    "done_count": done_count,
                    "total_count": total_count,
                }

    projects = []
    for r in registry:
        info = project_map.get(r["task_dir"]) or project_map.get(f"projects/{r['id']}/") or {}
        r["name"] = info.get("name", r["id"])
        r["status"] = info.get("status", "active")
        r["done_count"] = info.get("done_count", 0)
        r["total_count"] = info.get("total_count", 0)
        projects.append(r)

    return projects, warnings


def parse_tasks(root: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
    warnings = []
    task_files = sorted(root.glob("projects/*/tasks/*.md"))
    tasks = []

    for tf in task_files:
        try:
            fm, body = parse_file(tf)
            rel_path = str(tf.relative_to(root))
            project_id = tf.parent.parent.name
            task_id = str(fm.get("id") or tf.stem.split("-")[0]).strip()
            title = str(fm.get("title") or tf.name).strip()

            status = normalize_status(fm.get("status"))
            priority = str(fm.get("priority")).lower() if fm.get("priority") else None
            risk = str(fm.get("risk")).lower() if fm.get("risk") else None
            executor = str(fm.get("executor")).strip() if fm.get("executor") else None
            reviewer = str(fm.get("reviewer")).strip() if fm.get("reviewer") else None
            result_ref = str(fm.get("result_ref") or fm.get("result-ref")).strip() if (fm.get("result_ref") or fm.get("result-ref")) else None
            verdict = str(fm.get("verdict")).strip() if fm.get("verdict") else None
            predicted_success = str(fm.get("predicted_success")).strip() if fm.get("predicted_success") else None
            prediction_factors = fm.get("prediction_factors") if isinstance(fm.get("prediction_factors"), (dict, list)) else None

            deadline = parse_d(fm.get("deadline"))
            created_at = parse_dt(fm.get("created") or fm.get("created_at")) or datetime.now(timezone.utc).replace(tzinfo=None)
            updated_at = parse_dt(fm.get("updated") or fm.get("updated_at")) or datetime.now(timezone.utc).replace(tzinfo=None)
            dispatched_at = parse_dt(fm.get("dispatched") or fm.get("dispatched_at"))
            in_review_at = parse_dt(fm.get("in_review") or fm.get("in_review_at"))
            done_at = parse_dt(fm.get("done") or fm.get("done_at") or fm.get("completed_at"))
            completed_at = done_at

            ac = extract_acceptance_criteria(body, fm.get("acceptance_criteria"))
            files = to_list(fm.get("files"))
            tests = to_list(fm.get("tests"))
            flows = to_list(fm.get("flows"))
            depends_on = to_list(fm.get("depends_on"))
            findings = to_list(fm.get("findings"))
            plan = extract_plan(body, fm.get("plan"))

            tasks.append({
                "id": task_id,
                "project": project_id,
                "title": title,
                "status": status,
                "priority": priority,
                "risk": risk,
                "executor": executor,
                "reviewer": reviewer,
                "acceptance_criteria": ac,
                "files": files,
                "tests": tests,
                "flows": flows,
                "depends_on": depends_on,
                "plan": plan,
                "result_ref": result_ref,
                "findings": findings,
                "verdict": verdict,
                "predicted_success": predicted_success,
                "prediction_factors": prediction_factors,
                "deadline": deadline,
                "created_at": created_at,
                "updated_at": updated_at,
                "dispatched_at": dispatched_at,
                "in_review_at": in_review_at,
                "done_at": done_at,
                "completed_at": completed_at,
                "body": body,
                "file_path": rel_path,
            })
        except Exception as e:
            warnings.append(f"Error parsing task {tf}: {e}")

    return tasks, warnings


def parse_agents(root: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
    warnings = []
    agent_files = sorted(root.glob("knowledge/agents/@*.md"))
    agents = []

    for af in agent_files:
        try:
            fm, body = parse_file(af)
            rel_path = str(af.relative_to(root))
            agent_id = str(fm.get("agent_id") or fm.get("id") or f"@{af.stem[1:] if af.stem.startswith('@') else af.stem}").strip()
            
            # Extract title / name
            name = fm.get("name")
            if not name:
                for line in body.splitlines():
                    if line.startswith("# Agent Profile:"):
                        name = line.replace("# Agent Profile:", "").strip()
                        break
            if not name:
                name = agent_id

            agent_type = str(fm.get("type", "ai")).lower()
            model = str(fm.get("model")).strip() if fm.get("model") else None
            role = str(fm.get("role")).strip() if fm.get("role") else None

            # Extract role summary block if present
            if not role:
                for line in body.splitlines():
                    if line.startswith("> "):
                        role = line[2:].strip()
                        break

            stats = {
                "total_tasks_executed": int(fm.get("total_tasks_executed", 0) or 0),
                "total_tasks_reviewed": int(fm.get("total_tasks_reviewed", 0) or 0),
                "success_rate": float(fm.get("success_rate", 1.0) or 1.0),
                "avg_review_rounds": float(fm.get("avg_review_rounds", 1.0) or 1.0),
                "strengths": to_list(fm.get("strengths")),
                "weaknesses": to_list(fm.get("weaknesses")),
                "recent_trend": str(fm.get("recent_trend")) if fm.get("recent_trend") else None,
                "last_active": str(fm.get("last_active")) if fm.get("last_active") else None,
            }

            created_at = parse_dt(fm.get("created") or fm.get("created_at")) or datetime.now(timezone.utc).replace(tzinfo=None)
            updated_at = parse_dt(fm.get("updated") or fm.get("updated_at")) or datetime.now(timezone.utc).replace(tzinfo=None)

            agents.append({
                "id": agent_id,
                "name": name,
                "role": role,
                "type": agent_type,
                "model": model,
                "system_prompt": body,
                "file_path": rel_path,
                "stats": stats,
                "created_at": created_at,
                "updated_at": updated_at,
            })
        except Exception as e:
            warnings.append(f"Error parsing agent {af}: {e}")

    return agents, warnings


def parse_knowledge(root: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
    warnings = []
    all_k = sorted(root.glob("knowledge/**/*.md"))
    k_files = [f for f in all_k if not f.match("knowledge/agents/@*.md")]
    knowledge_items = []

    for kf in k_files:
        try:
            fm, body = parse_file(kf)
            rel_path = str(kf.relative_to(root))
            slug = rel_path.replace(".md", "")
            category = kf.parent.name if kf.parent.name != "knowledge" else "general"

            title = fm.get("title")
            if not title:
                for line in body.splitlines():
                    if line.startswith("# "):
                        title = line[2:].strip()
                        break
            if not title:
                title = kf.stem

            created_at = parse_dt(fm.get("created") or fm.get("created_at")) or datetime.now(timezone.utc).replace(tzinfo=None)
            updated_at = parse_dt(fm.get("updated") or fm.get("updated_at")) or datetime.now(timezone.utc).replace(tzinfo=None)

            metadata_info = {
                "tags": to_list(fm.get("tags")),
                "scope": fm.get("scope"),
                "related": to_list(fm.get("related")),
                "status": fm.get("status"),
                "type": fm.get("type"),
            }

            knowledge_items.append({
                "id": slug,
                "title": title,
                "category": category,
                "path": rel_path,
                "content": body,
                "metadata_info": metadata_info,
                "created_at": created_at,
                "updated_at": updated_at,
            })
        except Exception as e:
            warnings.append(f"Error parsing knowledge {kf}: {e}")

    return knowledge_items, warnings


def parse_audit_log(root: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
    warnings = []
    log_file = root / "log.md"
    if not log_file.exists():
        warnings.append(f"log.md not found at {log_file}")
        return [], warnings

    content = log_file.read_text(encoding="utf-8")
    blocks = content.split("\n## ")
    entries = []

    for b in blocks[1:]:
        try:
            lines = b.splitlines()
            header = lines[0].strip()
            m = re.match(r"^\[(.*?)\]\s*([^|]+)(?:\|\s*(.*))?$", header)
            if not m:
                continue

            ts_str, action, target = m.group(1).strip(), m.group(2).strip(), m.group(3)
            if target:
                target = target.strip()

            created_at = parse_dt(ts_str) or datetime.now(timezone.utc).replace(tzinfo=None)
            task_id = target if target and not re.search(r"\.\.| ", target) else None
            actor = None
            bullets = {}

            for line in lines[1:]:
                line_str = line.strip()
                if line_str.startswith("- "):
                    kv = line_str[2:]
                    if ":" in kv:
                        k, v = kv.split(":", 1)
                        bullets[k.strip()] = v.strip()
                        if k.strip().lower() in ("reviewer", "executor", "actor"):
                            actor = v.strip().split()[0]

            details = {
                "target": target,
                "bullets": bullets,
                "raw_header": header,
            }

            entries.append({
                "task_id": task_id,
                "action": action,
                "actor": actor,
                "details": details,
                "created_at": created_at,
            })
        except Exception as e:
            warnings.append(f"Error parsing log block: {e}")

    return entries, warnings


def run_migration(db_url: str, dry_run: bool = False) -> Dict[str, Any]:
    print("=" * 60)
    print("      CONTROL TOWER MD → DB MIGRATION EXECUTION      ")
    print("=" * 60)
    print(f"Database URL: {db_url}")
    print(f"Dry Run Mode: {dry_run}")
    print("-" * 60)

    root = REPO_ROOT
    all_warnings = []

    # 1. Projects
    print("Parsing index.md (projects)...")
    projects_data, w = parse_projects(root)
    all_warnings.extend(w)

    # 2. Tasks
    print(f"Parsing projects/*/tasks/*.md (tasks)...")
    tasks_data, w = parse_tasks(root)
    all_warnings.extend(w)

    # 3. Agents
    print("Parsing knowledge/agents/@*.md (agents)...")
    agents_data, w = parse_agents(root)
    all_warnings.extend(w)

    # 4. Knowledge
    print("Parsing knowledge/**/*.md (knowledge)...")
    knowledge_data, w = parse_knowledge(root)
    all_warnings.extend(w)

    # 5. Audit Log
    print("Parsing log.md (audit_log)...")
    audit_data, w = parse_audit_log(root)
    all_warnings.extend(w)

    counts = {
        "projects": len(projects_data),
        "tasks": len(tasks_data),
        "agents": len(agents_data),
        "knowledge": len(knowledge_data),
        "audit_log": len(audit_data),
    }

    print("-" * 60)
    print("PARSED SUMMARY:")
    for k, v in counts.items():
        print(f"  - {k:<12}: {v} records")
    print(f"Total Warnings/Errors: {len(all_warnings)}")
    for warning in all_warnings[:10]:
        print(f"  [WARNING] {warning}")
    if len(all_warnings) > 10:
        print(f"  ... and {len(all_warnings) - 10} more warnings.")

    if dry_run:
        print("\n[DRY RUN] Skipping database writes.")
        print("=" * 60)
        return {"counts": counts, "warnings": all_warnings, "dry_run": True}

    # Execute DB migration
    print("\nConnecting to database and executing upserts...")
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    imported = {
        "projects": 0,
        "tasks": 0,
        "agents": 0,
        "knowledge": 0,
        "audit_log": 0,
    }

    try:
        # Projects upsert
        for p in projects_data:
            obj = session.query(Project).filter_by(id=p["id"]).first()
            if not obj:
                obj = Project(id=p["id"])
                session.add(obj)
            obj.name = p["name"]
            obj.repo_root = p["repo_root"]
            obj.task_dir = p["task_dir"]
            obj.graph_status = p["graph_status"]
            obj.graph_embedded = p["graph_embedded"]
            obj.daemon_watch = p["daemon_watch"]
            obj.patterns_exportable = p["patterns_exportable"]
            obj.status = p["status"]
            obj.done_count = p["done_count"]
            obj.total_count = p["total_count"]
            imported["projects"] += 1

        session.commit()

        # Tasks upsert
        for t in tasks_data:
            obj = session.query(Task).filter_by(id=t["id"]).first()
            if not obj:
                obj = Task(id=t["id"])
                session.add(obj)
            for key, value in t.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            imported["tasks"] += 1

        session.commit()

        # Agents upsert
        for a in agents_data:
            obj = session.query(Agent).filter_by(id=a["id"]).first()
            if not obj:
                obj = Agent(id=a["id"])
                session.add(obj)
            for key, value in a.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            imported["agents"] += 1

        session.commit()

        # Knowledge upsert
        for k in knowledge_data:
            obj = session.query(Knowledge).filter_by(id=k["id"]).first()
            if not obj:
                obj = Knowledge(id=k["id"])
                session.add(obj)
            for key, value in k.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            imported["knowledge"] += 1

        session.commit()

        # Audit log insertion (avoid duplicate entries by raw_header or created_at + action)
        existing_log_headers = {
            log.details.get("raw_header")
            for log in session.query(AuditLog.details).all()
            if log.details and isinstance(log.details, dict) and "raw_header" in log.details
        }

        for log in audit_data:
            raw_header = log["details"].get("raw_header") if log.get("details") else None
            if not raw_header or raw_header not in existing_log_headers:
                obj = AuditLog(
                    task_id=log["task_id"],
                    action=log["action"],
                    actor=log["actor"],
                    details=log["details"],
                    created_at=log["created_at"],
                )
                session.add(obj)
                if raw_header:
                    existing_log_headers.add(raw_header)
                imported["audit_log"] += 1

        session.commit()

        print("\nDATABASE IMPORT COMPLETED SUCCESSFULLY!")
        print("IMPORTED RECORD COUNTS:")
        for k, v in imported.items():
            print(f"  - {k:<12}: {v} inserted/updated")
        print("=" * 60)
        return {"counts": imported, "warnings": all_warnings, "dry_run": False}

    except Exception as e:
        session.rollback()
        print(f"\n[ERROR] Database migration failed: {e}")
        raise e
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(description="Migrate Control Tower Markdown data to Database.")
    parser.add_argument("--dry-run", action="store_true", help="Parse and validate without committing to database.")
    parser.add_argument("--db-url", type=str, default=None, help="Database connection URL.")
    args = parser.parse_args()

    db_url = args.db_url or os.getenv("DATABASE_URL")
    if not db_url:
        # Default connection string for localhost dev/test environment
        db_url = "postgresql://ct:secret@localhost:5433/control_tower"

    run_migration(db_url, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
