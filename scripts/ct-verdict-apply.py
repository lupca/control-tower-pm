#!/usr/bin/env python3
"""
ct-verdict-apply.py — mechanical apply step for the /verdict skill.

Applies the file mutations a pass/changes verdict requires, AFTER the
coordinator (LLM) has already done the parts that need judgment: reading
`state/mode.md` and getting Gate confirmation, and (for `risk: high`)
collecting the four causal-analysis fields from the User.

This script independently re-checks the two hard invariants before writing
anything (defense in depth — it does not trust the caller):
  - task `status:` must be `in-review`
  - `--reviewer` must differ from the task's `executor:` (four-eyes)
If either fails, it exits 1 with an error JSON and touches no files.

What it does NOT do (still the coordinator's job):
  - decide whether to run at all (Gate / four-eyes judgment, mode.md)
  - write `log.md` (needs a narrative "Giải trình")
  - decide the causal-analysis content, or whether it's required
  - propose a brand-new pattern file (must stay COLLABORATIVE per skill notes)

Usage:
  ct-verdict-apply.py <task-id> pass --reviewer @id --commit <hash> \\
      [--causal-root-cause "..." --causal-mechanism "..." \\
       --causal-counterfactual "..." --causal-pattern-id <id>] [--dry-run]

  ct-verdict-apply.py <task-id> changes --reviewer @id --notes "finding one; finding two" [--dry-run]

Prints a JSON summary of what changed.
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def fail(msg, **extra):
    print(json.dumps({"ok": False, "error": msg, **extra}, ensure_ascii=False, indent=2))
    sys.exit(1)


def split_frontmatter(text, path):
    m = FM_RE.match(text)
    if not m:
        fail(f"{path}: no frontmatter block found")
    return m.group(1).split("\n"), text[m.end():]


def rebuild(lines, body):
    return "---\n" + "\n".join(lines) + "\n---\n" + body


def fm_get(lines, key):
    for i, line in enumerate(lines):
        mm = re.match(rf"^{re.escape(key)}:\s*(.*)$", line)
        if mm:
            v = mm.group(1).strip()
            if v.startswith('"') and v.endswith('"') and len(v) >= 2:
                v = v[1:-1]
            return v, i
    return None, -1


def fm_set(lines, key, value, quote=False):
    rendered = f'"{value}"' if quote else str(value)
    newline = f"{key}: {rendered}"
    _, idx = fm_get(lines, key)
    if idx == -1:
        lines.append(newline)
    else:
        lines[idx] = newline
    return lines


def fm_get_inline_list(lines, key):
    v, _ = fm_get(lines, key)
    if not v or v == "[]":
        return []
    inner = v.strip("[]")
    return [x.strip() for x in inner.split(",") if x.strip()]


def find_task_file(task_id):
    matches = sorted((REPO_ROOT / "projects").glob(f"*/tasks/{task_id}-*.md"))
    return matches[0] if matches else None


def review_sheet_path(task_path, task_id):
    project_dir = task_path.parent.parent
    return project_dir / "reviews" / f"{task_id}-review.md"


def tick_ac_checkboxes(body):
    """
    Ticks '- [ ]' -> '- [x]' ONLY within the AC section ('## Tiêu chí nghiệm thu...').
    Stops at the next '## ' heading or end of body.
    """
    lines = body.split("\n")
    ac_start = None
    ac_end = len(lines)
    for i, line in enumerate(lines):
        if ac_start is None:
            if re.match(r"^##\s+Tiêu chí nghiệm thu", line):
                ac_start = i
        else:
            if re.match(r"^##\s+", line):
                ac_end = i
                break

    if ac_start is None:
        return body, 0

    ac_lines = lines[ac_start:ac_end]
    ac_text = "\n".join(ac_lines)
    ticked = ac_text.count("- [ ]")
    ac_text_ticked = ac_text.replace("- [ ]", "- [x]")

    new_lines = lines[:ac_start] + ac_text_ticked.split("\n") + lines[ac_end:]
    return "\n".join(new_lines), ticked


def append_section(body, heading, content):
    return body.rstrip("\n") + f"\n\n{heading}\n{content.rstrip()}\n"


def parse_confidence_interval(ci_str):
    if not ci_str:
        return None
    ci_str = ci_str.strip()
    m = re.match(r"^\[\s*([0-9.]+)\s*,\s*([0-9.]+)\s*\]$", ci_str)
    if m:
        try:
            return float(m.group(1)), float(m.group(2))
        except ValueError:
            return None
    return None


def prepare_prediction_accuracy(task_id, verdict, task_fm_lines, today_str):
    path = REPO_ROOT / "knowledge" / "metrics" / "prediction-accuracy.md"
    if not path.is_file():
        return {"updated": False, "reason": "file not found"}, None
    text = path.read_text(encoding="utf-8")

    predicted_level, _ = fm_get(task_fm_lines, "predicted_success")
    score = ""
    factors = ""
    m = re.search(r"prediction_factors:\n(.*?)(?=\n[a-zA-Z_]+:|\Z)", "\n".join(task_fm_lines) + "\n", re.DOTALL)
    if m:
        block = m.group(1)
        sm = re.search(r"score:\s*(\S+)", block)
        if sm:
            score = sm.group(1)
        dm = re.findall(r'- "([^"]+)"', block)
        factors = ", ".join(dm)

    row_re = re.compile(r"^\|([^|]*\|){8}[^|]*\|$")
    lines = text.split("\n")
    last_row_idx = None
    header_idx = None
    for i, line in enumerate(lines):
        if line.startswith("| Date | Task ID |"):
            header_idx = i
        if header_idx is not None and i > header_idx + 1 and row_re.match(line):
            last_row_idx = i

    if header_idx is None:
        return {"updated": False, "reason": "Log History table header not found"}, None

    # Well-formed data rows: 9-column rows after the header/separator.
    wellformed = []
    malformed = 0
    for i in range(header_idx + 2, len(lines)):
        line = lines[i]
        if not line.strip().startswith("|"):
            continue
        if row_re.match(line):
            cols = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cols) == 9:
                wellformed.append(cols)
        else:
            malformed += 1

    # Match = does the actual verdict agree with what the predicted level implied?
    # high/medium => expected pass; low => expected changes (per file's own §1 scoring semantics).
    if predicted_level in ("high", "medium"):
        matched = verdict == "pass"
    elif predicted_level == "low":
        matched = verdict == "changes"
    else:
        matched = None
    match_symbol = "✅" if matched else ("❌" if matched is False else "—")

    # Independent In-Interval calculation (AC2)
    confidence_interval_raw, _ = fm_get(task_fm_lines, "confidence_interval")
    ci_parsed = parse_confidence_interval(confidence_interval_raw)
    ci_display = confidence_interval_raw if confidence_interval_raw else "—"

    if ci_parsed is not None:
        lo, hi = ci_parsed
        outcome = 1.0 if verdict == "pass" else 0.0
        in_interval = "✅" if (lo <= outcome <= hi) else "❌"
    else:
        in_interval = "—"

    new_row = (
        f"| {today_str} | {task_id} | {predicted_level or '—'} | {score or '—'} | "
        f"{factors or '—'} | {ci_display} | {verdict} | {match_symbol} | {in_interval} |"
    )
    wellformed.append([today_str, task_id, predicted_level or "—", score or "—",
                        factors or "—", ci_display, verdict, match_symbol, in_interval])

    insert_at = (last_row_idx + 1) if last_row_idx is not None else (header_idx + 2)
    lines.insert(insert_at, new_row)

    total = len(wellformed)
    pass_count = sum(1 for r in wellformed if r[6] == "pass")
    changes_count = sum(1 for r in wellformed if r[6] == "changes")
    overall_match = sum(1 for r in wellformed if r[7] == "✅")

    def precision_for(level):
        rows = [r for r in wellformed if r[2] == level]
        if not rows:
            return "N/A"
        matches = sum(1 for r in rows if r[7] == "✅")
        return f"{round(100 * matches / len(rows))}% ({matches}/{len(rows)})"

    stats = {
        "Total Predicted Tasks": str(total),
        "Pass Count (Actual Success)": str(pass_count),
        "Changes Count (Actual Rework/Fail)": str(changes_count),
        "Overall Prediction Accuracy": f"{round(100 * overall_match / total) if total else 0}% ({overall_match}/{total})",
        "High Prediction Precision": precision_for("high"),
        "Medium Prediction Precision": precision_for("medium"),
        "Low Prediction Precision": precision_for("low"),
    }

    for i, line in enumerate(lines):
        mm = re.match(r"^\|\s*\*\*([^*]+)\*\*\s*\|", line)
        if mm and mm.group(1) in stats:
            lines[i] = f"| **{mm.group(1)}** | {stats[mm.group(1)]} |"

    new_text = "\n".join(lines)
    return {"updated": True, "new_row": new_row, "malformed_rows_skipped": malformed, "stats": stats}, (path, new_text)


def prepare_pattern_bump(pattern_id):
    idx_path = REPO_ROOT / "knowledge" / "patterns" / "_index.md"
    pattern_path = REPO_ROOT / "knowledge" / "patterns" / f"{pattern_id}.md"
    if not pattern_path.is_file() or not idx_path.is_file():
        return {"bumped": False, "reason": "pattern or index not found"}, None
    text = idx_path.read_text(encoding="utf-8")
    pat = re.compile(rf"(\|\s*\[\[{re.escape(pattern_id)}\]\]\s*\|[^|]*\|[^|]*\|\s*)(\d+)(\s*\|)")
    m = pat.search(text)
    if not m:
        return {"bumped": False, "reason": "row not found in _index.md"}, None
    new_count = int(m.group(2)) + 1
    new_text = pat.sub(lambda mm: f"{mm.group(1)}{new_count}{mm.group(3)}", text, count=1)
    return {"bumped": True, "new_count": new_count}, (idx_path, new_text)


def run_agent_stats(agent_id, role, verdict, dry_run=False):
    if dry_run:
        return {"ran": False, "dry_run": True}
    script = REPO_ROOT / "scripts" / "update-agent-stats.sh"
    if not script.is_file():
        return {"ran": False, "reason": "script not found"}
    r = subprocess.run([str(script), agent_id, role, verdict], capture_output=True, text=True)
    return {"ran": True, "returncode": r.returncode, "stdout": r.stdout.strip(), "stderr": r.stderr.strip()}


def atomic_write(path: Path, content: str):
    tmp_path = path.with_name(f".{path.name}.tmp")
    try:
        tmp_path.write_text(content, encoding="utf-8")
        tmp_path.replace(path)
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink()
        raise


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("task_id")
    ap.add_argument("verdict", choices=["pass", "changes"])
    ap.add_argument("--reviewer", required=True)
    ap.add_argument("--commit")
    ap.add_argument("--notes")
    ap.add_argument("--causal-root-cause")
    ap.add_argument("--causal-mechanism")
    ap.add_argument("--causal-counterfactual")
    ap.add_argument("--causal-pattern-id")
    ap.add_argument("--dry-run", action="store_true", help="Perform logic validation and JSON generation without writing files")
    args = ap.parse_args()

    if args.verdict == "pass" and not args.commit:
        fail("--commit is required for a pass verdict (never invent one)")
    if args.verdict == "changes" and not args.notes:
        fail("--notes is required for a changes verdict")

    task_path = find_task_file(args.task_id)
    if not task_path:
        fail(f"no task file found for {args.task_id}")

    text = task_path.read_text(encoding="utf-8")
    lines, body = split_frontmatter(text, task_path)

    status, _ = fm_get(lines, "status")
    if status != "in-review":
        fail(f"task status is {status!r}, not 'in-review' — refusing", task=args.task_id)

    executor, _ = fm_get(lines, "executor")
    reviewer_arg = args.reviewer if args.reviewer.startswith("@") else f"@{args.reviewer}"
    executor_norm = executor if (executor or "").startswith("@") else f"@{executor}"
    if reviewer_arg == executor_norm:
        fail("reviewer == executor — four-eyes violation, refusing", task=args.task_id)

    today_str = date.today().isoformat()
    risk, _ = fm_get(lines, "risk")
    depends_on = fm_get_inline_list(lines, "depends_on")
    sheet_path = review_sheet_path(task_path, args.task_id)

    result = {
        "ok": True,
        "dry_run": args.dry_run,
        "task": args.task_id,
        "task_path": str(task_path.relative_to(REPO_ROOT)),
        "verdict": args.verdict,
        "risk": risk,
        "depends_on": depends_on,
    }

    pending_writes = []

    # --- Review sheet frontmatter ---
    if sheet_path.is_file():
        s_text = sheet_path.read_text(encoding="utf-8")
        s_lines, s_body = split_frontmatter(s_text, sheet_path)
        fm_set(s_lines, "reviewer", reviewer_arg, quote=True)
        fm_set(s_lines, "status", "passed" if args.verdict == "pass" else "changes-requested")
        fm_set(s_lines, "verdict", args.verdict)
        fm_set(s_lines, "verdict_date", today_str)
        pending_writes.append((sheet_path, rebuild(s_lines, s_body)))
        result["review_sheet_updated"] = str(sheet_path.relative_to(REPO_ROOT))
    else:
        result["review_sheet_updated"] = None
        result["review_sheet_warning"] = f"not found at {sheet_path.relative_to(REPO_ROOT)}, skipped"

    if args.verdict == "pass":
        body, ticked = tick_ac_checkboxes(body)
        result["checkboxes_ticked"] = ticked

        causal_fields = [args.causal_root_cause, args.causal_mechanism, args.causal_counterfactual]
        if any(causal_fields):
            content = (
                f"- **Root cause**: {args.causal_root_cause or '(chưa cung cấp)'}\n"
                f"- **Mechanism**: {args.causal_mechanism or '(chưa cung cấp)'}\n"
                f"- **Counterfactual**: {args.causal_counterfactual or '(chưa cung cấp)'}\n"
            )
            if args.causal_pattern_id:
                content += f"- **Pattern**: [[{args.causal_pattern_id}]]\n"
            body = append_section(body, "## Causal Analysis", content)
            result["causal_analysis_added"] = True
        else:
            result["causal_analysis_added"] = False

        if args.causal_pattern_id:
            bump_res, bump_write = prepare_pattern_bump(args.causal_pattern_id)
            result["pattern_bump"] = bump_res
            if bump_write:
                pending_writes.append(bump_write)

        fm_set(lines, "status", "done")
        fm_set(lines, "reviewer", reviewer_arg, quote=True)
        fm_set(lines, "result_ref", args.commit, quote=True)
        fm_set(lines, "updated", today_str)

    else:  # changes
        findings = [f.strip() for f in re.split(r"[;\n]", args.notes) if f.strip()]
        content = "\n".join(f"- [ ] {f}" for f in findings)
        body = append_section(body, "## Findings từ reviewer", content)
        result["findings_added"] = findings

        rejections_str, _ = fm_get(lines, "rejections")
        rejections = int(rejections_str) if rejections_str else 0
        rejections += 1
        fm_set(lines, "rejections", rejections)
        fm_set(lines, "status", "changes-requested")
        fm_set(lines, "updated", today_str)
        result["rejections"] = rejections
        result["reviewer_rotation_alert"] = rejections >= 2

    pending_writes.append((task_path, rebuild(lines, body)))

    pa_res, pa_write = prepare_prediction_accuracy(args.task_id, args.verdict, lines, today_str)
    result["prediction_accuracy"] = pa_res
    if pa_write:
        pending_writes.append(pa_write)

    if not args.dry_run:
        for p, c in pending_writes:
            atomic_write(p, c)

    result["agent_stats"] = {
        "executor": run_agent_stats(executor_norm, "executor", args.verdict, dry_run=args.dry_run),
        "reviewer": run_agent_stats(reviewer_arg, "reviewer", args.verdict, dry_run=args.dry_run),
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
