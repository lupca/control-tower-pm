#!/usr/bin/env python3
"""Tests for the Control Tower skill-health validator."""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "ct_validate_skills", SCRIPTS_DIR / "ct-validate-skills.py"
)
ct_validate_skills = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ct_validate_skills
SPEC.loader.exec_module(ct_validate_skills)


class TestCTValidateSkills(unittest.TestCase):
    def write_skill(self, root, directory, content):
        skill_dir = root / directory
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")
        return skill_dir

    def test_valid_skill_passes_and_accepts_control_tower_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = self.write_skill(
                Path(tmpdir),
                "demo-skill",
                """---
name: demo-skill
description: Validate a demo skill.
argument-hint: "[--json]"
allowed-tools: Read, Glob
---
# Demo
""",
            )
            self.assertEqual([], ct_validate_skills.validate_skill(skill_dir))

    def test_missing_frontmatter_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = self.write_skill(Path(tmpdir), "demo-skill", "# Demo\n")
            findings = ct_validate_skills.validate_skill(skill_dir)
            self.assertEqual("error", findings[0]["severity"])
            self.assertIn("frontmatter", findings[0]["issue"])

    def test_name_must_match_skill_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = self.write_skill(
                Path(tmpdir),
                "demo-skill",
                """---
name: another-skill
description: A valid description.
---
# Demo
""",
            )
            findings = ct_validate_skills.validate_skill(skill_dir)
            self.assertEqual("warning", findings[0]["severity"])
            self.assertIn("does not match", findings[0]["issue"])


if __name__ == "__main__":
    unittest.main()
