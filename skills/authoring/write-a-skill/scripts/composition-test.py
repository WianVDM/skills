#!/usr/bin/env python3
"""
composition-test.py

End-to-end composition test for write-a-skill's script-based dependencies.

Creates a temporary sample skill, then exercises:
  - detect-project-context
  - list-available-skills
  - parse-skill-frontmatter
  - validate-skill-frontmatter
  - audit-skill
  - run-trigger-evals

The conductor skills (decide-skill-shape, review-skill) are model-invoked and
produce context reports; this test documents where they fit in the full
write-a-skill workflow but does not invoke them automatically.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


SKILL_NAME = "sample-composition-skill"

SAMPLE_SKILL_MD = """---
name: sample-composition-skill
description: A temporary sample skill used to exercise the write-a-skill dependency surface.
version: 1.0.0
invocation: model-invoked
metadata:
  author: composition-test
  tags: [test, sample]
  verification_level: declared
---

# sample-composition-skill

## Purpose

Verify that write-a-skill's script-based dependencies can be invoked end-to-end.

## Type

Building block.

## In scope

- Parse the skill frontmatter.
- Validate the frontmatter against the schema.
- Audit the skill for blockers.
- Generate trigger evals.

## Out of scope

- Real behavior; this is a throwaway test fixture.

## When to use

A conductor wants to verify the dependency chain is healthy.

## Branch entry

| Branch | Trigger | Outcome |
|---|---|---|
| **run** | User wants to run the composition test. | All dependency checks pass. |

## References

- None.
"""


def run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


def main():
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    skills_dir = repo_root / "skills"

    with tempfile.TemporaryDirectory(prefix="write-a-skill-composition-") as tmp:
        tmp_path = Path(tmp)
        sample_skill_dir = tmp_path / "skills" / SKILL_NAME
        sample_skill_dir.mkdir(parents=True)
        (sample_skill_dir / "SKILL.md").write_text(SAMPLE_SKILL_MD, encoding="utf-8")

        results = []

        # 1. detect-project-context
        rc, out, err = run([
            sys.executable, str(skills_dir / "detect-project-context" / "scripts" / "detect-project-context.py"),
            "--start", str(repo_root), "--json",
        ])
        data = json.loads(out)
        results.append({
            "step": "detect-project-context",
            "pass": rc == 0 and data.get("project_root") == str(repo_root),
            "rc": rc,
            "error": err,
        })

        # 2. list-available-skills (project scope only)
        rc, out, err = run([
            sys.executable, str(skills_dir / "list-available-skills" / "scripts" / "list-available-skills.py"),
            "--project-root", str(repo_root), "--exclude-user", "--json",
        ])
        data = json.loads(out)
        results.append({
            "step": "list-available-skills",
            "pass": rc == 0 and any(s.get("name") == "write-a-skill" for s in data.get("skills", [])),
            "rc": rc,
            "error": err,
        })

        # 3. parse-skill-frontmatter
        rc, out, err = run([
            sys.executable, str(skills_dir / "parse-skill-frontmatter" / "scripts" / "parse-skill-frontmatter.py"),
            str(sample_skill_dir / "SKILL.md"), "--json",
        ])
        data = json.loads(out)
        results.append({
            "step": "parse-skill-frontmatter",
            "pass": rc == 0 and data.get("name") == SKILL_NAME and data.get("author") == "composition-test",
            "rc": rc,
            "error": err,
        })

        # 4. validate-skill-frontmatter
        rc, out, err = run([
            sys.executable, str(skills_dir / "validate-skill-frontmatter" / "scripts" / "validate-skill-frontmatter.py"),
            str(sample_skill_dir / "SKILL.md"), "--json",
        ])
        data = json.loads(out)
        results.append({
            "step": "validate-skill-frontmatter",
            "pass": rc == 0 and data.get("valid") is True,
            "rc": rc,
            "error": err,
        })

        # 5. audit-skill
        rc, out, err = run([
            sys.executable, str(skills_dir / "audit-skill" / "scripts" / "audit-skill.py"),
            str(sample_skill_dir), "--json",
        ])
        data = json.loads(out)
        results.append({
            "step": "audit-skill",
            "pass": rc == 0 and data.get("summary", {}).get("blockers") == 0,
            "rc": rc,
            "error": err,
        })

        # 6. run-trigger-evals
        rc, out, err = run([
            sys.executable, str(skills_dir / "run-trigger-evals" / "scripts" / "run-trigger-evals.py"),
            str(sample_skill_dir), "--json",
        ])
        data = json.loads(out)
        results.append({
            "step": "run-trigger-evals",
            "pass": rc == 0 and data.get("valid") is True and data.get("should_trigger_count", 0) > 0,
            "rc": rc,
            "error": err,
        })

    all_pass = all(r["pass"] for r in results)

    report = {
        "overall": "PASS" if all_pass else "FAIL",
        "results": results,
        "note": (
            "Conductor skills (decide-skill-shape, review-skill) are model-invoked "
            "and produce context reports; they are not invoked by this script."
        ),
    }

    print(json.dumps(report, indent=2))
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
