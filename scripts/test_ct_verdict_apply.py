#!/usr/bin/env python3
"""
Regression test suite for ct-verdict-apply.py covering CT-024 fixes:
1. AC3: Line-anchored regex AC checkbox ticking (skips inline code & fenced code).
2. AC4a: Transactional multi-file writes with full rollback on failure.
3. AC4b: Handling OSError / subprocess launch failure in run_agent_stats cleanly.
"""

import sys
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

import importlib.util

SCRIPTS_DIR = Path(__file__).resolve().parent
script_path = SCRIPTS_DIR / "ct-verdict-apply.py"

spec = importlib.util.spec_from_file_location("ct_verdict_apply", script_path)
ct_verdict_apply = importlib.util.module_from_spec(spec)
sys.modules["ct_verdict_apply"] = ct_verdict_apply
spec.loader.exec_module(ct_verdict_apply)


class TestCTVerdictApply(unittest.TestCase):

    def test_ac3_scoped_checkbox_ticking(self):
        """
        Verify that tick_ac_checkboxes:
        - Ticks real AC checkboxes (- [ ] -> - [x])
        - Does NOT tick '- [ ]' appearing inside inline code backticks within AC section
        - Does NOT tick checkboxes inside fenced code blocks within AC section
        - Does NOT tick checkboxes outside the AC section
        - Accurately counts ticked checkboxes (checkboxes_ticked == real count)
        """
        sample_body = """
> Project: control-tower

## Tiêu chí nghiệm thu (AC)

- [ ] **AC1:** Validate safety with `--dry-run` flag
- [ ] **AC3:** Fix substring replace of '- [ ]' inside backticks
  - [ ] Sub-item under AC3

```markdown
- [ ] Example inside code fence
```

## Implementation

- [ ] Non-AC checkbox in Implementation section
- [ ] Another non-AC checkbox
"""
        new_body, ticked_count = ct_verdict_apply.tick_ac_checkboxes(sample_body)

        # There are 3 real AC checkboxes (AC1, AC3, Sub-item under AC3)
        self.assertEqual(ticked_count, 3)

        # Verify AC items were ticked
        self.assertIn("- [x] **AC1:**", new_body)
        self.assertIn("- [x] **AC3:** Fix substring replace of '- [ ]' inside backticks", new_body)
        self.assertIn("  - [x] Sub-item under AC3", new_body)

        # Verify inline backtick code '- [ ]' remained unticked
        self.assertIn("'- [ ]' inside backticks", new_body)

        # Verify fenced code block checkbox remained unticked
        self.assertIn("```markdown\n- [ ] Example inside code fence\n```", new_body)

        # Verify Implementation section checkboxes remained unticked
        self.assertIn("- [ ] Non-AC checkbox in Implementation section", new_body)
        self.assertIn("- [ ] Another non-AC checkbox", new_body)

    def test_ac4a_transactional_writes_rollback(self):
        """
        Verify that transactional_write_all:
        - Successfully writes files if all succeed.
        - Restores original files to pre-write contents if ANY file write fails midway.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            file1 = tmp_path / "file1.txt"
            file2 = tmp_path / "file2.txt"

            file1.write_text("initial file1", encoding="utf-8")
            file2.write_text("initial file2", encoding="utf-8")

            pending_writes = [
                (file1, "modified file1"),
                (file2, "modified file2"),
            ]

            original_atomic_write = ct_verdict_apply.atomic_write

            def mock_atomic_write(path, content):
                if path == file2 and content == "modified file2":
                    raise OSError("Simulated write error on file2")
                original_atomic_write(path, content)

            with patch.object(ct_verdict_apply, "atomic_write", side_effect=mock_atomic_write):
                with self.assertRaises(SystemExit):
                    ct_verdict_apply.transactional_write_all(pending_writes)

            # Assert file1 was rolled back to initial content
            self.assertEqual(file1.read_text(encoding="utf-8"), "initial file1")
            self.assertEqual(file2.read_text(encoding="utf-8"), "initial file2")

    def test_ac4b_run_agent_stats_oserror_handling(self):
        """
        Verify that run_agent_stats catches OSError / subprocess launch failures
        and returns {"ran": False, "error": ...} instead of throwing an exception.
        """
        with patch("subprocess.run", side_effect=OSError("Permission denied: update-agent-stats.sh")):
            with patch.object(Path, "is_file", return_value=True):
                result = ct_verdict_apply.run_agent_stats("@executor", "executor", "pass", dry_run=False)
                self.assertFalse(result["ran"])
                self.assertIn("error", result)
                self.assertIn("Permission denied", result["error"])

    def test_sandbox_end_to_end(self):
        """
        Verify end-to-end execution of ct-verdict-apply in a throwaway sandbox directory in /tmp.
        """
        import json

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            task_dir = tmp_root / "projects" / "control-tower" / "tasks"
            review_dir = tmp_root / "projects" / "control-tower" / "reviews"
            metrics_dir = tmp_root / "knowledge" / "metrics"
            patterns_dir = tmp_root / "knowledge" / "patterns"

            task_dir.mkdir(parents=True)
            review_dir.mkdir(parents=True)
            metrics_dir.mkdir(parents=True)
            patterns_dir.mkdir(parents=True)

            task_file = task_dir / "CT-999-dummy-task.md"
            task_file.write_text("""---
