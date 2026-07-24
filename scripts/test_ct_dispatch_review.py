#!/usr/bin/env python3
"""Sandbox tests for CT-028 dispatch and review-order mechanics."""

import contextlib
import io
import importlib.util
import json
import shlex
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import ct_common


SCRIPTS_DIR = Path(__file__).resolve().parent


def load_script(module_name, filename):
    spec = importlib.util.spec_from_file_location(module_name, SCRIPTS_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


ct_dispatch = load_script("ct_dispatch_ct028", "ct-dispatch.py")
ct_review_order = load_script("ct_review_order_ct028", "ct-review-order.py")


class TestCT028Scripts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "projects" / "demo" / "tasks").mkdir(parents=True)
        (self.root / "knowledge" / "agents").mkdir(parents=True)
        (self.root / "knowledge" / "guides").mkdir(parents=True)
        (self.root / "index.md").write_text(
            "| Project | repo_root |\n|---|---|\n| `demo` | `/tmp/target-repo` |\n",
            encoding="utf-8",
        )
        (self.root / "knowledge" / "guides" / "spawn-patterns.md").write_text(
            "## Claude Code\nclaude --model\n## Agy\nagy --model\n## Codex\ncodex exec -m\n",
            encoding="utf-8",
        )
        (self.root / "knowledge" / "agents" / "@worker.md").write_text(
            "---\nagent_id: \"@worker\"\nmodel: gpt-5.6-luna\neffort: high\n---\n",
            encoding="utf-8",
        )
        (self.root / "knowledge" / "agents" / "@reviewer.md").write_text(
            "---\nagent_id: \"@reviewer\"\nmodel: claude-sonnet-5\neffort: high\n---\n",
            encoding="utf-8",
        )
        self.task = self.root / "projects" / "demo" / "tasks" / "DEMO-001-sandbox.md"
        self.task.write_text(
            """---
id: DEMO-001
title: "Sandbox task"
status: todo
executor: "@worker"
reviewer: null
result_ref: null
tests:
  - tests/test_demo.py
---

## Tiêu chí nghiệm thu (AC)

- [ ] AC1: preserve the exact block
- [ ] AC2: do not spawn a process

## Verification

- `pytest tests/test_demo.py`
""",
            encoding="utf-8",
        )
        self.patch_roots = contextlib.ExitStack()
        self.patch_roots.enter_context(patch.object(ct_dispatch, "REPO_ROOT", self.root))
        self.patch_roots.enter_context(
            patch.object(ct_dispatch, "SPAWN_GUIDE", self.root / "knowledge/guides/spawn-patterns.md")
        )
        self.patch_roots.enter_context(patch.object(ct_review_order, "REPO_ROOT", self.root))

    def tearDown(self):
        self.patch_roots.close()
        self.tmp.cleanup()

    def run_main(self, module, argv):
        output = io.StringIO()
        with patch.object(sys, "argv", argv), contextlib.redirect_stdout(output):
            module.main()
        return output.getvalue()

    def test_dispatch_print_only_builds_codex_without_writing(self):
        before = self.task.read_text(encoding="utf-8")
        command = self.run_main(ct_dispatch, ["ct-dispatch.py", "DEMO-001", "--print-only"])
        self.assertIn("cd /tmp/target-repo && codex exec -m gpt-5.6-luna", command)
        self.assertIn("-c model_reasoning_effort=high", command)
        self.assertIn("Execute task at", command)
        self.assertEqual(before, self.task.read_text(encoding="utf-8"))

    def test_dispatch_uses_canonical_command_shape_for_each_cli(self):
        self.assertIn(
            "claude --model claude-sonnet-5 -p 'Execute task at /tmp/task.md'",
            ct_dispatch.build_command("/tmp/repo", "claude", "claude-sonnet-5", "high", "Execute task at /tmp/task.md"),
        )
        self.assertIn(
            "agy --model gemini-3.6-flash-high --print 'Execute task at /tmp/task.md'",
            ct_dispatch.build_command("/tmp/repo", "agy", "gemini-3.6-flash-high", "high", "Execute task at /tmp/task.md"),
        )
        self.assertIn(
            "codex exec -m gpt-5.6-sol -c model_reasoning_effort=high",
            ct_dispatch.build_command("/tmp/repo", "codex", "gpt-5.6-sol", "high", "Execute task at /tmp/task.md"),
        )

    def test_dispatch_records_status_but_never_spawns(self):
        command = self.run_main(ct_dispatch, ["ct-dispatch.py", "DEMO-001"])
        text = self.task.read_text(encoding="utf-8")
        self.assertIn("status: dispatched", text)
        self.assertIn('executor: "@worker"', text)
        self.assertIn("codex exec", command)

    def test_review_order_dry_run_writes_nothing(self):
        self.task.write_text(
            self.task.read_text(encoding="utf-8").replace("status: todo", "status: dispatched"),
            encoding="utf-8",
        )
        text_before = self.task.read_text(encoding="utf-8")
        output = self.run_main(
            ct_review_order,
            ["ct-review-order.py", "DEMO-001", "--ref", "abc123", "--reviewer", "@reviewer", "--dry-run"],
        )
        result = json.loads(output)
        self.assertTrue(result["ok"])
        self.assertTrue(result["dry_run"])
        self.assertEqual([], result["writes"])
        self.assertEqual(text_before, self.task.read_text(encoding="utf-8"))
        self.assertFalse((self.root / "projects/demo/reviews").exists())

    def test_review_order_enforces_four_eyes_without_writing(self):
        task_text = self.task.read_text(encoding="utf-8").replace("status: todo", "status: dispatched")
        self.task.write_text(task_text, encoding="utf-8")
        before = self.task.read_text(encoding="utf-8")
        with self.assertRaises(SystemExit) as raised:
            self.run_main(
                ct_review_order,
                ["ct-review-order.py", "DEMO-001", "--ref", "abc123", "--reviewer", "@worker"],
            )
        self.assertEqual(1, raised.exception.code)
        self.assertEqual(before, self.task.read_text(encoding="utf-8"))
        self.assertFalse((self.root / "projects/demo/reviews").exists())

    def test_dispatch_review_enforces_four_eyes_without_output_or_writing(self):
        task_text = self.task.read_text(encoding="utf-8").replace("status: todo", "status: in-review")
        self.task.write_text(task_text, encoding="utf-8")
        before = self.task.read_text(encoding="utf-8")
        stdout = io.StringIO()
        stderr = io.StringIO()
        with self.assertRaises(SystemExit) as raised, patch.object(
            sys, "argv", ["ct-dispatch.py", "DEMO-001", "--role", "review", "--reviewer", "@worker"]
        ), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            ct_dispatch.main()
        self.assertEqual(1, raised.exception.code)
        self.assertEqual("", stdout.getvalue())
        self.assertIn("four-eyes", stderr.getvalue())
        self.assertEqual(before, self.task.read_text(encoding="utf-8"))

    def test_dispatch_shell_quotes_injection_shaped_result_ref(self):
        prompt = ct_dispatch.build_prompt(
            "review", Path("/tmp/task.md"), "abc$(touch /tmp/pwned)`whoami`", Path("/tmp/review.md")
        )
        command = ct_dispatch.build_command("/tmp/repo", "codex", "gpt-5.6-sol", "high", prompt)
        self.assertIn(shlex.quote(prompt), command)
        self.assertIn(prompt, shlex.split(command))

    def test_review_order_copies_fenced_ac_headings_in_full(self):
        self.task.write_text(
            self.task.read_text(encoding="utf-8").replace(
                "- [ ] AC2: do not spawn a process\n\n## Verification",
                "- [ ] AC2: do not spawn a process\n\n```markdown\n## This is inside the AC fence\n- preserve this line\n```\n\n## Verification",
            ).replace("status: todo", "status: dispatched"),
            encoding="utf-8",
        )
        self.run_main(
            ct_review_order,
            ["ct-review-order.py", "DEMO-001", "--ref", "abc123", "--reviewer", "@reviewer"],
        )
        sheet = (self.root / "projects/demo/reviews/DEMO-001-review.md").read_text(encoding="utf-8")
        self.assertIn("## This is inside the AC fence", sheet)
        self.assertIn("- preserve this line", sheet)
        self.assertIn("## Test gợi ý chạy trong repo code", sheet)

    def test_review_order_writes_task_and_sheet(self):
        self.task.write_text(
            self.task.read_text(encoding="utf-8").replace("status: todo", "status: dispatched"),
            encoding="utf-8",
        )
        output = self.run_main(
            ct_review_order,
            ["ct-review-order.py", "DEMO-001", "--ref", "abc123", "--reviewer", "@reviewer"],
        )
        result = json.loads(output)
        self.assertTrue(result["ok"])
        task_text = self.task.read_text(encoding="utf-8")
        sheet = self.root / "projects" / "demo" / "reviews" / "DEMO-001-review.md"
        sheet_text = sheet.read_text(encoding="utf-8")
        self.assertIn("status: in-review", task_text)
        self.assertIn('result_ref: "abc123"', task_text)
        self.assertIn("- [ ] AC1: preserve the exact block", sheet_text)
        self.assertIn("tests/test_demo.py", sheet_text)
        self.assertIn("Definition of Done", sheet_text)


if __name__ == "__main__":
    unittest.main()
