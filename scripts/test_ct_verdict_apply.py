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

    def test_ac3_fenced_code_with_heading_boundary(self):
        """
        Regression test for CT-024 Round 3:
        Verify that a '##' heading inside a fenced code block within the AC section
        is NOT treated as the AC section boundary, and real AC checkboxes AFTER
        the fence are correctly ticked and counted.
        """
        sample_body = """
> Project: control-tower

## Tiêu chí nghiệm thu (AC)

- [ ] **AC1:** Pre-fence criteria

```markdown
## Faked Heading Inside Code Fence
- [ ] Fenced example checkbox
```

- [ ] **AC2:** Post-fence criteria

## Next Section

- [ ] Non-AC checkbox
"""
        new_body, ticked_count = ct_verdict_apply.tick_ac_checkboxes(sample_body)

        # Expect 2 real AC checkboxes ticked (AC1 and AC2)
        self.assertEqual(ticked_count, 2)

        # Verify AC1 and AC2 were ticked
        self.assertIn("- [x] **AC1:** Pre-fence criteria", new_body)
        self.assertIn("- [x] **AC2:** Post-fence criteria", new_body)

        # Verify fenced code block content remained unchanged
        self.assertIn("## Faked Heading Inside Code Fence", new_body)
        self.assertIn("- [ ] Fenced example checkbox", new_body)

        # Verify Next Section checkbox remained unticked
        self.assertIn("- [ ] Non-AC checkbox", new_body)

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
        def mock_is_file(self_path):
            if str(self_path).endswith("update-agent-stats.sh"):
                return True
            return False

        with patch("subprocess.run", side_effect=OSError("Permission denied: update-agent-stats.sh")):
            with patch.object(Path, "is_file", autospec=True, side_effect=mock_is_file):
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

    def test_ct026_ac1_reverdict_prediction_accuracy_idempotent(self):
        """
        AC1: Re-verdicting a task updates its existing row in prediction-accuracy.md
        in-place rather than appending a new row, leaving exactly ONE row per task.
        """
        import json

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            task_dir = tmp_root / "projects" / "control-tower" / "tasks"
            review_dir = tmp_root / "projects" / "control-tower" / "reviews"
            metrics_dir = tmp_root / "knowledge" / "metrics"
            agents_dir = tmp_root / "knowledge" / "agents"

            task_dir.mkdir(parents=True)
            review_dir.mkdir(parents=True)
            metrics_dir.mkdir(parents=True)
            agents_dir.mkdir(parents=True)

            task_file = task_dir / "CT-888-test-reverdict.md"
            task_file.write_text("""---
id: CT-888
title: "Test re-verdict idempotency"
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

- [ ] **AC1:** Criteria 1
""", encoding="utf-8")

            review_file = review_dir / "CT-888-review.md"
            review_file.write_text("""---
id: CT-888
status: in-review
verdict: pending
---
# Review
""", encoding="utf-8")

            pa_file = metrics_dir / "prediction-accuracy.md"
            pa_file.write_text("""# Prediction Accuracy

| Date | Task ID | Level | Score | Factors | CI | Verdict | Match? | In Interval? |
|---|---|---|---|---|---|---|---|---|

| Metric | Value |
|---|---|
| **Total Predicted Tasks** | 0 |
| **Pass Count (Actual Success)** | 0 |
| **Changes Count (Actual Rework/Fail)** | 0 |
| **Overall Prediction Accuracy** | 0% (0/0) |
| **High Prediction Precision** | N/A |
| **Medium Prediction Precision** | N/A |
| **Low Prediction Precision** | N/A |
""", encoding="utf-8")

            agent_file = agents_dir / "@worker.md"
            agent_file.write_text("""---
agent_id: "@worker"
total_tasks_executed: 0
success_rate: 1.0
---
""", encoding="utf-8")

            with patch.object(ct_verdict_apply, "REPO_ROOT", tmp_root):
                # 1. Round 1: verdict = changes
                sys_argv1 = ["ct-verdict-apply.py", "CT-888", "changes", "--reviewer", "@reviewer1", "--notes", "Need fixes"]
                with patch.object(sys, "argv", sys_argv1):
                    with patch("builtins.print"):
                        ct_verdict_apply.main()

                pa_text1 = pa_file.read_text(encoding="utf-8")
                ct888_rows1 = [l for l in pa_text1.splitlines() if "| CT-888 |" in l]
                self.assertEqual(len(ct888_rows1), 1)
                self.assertIn("changes", ct888_rows1[0])

                # 2. Reset task status to in-review for Round 2
                task_content = task_file.read_text(encoding="utf-8")
                task_content = task_content.replace("status: changes-requested", "status: in-review")
                task_file.write_text(task_content, encoding="utf-8")

                # Round 2: verdict = pass
                sys_argv2 = ["ct-verdict-apply.py", "CT-888", "pass", "--reviewer", "@reviewer1", "--commit", "abcdef123"]
                with patch.object(sys, "argv", sys_argv2):
                    with patch("builtins.print"):
                        ct_verdict_apply.main()

                pa_text2 = pa_file.read_text(encoding="utf-8")
                ct888_rows2 = [l for l in pa_text2.splitlines() if "| CT-888 |" in l]
                # MUST leave exactly ONE row for CT-888, reflecting the final outcome 'pass'
                self.assertEqual(len(ct888_rows2), 1)
                self.assertIn("pass", ct888_rows2[0])
                self.assertIn("| **Pass Count (Actual Success)** | 1 |", pa_text2)
                self.assertIn("| **Changes Count (Actual Rework/Fail)** | 0 |", pa_text2)

    def test_ct026_ac2_reverdict_does_not_double_count_executed(self):
        """
        AC2: Re-verdicting a task does NOT increment total_tasks_executed for the executor again,
        and success_rate reflects the final outcome.
        """
        import json

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            task_dir = tmp_root / "projects" / "control-tower" / "tasks"
            review_dir = tmp_root / "projects" / "control-tower" / "reviews"
            metrics_dir = tmp_root / "knowledge" / "metrics"
            agents_dir = tmp_root / "knowledge" / "agents"

            task_dir.mkdir(parents=True)
            review_dir.mkdir(parents=True)
            metrics_dir.mkdir(parents=True)
            agents_dir.mkdir(parents=True)

            task_file = task_dir / "CT-777-test-stats.md"
            task_file.write_text("""---
id: CT-777
title: "Test executor stats"
status: in-review
priority: medium
risk: normal
executor: "@worker"
reviewer: "@reviewer1"
predicted_success: high
rejections: 0
---

## Tiêu chí nghiệm thu (AC)

- [ ] **AC1:** Criteria 1
""", encoding="utf-8")

            pa_file = metrics_dir / "prediction-accuracy.md"
            pa_file.write_text("""# Prediction Accuracy

| Date | Task ID | Level | Score | Factors | CI | Verdict | Match? | In Interval? |
|---|---|---|---|---|---|---|---|---|

| Metric | Value |
|---|---|
| **Total Predicted Tasks** | 0 |
| **Pass Count (Actual Success)** | 0 |
| **Changes Count (Actual Rework/Fail)** | 0 |
""", encoding="utf-8")

            agent_file = agents_dir / "@worker.md"
            agent_file.write_text("""---
agent_id: "@worker"
type: ai
total_tasks_executed: 0
total_tasks_reviewed: 0
success_rate: 1.0
recent_trend: stable
last_active: 2026-07-24
---
# @worker
""", encoding="utf-8")

            with patch.object(ct_verdict_apply, "REPO_ROOT", tmp_root):
                # 1. Round 1 verdict = changes
                sys_argv1 = ["ct-verdict-apply.py", "CT-777", "changes", "--reviewer", "@reviewer1", "--notes", "Fix required"]
                with patch.object(sys, "argv", sys_argv1):
                    with patch("builtins.print"):
                        ct_verdict_apply.main()

                prof1 = agent_file.read_text(encoding="utf-8")
                self.assertIn("total_tasks_executed: 1", prof1)

                # 2. Reset task status to in-review for Round 2
                task_content = task_file.read_text(encoding="utf-8")
                task_content = task_content.replace("status: changes-requested", "status: in-review")
                task_file.write_text(task_content, encoding="utf-8")

                # Round 2 verdict = pass
                sys_argv2 = ["ct-verdict-apply.py", "CT-777", "pass", "--reviewer", "@reviewer1", "--commit", "commit777"]
                with patch.object(sys, "argv", sys_argv2):
                    with patch("builtins.print"):
                        ct_verdict_apply.main()

                # Check agent profile after Round 2: total_tasks_executed MUST remain 1, success_rate MUST be 1.0
                prof2 = agent_file.read_text(encoding="utf-8")
                self.assertIn("total_tasks_executed: 1", prof2)
                self.assertIn("success_rate: 1.0", prof2)

    def test_ct026_ac3_mixed_marker_fence(self):
        """
        AC3: Mixed-marker nested fences (e.g. ``` fence containing ~~~) only close with
        their own opening marker. A '##' line inside the inner fence does not cause premature AC exit.
        """
        sample_body = """
> Project: control-tower

## Tiêu chí nghiệm thu (AC)

- [ ] **AC1:** Pre-fence item

```markdown
~~~yaml
## Fake heading inside mixed-marker fence
- [ ] Fake fenced item
~~~
```

- [ ] **AC2:** Post-fence item

## Implementation

- [ ] Non-AC item
"""
        new_body, ticked_count = ct_verdict_apply.tick_ac_checkboxes(sample_body)

        # Both AC1 and AC2 must be ticked
        self.assertEqual(ticked_count, 2)
        self.assertIn("- [x] **AC1:** Pre-fence item", new_body)
        self.assertIn("- [x] **AC2:** Post-fence item", new_body)

        # Fenced content must remain unticked and intact
        self.assertIn("## Fake heading inside mixed-marker fence", new_body)
        self.assertIn("- [ ] Fake fenced item", new_body)

        # Implementation item remains unticked
        self.assertIn("- [ ] Non-AC item", new_body)

    def test_ct026_ac4_crlf_frontmatter_tolerance(self):
        """
        AC4: FM_RE and split_frontmatter tolerate CRLF (\\r\\n) task files cleanly.
        """
        import json

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            task_dir = tmp_root / "projects" / "control-tower" / "tasks"
            review_dir = tmp_root / "projects" / "control-tower" / "reviews"
            metrics_dir = tmp_root / "knowledge" / "metrics"
            agents_dir = tmp_root / "knowledge" / "agents"

            task_dir.mkdir(parents=True)
            review_dir.mkdir(parents=True)
            metrics_dir.mkdir(parents=True)
            agents_dir.mkdir(parents=True)

            task_file = task_dir / "CT-666-crlf-task.md"
            task_file.write_bytes(
                "---\r\nid: CT-666\r\ntitle: \"CRLF task\"\r\nstatus: in-review\r\npriority: medium\r\nrisk: normal\r\nexecutor: \"@worker\"\r\nreviewer: \"@reviewer1\"\r\npredicted_success: high\r\nrejections: 0\r\n---\r\n\r\n## Tiêu chí nghiệm thu (AC)\r\n\r\n- [ ] **AC1:** CRLF item\r\n".encode("utf-8")
            )

            pa_file = metrics_dir / "prediction-accuracy.md"
            pa_file.write_text("""# Prediction Accuracy

| Date | Task ID | Level | Score | Factors | CI | Verdict | Match? | In Interval? |
|---|---|---|---|---|---|---|---|---|
""", encoding="utf-8")

            with patch.object(ct_verdict_apply, "REPO_ROOT", tmp_root):
                sys_argv = ["ct-verdict-apply.py", "CT-666", "pass", "--reviewer", "@reviewer1", "--commit", "crlf123"]
                with patch.object(sys, "argv", sys_argv):
                    with patch("builtins.print") as mock_print:
                        ct_verdict_apply.main()
                        res = json.loads(mock_print.call_args[0][0])
                        self.assertTrue(res["ok"])

            new_task_text = task_file.read_text(encoding="utf-8")
            self.assertIn("status: done", new_task_text)
            self.assertIn("- [x] **AC1:** CRLF item", new_task_text)

    def test_ct026_ac2_legacy_duplicate_rows_last_prev_verdict(self):
        """
        Regression test for CT-026 AC2 blocking defect:
        When prediction-accuracy has legacy duplicate rows (e.g. changes -> pass),
        a new 'changes' verdict must pick the LAST matching row ('pass') as prev_verdict,
        correctly adjusting executor success_rate (from 1.0 down to 0.0 for pass -> changes)
        AND consolidating the legacy duplicate rows into a single final 'changes' row.
        """
        import json

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            task_dir = tmp_root / "projects" / "control-tower" / "tasks"
            review_dir = tmp_root / "projects" / "control-tower" / "reviews"
            metrics_dir = tmp_root / "knowledge" / "metrics"
            agents_dir = tmp_root / "knowledge" / "agents"

            task_dir.mkdir(parents=True)
            review_dir.mkdir(parents=True)
            metrics_dir.mkdir(parents=True)
            agents_dir.mkdir(parents=True)

            task_file = task_dir / "CT-555-legacy-dup.md"
            task_file.write_text("""---
id: CT-555
title: "Legacy duplicate test"
status: in-review
priority: medium
risk: normal
executor: "@worker"
reviewer: "@reviewer1"
predicted_success: high
rejections: 1
---

## Tiêu chí nghiệm thu (AC)

- [ ] **AC1:** Criteria 1
""", encoding="utf-8")

            pa_file = metrics_dir / "prediction-accuracy.md"
            # Seed legacy duplicate rows: changes -> pass
            pa_file.write_text("""# Prediction Accuracy

| Date | Task ID | Level | Score | Factors | CI | Verdict | Match? | In Interval? |
|---|---|---|---|---|---|---|---|---|
| 2026-07-20 | CT-555 | high | 0.8 | deduction | [0.7, 0.9] | changes | ❌ | ❌ |
| 2026-07-21 | CT-555 | high | 0.8 | deduction | [0.7, 0.9] | pass | ✅ | ✅ |

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

            agent_file = agents_dir / "@worker.md"
            # Executor had 1 task executed, currently pass -> success_rate 1.0
            agent_file.write_text("""---
agent_id: "@worker"
type: ai
total_tasks_executed: 1
total_tasks_reviewed: 0
success_rate: 1.0
recent_trend: improving
last_active: 2026-07-21
---
# @worker
""", encoding="utf-8")

            with patch.object(ct_verdict_apply, "REPO_ROOT", tmp_root):
                sys_argv = ["ct-verdict-apply.py", "CT-555", "changes", "--reviewer", "@reviewer1", "--notes", "New regression issue"]
                with patch.object(sys, "argv", sys_argv):
                    with patch("builtins.print") as mock_print:
                        ct_verdict_apply.main()
                        res = json.loads(mock_print.call_args[0][0])
                        self.assertTrue(res["ok"])

            # 1. Check duplicate rows in prediction-accuracy.md consolidated to 1 row
            pa_text = pa_file.read_text(encoding="utf-8")
            ct555_rows = [l for l in pa_text.splitlines() if "| CT-555 |" in l]
            self.assertEqual(len(ct555_rows), 1)
            self.assertIn("changes", ct555_rows[0])

            # 2. Check executor stats adjusted correctly (pass -> changes: rate goes from 1.0 to 0.0)
            prof = agent_file.read_text(encoding="utf-8")
            self.assertIn("total_tasks_executed: 1", prof)
            self.assertIn("success_rate: 0.0", prof)
            self.assertIn("recent_trend: declining", prof)


if __name__ == "__main__":
    unittest.main()