id: CT-999
title: "Dummy task for sandbox test"
status: in-review
priority: medium
risk: normal
executor: "@worker"
reviewer: "@reviewer1"
confidence_interval: [0.7, 0.9]
predicted_success: high
rejections: 0
---

## Tiêu chí nghiệm thu (AC)

- [ ] **AC1:** First criteria with '- [ ]' in backticks
- [ ] **AC2:** Second criteria

## Implementation

- [ ] Non-AC item
""", encoding="utf-8")

            review_file = review_dir / "CT-999-review.md"
            review_file.write_text("""---
id: CT-999
status: in-review
verdict: pending
---
# Review
""", encoding="utf-8")

            pa_file = metrics_dir / "prediction-accuracy.md"
            pa_file.write_text("""# Prediction Accuracy

| Date | Task ID | Level | Score | Factors | CI | Verdict | Match? | In Interval? |
|---|---|---|---|---|---|---|---|---|
| 2026-07-24 | CT-000 | high | 0.8 | deduction | [0.7, 0.9] | pass | ✅ | ✅ |

| Metric | Value |
|---|---|
| **Total Predicted Tasks** | 1 |
| **Pass Count (Actual Success)** | 1 |
| **Changes Count (Actual Rework/Fail)** | 0 |
| **Overall Prediction Accuracy** | 100% (1/1) |
| **High Prediction Precision** | 100% (1/1) |
| **Medium Prediction Precision** | N/A |
| **Low Prediction Precision** | N/A |
""", encoding="utf-8")

            with patch.object(ct_verdict_apply, "REPO_ROOT", tmp_root):
                # 1. Test dry-run
                sys_argv_dry = ["ct-verdict-apply.py", "CT-999", "pass", "--reviewer", "@reviewer1", "--commit", "1234567", "--dry-run"]
                with patch.object(sys, "argv", sys_argv_dry):
                    with patch("builtins.print") as mock_print:
                        ct_verdict_apply.main()
                        printed_arg = mock_print.call_args[0][0]
                        res = json.loads(printed_arg)
                        self.assertTrue(res["ok"])
                        self.assertTrue(res["dry_run"])
                        self.assertEqual(res["checkboxes_ticked"], 2)

                # Ensure dry run did not modify task_file
                self.assertIn("- [ ] **AC1:**", task_file.read_text(encoding="utf-8"))

                # 2. Test actual run
                sys_argv_real = ["ct-verdict-apply.py", "CT-999", "pass", "--reviewer", "@reviewer1", "--commit", "1234567"]
                with patch.object(sys, "argv", sys_argv_real):
                    with patch("builtins.print") as mock_print:
                        ct_verdict_apply.main()
                        printed_arg = mock_print.call_args[0][0]
                        res = json.loads(printed_arg)
                        self.assertTrue(res["ok"])
                        self.assertFalse(res["dry_run"])

                # Verify files were mutated properly
                new_task_text = task_file.read_text(encoding="utf-8")
                self.assertIn("- [x] **AC1:** First criteria with '- [ ]' in backticks", new_task_text)
                self.assertIn("status: done", new_task_text)
                self.assertIn("- [ ] Non-AC item", new_task_text)


if __name__ == "__main__":
    unittest.main()
