#!/usr/bin/env python3
"""
eval-write-a-skill.py

Static behavioral eval for the write-a-skill skill in the workspace.
Produces a markdown report in the project context directory.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

SKILL_DIR = Path("G:/My Drive/.agents/skills/write-a-skill")
CONTEXT_DIR = Path("G:/My Drive/.agents/context")
REPORT_PATH = CONTEXT_DIR / "skill-eval" / f"write-a-skill-eval-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_links(text: str, base: Path) -> list[str]:
    missing = []
    for target in re.findall(r'\[([^\]]+)\]\(([^)]+)\)', text):
        label, url = target
        if url.startswith("http"):
            continue
        if not (base / url).exists():
            missing.append(f"[{label}]({url})")
    return missing


def count_section_items(text: str, heading: str) -> int:
    """Count bullet/numbered items directly under a markdown heading."""
    # Find heading and stop at next heading of same or higher level
    match = re.search(rf"(?m)^##* \s*{re.escape(heading)}.*?(?=\n## |\Z)", text, re.DOTALL)
    if not match:
        return 0
    section = match.group(0)
    # Count lines that start with a bullet or number
    return len(re.findall(r"(?m)^\s*(?:\d+\.|-)\s+", section))


def run_detection_script() -> dict:
    result = subprocess.run(
        [sys.executable, str(SKILL_DIR / "scripts" / "detect-project-layout.py"), "--start", str(CONTEXT_DIR.parent), "--json"],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def main() -> None:
    results: list[dict] = []

    def add(name: str, passed: bool, detail: str = "") -> None:
        results.append({"name": name, "passed": passed, "detail": detail})

    skill_md = read(SKILL_DIR / "SKILL.md")
    readme_md = read(SKILL_DIR / "README.md")
    dependencies_md = read(SKILL_DIR / "references" / "DEPENDENCIES.md")
    eval_md = read(SKILL_DIR / "references" / "EVAL.md")
    self_audit_md = read(SKILL_DIR / "references" / "SELF_AUDIT_CHECKLIST.md")
    branch_workflows_md = read(SKILL_DIR / "references" / "BRANCH_WORKFLOWS.md")
    drafter_md = read(SKILL_DIR / "subagents" / "skill-drafter.md")

    # 1. Invocation declaration
    add("Invocation: user-invoked declared", "invocation: user-invoked" in skill_md)
    add("Invocation: disable-model-invocation declared", "disable-model-invocation: true" in skill_md)

    # 2. No drafting before confirmation
    add(
        "No drafting before confirmation rule",
        ("will not draft files until the design and a self-audit pass the fundamentals" in skill_md
         or re.search(r"Do not proceed to implementation until the user confirms", branch_workflows_md) is not None)
        and re.search(r"Do not start drafting until the design is confirmed", drafter_md) is not None,
    )

    # 3. Self-audit blocks violations
    add(
        "Self-audit checks one core objective",
        "One core objective" in self_audit_md,
    )
    add(
        "Self-audit blocks drafting on failure",
        re.search(r"user explicitly overrides a failed check", skill_md + branch_workflows_md) is not None
        or re.search(r"If the self-audit fails", skill_md + branch_workflows_md) is not None,
    )

    # 4. Path detection used
    detection = run_detection_script()
    add(
        "Path detection returns high confidence",
        detection.get("confidence") == "high",
        detail=f"project_root={detection.get('project_root')}, confidence={detection.get('confidence')}",
    )

    # 5. Workers do not ask users
    workers = list((SKILL_DIR / "subagents").glob("*.md"))
    all_workers_ok = all(
        "Do not ask the user directly" in read(w) and "needs_input" in read(w)
        for w in workers
    )
    add("Workers do not ask users directly", all_workers_ok, detail=f"checked {len(workers)} workers")

    # 6. Completion criteria exist
    branch_sections = ["New skill workflow", "Quick skill workflow", "Review workflow", "Upgrade workflow"]
    criteria_present = all("**Completion criterion:**" in skill_md.split(section)[1].split("##")[0] for section in branch_sections)
    add("Every branch has a completion criterion", criteria_present)

    # 7. No .agents/ hardcoding in wrong places
    allowed = {"PLUGGABILITY.md", "DEPENDENCIES.md", "MAINTENANCE.md", "EVAL.md", "STATE_SCHEMA.md", "CONTEXT_REPORTS.md", "GUIDE_SCRIPT_CURATION.md", "GUIDE_EXAMPLES.md", "detect-project-layout.py"}
    bad_hits = []
    for p in SKILL_DIR.rglob("*"):
        if p.is_file() and p.suffix in {".md", ".py", ".yaml", ".yml", ".txt"}:
            text = read(p)
            for m in re.finditer(r"\.agents/", text):
                if p.name not in allowed:
                    bad_hits.append(str(p.relative_to(SKILL_DIR)))
    add("No .agents/ hardcoding outside detection rules", len(bad_hits) == 0, detail=str(bad_hits) if bad_hits else "")

    # 8. Review is read-only
    review_text = skill_md + branch_workflows_md + read(SKILL_DIR / "subagents" / "skill-reviewer.md")
    add("Review workflow prefers read-only", "read-only" in review_text.lower() or "no files are modified" in review_text.lower())

    # 9. Upgrade confirms changes
    upgrade_worker = read(SKILL_DIR / "subagents" / "skill-upgrader.md")
    add("Upgrade confirms changes", "Do not apply changes without explicit user approval" in upgrade_worker)

    # 10. Branch workflow disclosure
    add("SKILL.md points to BRANCH_WORKFLOWS.md", "references/BRANCH_WORKFLOWS.md" in skill_md)
    add("SKILL.md is under 300 lines", len(skill_md.splitlines()) <= 300, detail=f"{len(skill_md.splitlines())} lines")

    # 11. Python dependency declared
    add("Python dependency declared", "Python 3.x" in dependencies_md)

    # 12. EVAL.md has 10 should-trigger and 10 should-not-trigger
    should_trigger_count = count_section_items(eval_md, "10 should-trigger queries")
    should_not_trigger_count = count_section_items(eval_md, "10 should-not-trigger queries")
    add(
        "EVAL.md has 10/10 trigger evals",
        should_trigger_count >= 10 and should_not_trigger_count >= 10,
        detail=f"should-trigger={should_trigger_count}, should-not-trigger={should_not_trigger_count}",
    )

    # 13. Glossary exists
    add("Glossary exists", (SKILL_DIR / "references" / "GLOSSARY.md").exists())

    # 14. Reference links resolve
    skill_missing = check_links(skill_md, SKILL_DIR)
    readme_missing = check_links(readme_md, SKILL_DIR)
    add("All reference links resolve", len(skill_missing) == 0 and len(readme_missing) == 0, detail=f"missing: {skill_missing + readme_missing}")

    # Generate report
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    report = ["---", f"skill: write-a-skill", f"version: \"3.1\"", f"timestamp: {datetime.now(timezone.utc).isoformat()}", "status: final", "---", "", "# Behavioral eval report: write-a-skill", "", f"**Result:** {passed}/{total} checks passed.", ""]
    for r in results:
        icon = "🟢" if r["passed"] else "🔴"
        report.append(f"- {icon} {r['name']}")
        if r.get("detail"):
            report.append(f"  - {r['detail']}")
    report.append("")
    report.append("## Summary")
    if passed == total:
        report.append("All static behavioral evals passed. The skill is ready for live trigger testing against an agent harness.")
    else:
        report.append("Some static checks failed. Review the red items above before running live trigger tests.")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(report), encoding="utf-8")
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
