import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[3]
PYTHON = sys.executable


def run_script(script_name, args, cwd=None):
    script = SKILL_ROOT / "scripts" / script_name
    result = subprocess.run(
        [PYTHON, str(script), *args],
        cwd=cwd or SKILL_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )
    return result


class ScanRelatedContextTests(unittest.TestCase):
    def test_complex_frontmatter_is_parsed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            context_dir = Path(tmpdir) / ".agents" / "context"
            context_dir.mkdir(parents=True)
            report = context_dir / "OC-1234-debrief.md"
            report.write_text(
                "---\n"
                "skill: debrief\n"
                "version: \"1.0\"\n"
                "ticket: OC-1234\n"
                "branch: feature/OC-1234-foo\n"
                "summary: |\n"
                "  This is a multi-line\n"
                "  summary for the report.\n"
                "generated_at: 2026-07-01T12:00:00Z\n"
                "---\n\n"
                "Body text here.\n",
                encoding="utf-8",
            )

            result = run_script(
                "scan-related-context.py",
                [
                    "--branch",
                    "feature/OC-1234-foo",
                    "--ticket",
                    "OC-1234",
                    "--cwd",
                    str(tmpdir),
                ],
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(len(data["matches"]), 1)
            match = data["matches"][0]
            self.assertEqual(match["skill"], "debrief")
            self.assertIn("multi-line", match["summary"])
            self.assertIn("report.", match["summary"])
            self.assertEqual(match["relevance"], "high")

    def test_excludes_self_skill(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            context_dir = Path(tmpdir) / ".agents" / "context"
            context_dir.mkdir(parents=True)
            report = context_dir / "verify-state.md"
            report.write_text(
                "---\n"
                "skill: verify-branch\n"
                "branch: main\n"
                "summary: Self reference.\n"
                "---\n\n"
                "Body.\n",
                encoding="utf-8",
            )

            result = run_script(
                "scan-related-context.py",
                [
                    "--branch",
                    "main",
                    "--cwd",
                    str(tmpdir),
                ],
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(len(data["matches"]), 0)


class InferStandardsTests(unittest.TestCase):
    def test_extracts_rules_from_markdown(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "standards.md"
            source.write_text(
                "---\n"
                "title: Coding Standards\n"
                "---\n\n"
                "# Naming\n\n"
                "- Variable names must be descriptive.\n"
                "- You should avoid single-letter names.\n\n"
                "# Testing\n\n"
                "- Always write unit tests for new code.\n",
                encoding="utf-8",
            )

            result = run_script(
                "infer-standards.py",
                [
                    "--source",
                    str(source),
                ],
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            import yaml

            data = yaml.safe_load(result.stdout)
            self.assertIn("rules", data)
            rules = data["rules"]
            self.assertTrue(len(rules) >= 3, rules)
            severities = {r["severity"] for r in rules}
            self.assertIn("violation", severities)
            self.assertIn("consideration", severities)


if __name__ == "__main__":
    unittest.main()
