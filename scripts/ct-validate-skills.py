#!/usr/bin/env python3
"""Validate the frontmatter of every Control Tower Claude skill."""

import argparse
import json
import re
import sys
from pathlib import Path


FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---(?:\n|\Z)", re.DOTALL)
FIELD_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):(?:[ \t]*(.*))?$")


def _finding(skill, severity, issue):
    return {"skill": skill, "severity": severity, "issue": issue}


def _unquote(value):
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    return value


def _parse_frontmatter(content):
    """Return (fields, issue) for the small YAML subset used by skill metadata."""
    match = FRONTMATTER_RE.match(content.replace("\r\n", "\n"))
    if not match:
        if not content.startswith("---"):
            return None, "missing YAML frontmatter"
        return None, "invalid YAML frontmatter structure"

    fields = {}
    for line_number, line in enumerate(match.group(1).split("\n"), start=2):
        if not line.strip():
            continue
        field = FIELD_RE.match(line)
        if not field:
            return None, f"invalid YAML frontmatter structure at line {line_number}"
        key, value = field.group(1), (field.group(2) or "").strip()
        if key in fields:
            return None, f"duplicate frontmatter field '{key}'"
        fields[key] = _unquote(value)
    return fields, None


def validate_skill(skill_path):
    """Return findings for one skill directory.

    Unknown frontmatter fields are intentionally accepted so Control Tower can
    use metadata such as ``argument-hint`` and ``allowed-tools``.
    """
    skill_path = Path(skill_path)
    skill = skill_path.name
    skill_md = skill_path / "SKILL.md"
    if not skill_md.is_file():
        return [_finding(skill, "error", "SKILL.md not found")]

    try:
        content = skill_md.read_text(encoding="utf-8")
    except OSError as exc:
        return [_finding(skill, "error", f"cannot read SKILL.md: {exc}")]

    fields, issue = _parse_frontmatter(content)
    if issue:
        return [_finding(skill, "error", issue)]

    findings = []
    for required in ("name", "description"):
        if not fields.get(required, "").strip():
            findings.append(_finding(skill, "error", f"missing '{required}' in frontmatter"))

    declared_name = fields.get("name", "").strip()
    if declared_name and declared_name != skill:
        findings.append(
            _finding(
                skill,
                "warning",
                f"frontmatter name '{declared_name}' does not match skill directory '{skill}'",
            )
        )
    return findings


def collect_findings(skills_dir):
    skills_dir = Path(skills_dir)
    if not skills_dir.is_dir():
        return [_finding(str(skills_dir), "error", "skills directory not found")]
    findings = []
    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        findings.extend(validate_skill(skill_md.parent))
    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit findings as a JSON array")
    parser.add_argument(
        "--skills-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / ".claude" / "skills",
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args(argv)
    findings = collect_findings(args.skills_dir)

    if args.json:
        print(json.dumps(findings, ensure_ascii=False, indent=2))
    elif findings:
        symbols = {"error": "🔴", "warning": "🟡"}
        for finding in findings:
            print(f"{symbols.get(finding['severity'], '🟡')} {finding['skill']}: {finding['issue']}")
    else:
        print("No skill health findings.")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
