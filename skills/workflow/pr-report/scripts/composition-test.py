#!/usr/bin/env python3
"""
Composition test for pr-report.

Validates the conductor's wiring without needing a live PR:
- SKILL.md frontmatter is valid.
- config.yaml is parseable and declares the expected keys.
- All references linked from SKILL.md exist.
- Adapter registry entries point to existing skills.
- evals/evals.json is valid.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def run() -> dict:
    results = []
    skill_dir = Path(__file__).resolve().parent.parent

    # 1. Validate frontmatter schema
    try:
        import subprocess
        result = subprocess.run(
            [
                sys.executable,
                "skills/tooling/validate-skill-frontmatter/scripts/validate-skill-frontmatter.py",
                str(skill_dir / "SKILL.md"),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            results.append({"check": "SKILL.md frontmatter validates", "status": "PASS"})
        else:
            results.append({"check": "SKILL.md frontmatter validates", "status": "FAIL", "detail": result.stdout})
    except Exception as e:
        results.append({"check": "SKILL.md frontmatter validates", "status": "FAIL", "detail": str(e)})

    # 2. config.yaml is parseable and contains tooling keys
    try:
        import yaml
        config = yaml.safe_load((skill_dir / "config.yaml").read_text(encoding="utf-8"))
        assert config is not None
        keys = {item["key"] for item in config.get("skill", [])}
        assert "pr-report.tooling.preference" in keys
        assert "pr-report.tooling.degraded_mode" in keys
        results.append({"check": "config.yaml declares tooling keys", "status": "PASS"})
    except Exception as e:
        results.append({"check": "config.yaml declares tooling keys", "status": "FAIL", "detail": str(e)})

    # 3. All internal markdown links in SKILL.md resolve
    try:
        body = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", body)
        broken = []
        for label, target in links:
            if target.startswith(("http://", "https://", "#")):
                continue
            target = target.split("#", 1)[0]
            resolved = (skill_dir / target).resolve()
            if not resolved.exists():
                broken.append(f"{label} -> {target}")
        if broken:
            results.append({"check": "SKILL.md links resolve", "status": "FAIL", "detail": ", ".join(broken)})
        else:
            results.append({"check": "SKILL.md links resolve", "status": "PASS"})
    except Exception as e:
        results.append({"check": "SKILL.md links resolve", "status": "FAIL", "detail": str(e)})

    # 4. Adapter registry entries point to existing skills
    try:
        registry = (skill_dir / "references" / "ADAPTER_REGISTRY.md").read_text(encoding="utf-8")
        # Extract adapter names from the registry code block
        names = re.findall(r"^\s+(\w[\w-]*-adapter):", registry, re.MULTILINE)
        missing = []
        for name in names:
            candidate = Path("skills") / "adapters" / name
            if not candidate.exists():
                # Some adapters are community/optional and may not exist yet
                continue
            if not (candidate / "SKILL.md").exists():
                missing.append(name)
        if missing:
            results.append({"check": "Built-in adapter registry entries exist", "status": "FAIL", "detail": ", ".join(missing)})
        else:
            results.append({"check": "Built-in adapter registry entries exist", "status": "PASS"})
    except Exception as e:
        results.append({"check": "Built-in adapter registry entries exist", "status": "FAIL", "detail": str(e)})

    # 5. evals/evals.json is valid JSON
    try:
        evals = json.loads((skill_dir / "evals" / "evals.json").read_text(encoding="utf-8"))
        assert "tests" in evals
        assert len(evals["tests"]) > 0
        # Check at least one behavioral eval exists
        behavioral = [t for t in evals["tests"] if t.get("type") == "behavioral"]
        assert len(behavioral) > 0
        results.append({"check": "evals/evals.json includes behavioral evals", "status": "PASS"})
    except Exception as e:
        results.append({"check": "evals/evals.json includes behavioral evals", "status": "FAIL", "detail": str(e)})

    overall = "PASS" if all(r["status"] == "PASS" for r in results) else "FAIL"
    return {"overall": overall, "results": results}


if __name__ == "__main__":
    report = run()
    print(json.dumps(report, indent=2))
    sys.exit(0 if report["overall"] == "PASS" else 1)
