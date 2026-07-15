#!/usr/bin/env python3
"""
Composition test for pr-report.

Validates the conductor's wiring without needing a live PR:
- SKILL.md frontmatter is valid.
- config.yaml is parseable and declares the expected provider/tooling keys.
- All internal markdown links in SKILL.md, references/*.md, and subagents/*.md resolve.
- evals/evals.json is valid and includes at least one behavioral eval.
- No legacy adapter names remain in the skill files.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
SKILL_MD = SKILL_DIR / "SKILL.md"
CONFIG_YAML = SKILL_DIR / "config.yaml"
REFERENCES_DIR = SKILL_DIR / "references"
SUBAGENTS_DIR = SKILL_DIR / "subagents"
EVALS_JSON = SKILL_DIR / "evals" / "evals.json"

ADAPTER_NAMES = {
    "github-pr-adapter",
    "github-actions-adapter",
    "sonarcloud-adapter",
    "jira-adapter",
    "manual-pr-adapter",
    "pr-adapter-contract",
}

REQUIRED_CONFIG_KEYS = {
    "pr-report.tools.pr.provider",
    "pr-report.tools.pr.repo",
    "pr-report.tools.ci.provider",
    "pr-report.tools.static_analysis.provider",
    "pr-report.tools.issue_tracker.provider",
    "pr-report.tooling.preference",
    "pr-report.tooling.degraded_mode",
    "pr-report.scope_mode",
    "pr-report.task_list.enabled",
    "pr-report.test_mode",
}


def validate_frontmatter() -> dict:
    try:
        import subprocess
        result = subprocess.run(
            [
                sys.executable,
                "skills/tooling/validate-skill-frontmatter/scripts/validate-skill-frontmatter.py",
                str(SKILL_MD),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return {"check": "SKILL.md frontmatter validates", "status": "PASS"}
        return {"check": "SKILL.md frontmatter validates", "status": "FAIL", "detail": result.stdout}
    except Exception as e:
        return {"check": "SKILL.md frontmatter validates", "status": "FAIL", "detail": str(e)}


def validate_config() -> dict:
    try:
        import yaml
        config = yaml.safe_load(CONFIG_YAML.read_text(encoding="utf-8"))
        assert config is not None
        keys = {item["key"] for item in config.get("skill", [])}
        missing = REQUIRED_CONFIG_KEYS - keys
        if missing:
            return {
                "check": "config.yaml declares provider/tooling keys",
                "status": "FAIL",
                "detail": f"Missing keys: {', '.join(sorted(missing))}",
            }
        return {"check": "config.yaml declares provider/tooling keys", "status": "PASS"}
    except Exception as e:
        return {"check": "config.yaml declares provider/tooling keys", "status": "FAIL", "detail": str(e)}


def extract_links(text: str) -> list[tuple[str, str]]:
    return re.findall(r"\[([^\]]+)\]\(([^)]+)\)", text)


def check_links(path: Path, text: str) -> list[str]:
    broken = []
    for label, target in extract_links(text):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = target.split("#", 1)[0]
        resolved = (path.parent / target).resolve()
        if not resolved.exists():
            broken.append(f"{label} -> {target}")
    return broken


def validate_links() -> dict:
    try:
        broken = []
        broken.extend(check_links(SKILL_MD, SKILL_MD.read_text(encoding="utf-8")))
        for ref in REFERENCES_DIR.glob("*.md"):
            broken.extend(check_links(ref, ref.read_text(encoding="utf-8")))
        for subagent in SUBAGENTS_DIR.glob("*.md"):
            broken.extend(check_links(subagent, subagent.read_text(encoding="utf-8")))
        if broken:
            return {
                "check": "All internal markdown links resolve",
                "status": "FAIL",
                "detail": "; ".join(broken[:20]),
            }
        return {"check": "All internal markdown links resolve", "status": "PASS"}
    except Exception as e:
        return {"check": "All internal markdown links resolve", "status": "FAIL", "detail": str(e)}


def validate_evals() -> dict:
    try:
        evals = json.loads(EVALS_JSON.read_text(encoding="utf-8"))
        assert "tests" in evals
        assert len(evals["tests"]) > 0
        behavioral = [t for t in evals["tests"] if t.get("type") == "behavioral"]
        assert len(behavioral) > 0
        return {"check": "evals/evals.json includes behavioral evals", "status": "PASS"}
    except Exception as e:
        return {"check": "evals/evals.json includes behavioral evals", "status": "FAIL", "detail": str(e)}


def validate_no_adapter_names() -> dict:
    try:
        found = []
        migration_files = {
            (REFERENCES_DIR / "VERSIONING.md").resolve(),
            (REFERENCES_DIR / "WORKFLOW.md").resolve(),
            (REFERENCES_DIR / "DEPENDENCIES.md").resolve(),
        }
        for path in [SKILL_MD, CONFIG_YAML] + list(REFERENCES_DIR.glob("*.md")) + list(SUBAGENTS_DIR.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            for name in ADAPTER_NAMES:
                if name in text:
                    if path.resolve() not in migration_files:
                        found.append(f"{name} in {path.relative_to(SKILL_DIR)}")
        if found:
            return {
                "check": "No adapter names remain in skill files",
                "status": "FAIL",
                "detail": "; ".join(found[:20]),
            }
        return {"check": "No adapter names remain in skill files", "status": "PASS"}
    except Exception as e:
        return {"check": "No adapter names remain in skill files", "status": "FAIL", "detail": str(e)}


def run() -> dict:
    results = [
        validate_frontmatter(),
        validate_config(),
        validate_links(),
        validate_evals(),
        validate_no_adapter_names(),
    ]
    overall = "PASS" if all(r["status"] == "PASS" for r in results) else "FAIL"
    return {"overall": overall, "results": results}


if __name__ == "__main__":
    report = run()
    print(json.dumps(report, indent=2))
    sys.exit(0 if report["overall"] == "PASS" else 1)
