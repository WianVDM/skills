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

In addition, verifies that the model-invoked conductor dependencies exist
and parse correctly:
  - detect-skill-overlap
  - decide-skill-shape
  - review-skill

The conductor skills themselves are model-invoked and produce context reports;
this test documents where they fit in the full write-a-skill workflow but does
not invoke them automatically.
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
- Demonstrate a capability-to-tool strategy: discover available tools for the fetch-data capability and disclose the choice.

## Out of scope

- Real behavior; this is a throwaway test fixture.

## When to use

A conductor wants to verify the dependency chain is healthy.

## Branch entry

| Branch | Trigger | Outcome |
|---|---|---|
| **run** | User wants to run the composition test. | All dependency checks pass. |

## Capability-to-tool strategy

| Capability | Preferred tool | Fallback tool | Degraded disclosure |
|---|---|---|---|
| Fetch data | `native-binary` if available | `manual-fallback` | Falls back to manual input; the user is asked to confirm. |

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


def skill_path(skills_dir: Path, *parts: str) -> Path:
    return skills_dir.joinpath(*parts)


def main() -> int:
    repo_root = Path(__file__).resolve().parents[5]
    skills_dir = repo_root / "skills"

    results = []

    with tempfile.TemporaryDirectory(prefix="write-a-skill-composition-") as tmp:
        tmp_path = Path(tmp)
        sample_skill_dir = tmp_path / "skills" / SKILL_NAME
        sample_skill_dir.mkdir(parents=True)
        (sample_skill_dir / "SKILL.md").write_text(SAMPLE_SKILL_MD, encoding="utf-8")

        # 1. detect-project-context
        rc, out, err = run([
            sys.executable, str(skill_path(skills_dir, "blocks", "project", "detect-project-context", "scripts", "detect-project-context.py")),
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
            sys.executable, str(skill_path(skills_dir, "blocks", "registry", "list-available-skills", "scripts", "list-available-skills.py")),
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
            sys.executable, str(skill_path(skills_dir, "blocks", "authoring", "parse-skill-frontmatter", "scripts", "parse-skill-frontmatter.py")),
            str(sample_skill_dir / "SKILL.md"), "--json",
        ])
        data = json.loads(out)
        results.append({
            "step": "parse-skill-frontmatter",
            "pass": rc == 0 and data.get("name") == SKILL_NAME,
            "rc": rc,
            "error": err,
        })

        # 4. validate-skill-frontmatter
        rc, out, err = run([
            sys.executable, str(skill_path(skills_dir, "blocks", "authoring", "validate-skill-frontmatter", "scripts", "validate-skill-frontmatter.py")),
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
            sys.executable, str(skill_path(skills_dir, "blocks", "authoring", "audit-skill", "scripts", "audit-skill.py")),
            str(sample_skill_dir), "--json",
        ])
        data = json.loads(out)
        findings = {f["id"]: f for f in data.get("findings", [])}
        ta01_ok = findings.get("TA-01", {}).get("result") in ("PASS", "MANUAL", "N/A")
        ta02_ok = findings.get("TA-02", {}).get("result") in ("PASS", "MANUAL", "N/A")
        results.append({
            "step": "audit-skill",
            "pass": rc == 0 and data.get("summary", {}).get("blockers") == 0 and ta01_ok and ta02_ok,
            "rc": rc,
            "error": err,
        })

        # 6. run-trigger-evals
        rc, out, err = run([
            sys.executable, str(skill_path(skills_dir, "blocks", "authoring", "run-trigger-evals", "scripts", "run-trigger-evals.py")),
            str(sample_skill_dir), "--json",
        ])
        data = json.loads(out)
        results.append({
            "step": "run-trigger-evals",
            "pass": rc == 0 and data.get("valid") is True and data.get("should_trigger_count", 0) > 0,
            "rc": rc,
            "error": err,
        })

    # 7. detect-skill-overlap files exist and parse
    overlap_md = skill_path(skills_dir, "blocks", "authoring", "detect-skill-overlap", "SKILL.md")
    overlap_evals = skill_path(skills_dir, "blocks", "authoring", "detect-skill-overlap", "evals", "evals.json")
    rc, out, err = run([
        sys.executable, str(skill_path(skills_dir, "blocks", "authoring", "parse-skill-frontmatter", "scripts", "parse-skill-frontmatter.py")),
        str(overlap_md), "--json",
    ])
    data = json.loads(out)
    overlap_evals_valid = False
    if overlap_evals.is_file():
        try:
            json.loads(overlap_evals.read_text(encoding="utf-8"))
            overlap_evals_valid = True
        except Exception:
            pass
    results.append({
        "step": "detect-skill-overlap-present",
        "pass": overlap_md.is_file() and data.get("name") == "detect-skill-overlap" and overlap_evals_valid,
        "rc": rc,
        "error": err if not overlap_md.is_file() else "",
    })

    # 8. decide-skill-shape files exist and parse
    decide_md = skill_path(skills_dir, "blocks", "authoring", "decide-skill-shape", "SKILL.md")
    rc, out, err = run([
        sys.executable, str(skill_path(skills_dir, "blocks", "authoring", "parse-skill-frontmatter", "scripts", "parse-skill-frontmatter.py")),
        str(decide_md), "--json",
    ])
    data = json.loads(out)
    results.append({
        "step": "decide-skill-shape-present",
        "pass": decide_md.is_file() and data.get("name") == "decide-skill-shape",
        "rc": rc,
        "error": err if not decide_md.is_file() else "",
    })

    # 9. review-skill files exist and parse
    review_md = skill_path(skills_dir, "blocks", "authoring", "review-skill", "SKILL.md")
    rc, out, err = run([
        sys.executable, str(skill_path(skills_dir, "blocks", "authoring", "parse-skill-frontmatter", "scripts", "parse-skill-frontmatter.py")),
        str(review_md), "--json",
    ])
    data = json.loads(out)
    results.append({
        "step": "review-skill-present",
        "pass": review_md.is_file() and data.get("name") == "review-skill",
        "rc": rc,
        "error": err if not review_md.is_file() else "",
    })

    # 10. Portable schema fallback exists
    shipped_schema = skill_path(skills_dir, "blocks", "authoring", "audit-skill", "references", "skill-frontmatter.schema.json")
    results.append({
        "step": "shipped-schema-fallback",
        "pass": shipped_schema.is_file(),
        "rc": 0,
        "error": "" if shipped_schema.is_file() else f"Missing {shipped_schema}",
    })

    # 11. chainlog building block exists and parses
    chainlog_md = skill_path(skills_dir, "blocks", "project", "chainlog", "SKILL.md")
    rc, out, err = run([
        sys.executable, str(skill_path(skills_dir, "blocks", "authoring", "parse-skill-frontmatter", "scripts", "parse-skill-frontmatter.py")),
        str(chainlog_md), "--json",
    ])
    data = json.loads(out)
    results.append({
        "step": "chainlog-present",
        "pass": chainlog_md.is_file() and data.get("name") == "chainlog",
        "rc": rc,
        "error": err if not chainlog_md.is_file() else "",
    })

    # 12. check-chainlog-needs subagent exists
    check_chainlog_md = skill_path(skills_dir, "main", "authoring", "write-a-skill", "subagents", "check-chainlog-needs.md")
    results.append({
        "step": "check-chainlog-needs-present",
        "pass": check_chainlog_md.is_file(),
        "rc": 0,
        "error": "" if check_chainlog_md.is_file() else f"Missing {check_chainlog_md}",
    })

    # 13. chainlog templates exist
    templates = [
        "chainlog-template-producer.md",
        "chainlog-template-consumer.md",
        "chainlog-template-both.md",
        "chainlog-template-neither.md",
    ]
    template_dir = skill_path(skills_dir, "main", "authoring", "write-a-skill", "references")
    all_templates_present = all((template_dir / t).is_file() for t in templates)
    results.append({
        "step": "chainlog-templates-present",
        "pass": all_templates_present,
        "rc": 0,
        "error": "" if all_templates_present else "Missing one or more chainlog templates.",
    })

    # 14. audit-skill reports chainlog findings on a chainlog-using fixture
    with tempfile.TemporaryDirectory(prefix="write-a-skill-chainlog-") as tmp:
        fixture_dir = Path(tmp) / "chainlog-consumer-fixture"
        fixture_dir.mkdir()
        fixture_skill_md = """---
name: chainlog-consumer-fixture
description: A fixture skill that consumes chainlog observations without declaring artifact-freshness.
version: 1.0.0
invocation: model-invoked
---

# chainlog-consumer-fixture

## Purpose

Fixture for testing chainlog audit rules.

## Type

Building block.

## In scope

- Query chainlog for the latest observation per capability.
- Synthesize a pass/fail decision.

## Out of scope

- Collecting new data from tools.

## References

- [Chainlog](references/chainlog.md)
"""
        chainlog_decl = """# chainlog-consumer-fixture chainlog declaration

## Classification

`chainlog-consumer-fixture` is a **consumer** of chainlog observations.

Rationale: The skill reads prior observations from the chainlog and makes a decision.

## Consumed capabilities

| Capability | Purpose | Freshness rule | Query point |
| ---------- | ------- | -------------- | ----------- |
| pr-source | Evaluate the current PR state | New commit or CI run | Before deciding |
"""
        (fixture_dir / "SKILL.md").write_text(fixture_skill_md, encoding="utf-8")
        (fixture_dir / "references").mkdir()
        (fixture_dir / "references" / "chainlog.md").write_text(chainlog_decl, encoding="utf-8")

        rc, out, err = run([
            sys.executable, str(skill_path(skills_dir, "blocks", "authoring", "audit-skill", "scripts", "audit-skill.py")),
            str(fixture_dir), "--json",
        ])
        try:
            data = json.loads(out)
            findings = {f["id"]: f for f in data.get("findings", [])}
            cl02 = findings.get("CL-02", {})
            results.append({
                "step": "audit-chainlog-consumer-finds-cl-02",
                "pass": rc == 0 and cl02.get("result") == "FAIL" and cl02.get("id") == "CL-02",
                "rc": rc,
                "error": err,
            })
        except Exception as exc:
            results.append({
                "step": "audit-chainlog-consumer-finds-cl-02",
                "pass": False,
                "rc": rc,
                "error": f"{err}; parse error: {exc}",
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
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
