#!/usr/bin/env python3
"""
audit-skill.py

Check a skill against the skill fundamentals and produce a structured audit report.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

# Regex patterns
SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"]?[a-z0-9_\-]{16,}['\"]?"),
    re.compile(r"(?i)(password|passwd|pwd|secret|token)\s*[:=]\s*['\"]?[^\s'\"]+['\"]?"),
    re.compile(r"(?i)(bearer|basic)\s+[a-z0-9_\-]{20,}"),
    re.compile(r"-----BEGIN (RSA |OPENSSH |PGP )?PRIVATE KEY-----"),
]

HARNESS_COMMANDS = [
    r"\bpi\s+",
    r"\bcodex\s+",
    r"\bclaude\s+",
    r"\bcursor\s+",
]

PI_REFERENCES = [
    r"(?i)\bpi\b\s+(?:coding[- ]?agent|agent|harness|tool|skills?|cli|app)",
    r"\bpi-coding-agent\b",
]

HARDCODED_PATH_PATTERNS = [
    re.compile(r"C:\\\\Users\\\\[^\s]+"),
    re.compile(r"/home/[^\s/]+/"),
    re.compile(r"/Users/[^\s/]+/"),
]


def finding(id: str, category: str, severity: str, check: str, result: str, recommendation: str) -> dict:
    """Return a single audit finding."""
    return {
        "id": id,
        "category": category,
        "severity": severity,
        "check": check,
        "result": result,
        "recommendation": recommendation,
    }


def pass_finding(id: str, category: str, severity: str, check: str) -> dict:
    return finding(id, category, severity, check, "PASS", "—")


def fail_finding(id: str, category: str, severity: str, check: str, recommendation: str) -> dict:
    return finding(id, category, severity, check, "FAIL", recommendation)


def manual_finding(id: str, category: str, severity: str, check: str, recommendation: str) -> dict:
    return finding(id, category, severity, check, "MANUAL", recommendation)


def na_finding(id: str, category: str, severity: str, check: str) -> dict:
    return finding(id, category, severity, check, "N/A", "—")


def find_skill_md(skill_dir: Path) -> Optional[Path]:
    if skill_dir.is_file():
        return skill_dir
    candidate = skill_dir / "SKILL.md"
    return candidate if candidate.is_file() else None


def parse_frontmatter(skill_md: Path) -> dict:
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end].strip()

    # Prefer PyYAML if available for robust nested parsing
    try:
        import yaml
        data = yaml.safe_load(block) or {}
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    # Fallback: simple top-level key parser
    data = {}
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        if line[0].isspace():
            continue
        key, _, value = stripped.partition(":")
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def extract_body(skill_md: Path) -> str:
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    if end == -1:
        return text
    return text[end + 4 :]


def collect_files(skill_dir: Path) -> list[Path]:
    files = []
    if skill_dir.is_file():
        return [skill_dir]
    for pattern in ["**/*.md", "**/*.py", "**/*.json", "**/*.yaml", "**/*.yml"]:
        files.extend(skill_dir.glob(pattern))
    return files


def find_markdown_links(text: str) -> list[str]:
    # [label](path)
    return re.findall(r"\[([^\]]+)\]\(([^)]+)\)", text)


def resolve_link(md_file: Path, link: str) -> bool:
    if link.startswith("http://") or link.startswith("https://") or link.startswith("#"):
        return True
    target = (md_file.parent / link).resolve()
    return target.exists()


def check_identities(skill_dir: Path, skill_md: Path, fm: dict) -> list[dict]:
    findings = []
    name = fm.get("name", "")
    expected_name = skill_dir.name if skill_dir.is_dir() else skill_dir.parent.name
    check = "`name` matches directory and uses allowed charset"

    if not name:
        findings.append(fail_finding("F01", "Identity", "blocker", check, "Add a `name` field to the frontmatter that matches the directory name."))
    elif not re.match(r"^[a-z0-9-]+$", name):
        findings.append(fail_finding("F01", "Identity", "blocker", check, f"Rename the skill to use only lowercase letters, digits, and hyphens (current: `{name}`)."))
    elif name != expected_name:
        findings.append(fail_finding("F01", "Identity", "blocker", check, f"Frontmatter name `{name}` does not match directory `{expected_name}`."))
    else:
        findings.append(pass_finding("F01", "Identity", "blocker", check))

    description = fm.get("description", "")
    check = "`description` is present and ≤ 1024 chars"
    if not description or len(description) > 1024:
        findings.append(fail_finding("F02", "Identity", "blocker", check, "Add a description between 1 and 1024 characters."))
    else:
        findings.append(pass_finding("F02", "Identity", "blocker", check))

    findings.append(manual_finding("F03", "Identity", "warning", "`description` front-loads the leading word or domain", "Review the description: the first 10–15 words should name the core action or domain."))
    findings.append(manual_finding("F04", "Identity", "warning", "`description` lists distinct triggers, not synonyms", "Review the description: each trigger should map to a distinct branch or intent."))

    version = fm.get("version", "")
    check = "`version` is valid SemVer if present, especially once shared or consumed"
    semver_re = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*)?(?:\+[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*)?$"
    if version:
        if not re.match(semver_re, version):
            findings.append(manual_finding("F05", "Identity", "warning", check, f"Use a valid SemVer version if you keep `version` (current: `{version}`)."))
        else:
            findings.append(pass_finding("F05", "Identity", "warning", check))
    else:
        findings.append(pass_finding("F05", "Identity", "warning", check))

    check = "`invocation` is `model-invoked` or `user-invoked`"
    invocation = fm.get("invocation", "")
    if invocation in ("model-invoked", "user-invoked"):
        findings.append(pass_finding("F06", "Identity", "blocker", check))
    else:
        findings.append(fail_finding("F06", "Identity", "blocker", check, "Set `invocation` to `model-invoked` or `user-invoked`."))

    metadata = fm.get("metadata", {})
    author = metadata.get("author") if isinstance(metadata, dict) else None
    tags = metadata.get("tags") if isinstance(metadata, dict) else None
    check = "`metadata` includes author and tags"
    if author and tags:
        findings.append(pass_finding("F07", "Identity", "warning", check))
    else:
        findings.append(fail_finding("F07", "Identity", "warning", check, "Add `metadata.author` and `metadata.tags` to the frontmatter."))

    findings.append(manual_finding("F08", "Identity", "blocker", "Frontmatter validates against JSON schema", "Run `validate-skill-frontmatter` for a full schema check."))

    return findings


def check_type_and_shape(skill_dir: Path, body: str) -> list[dict]:
    findings = []
    type_keywords = ["building block", "conductor", "wrapper", "multi-layer"]
    has_type = any(kw in body.lower() for kw in type_keywords)
    check = "Skill type is declared or clearly implied"
    if has_type:
        findings.append(pass_finding("T01", "Type", "blocker", check))
    else:
        findings.append(fail_finding("T01", "Type", "blocker", check, "Declare whether the skill is a building block, conductor, wrapper, or multi-layer skill."))

    findings.append(manual_finding("T02", "Type", "blocker", "Content matches the declared type", "Review that the skill's behavior matches its declared type."))
    findings.append(manual_finding("T03", "Type", "warning", "Multi-layer skills have a clear primary role", "If the skill has multiple roles, make the primary role explicit."))

    branch_header = re.search(r"\|\s*Branch\s*\|\s*Trigger\s*\|\s*Outcome\s*\|", body)
    check = "Branch entry is explicit if the skill has multiple paths"
    if branch_header or "branch" in body.lower():
        findings.append(finding("T04", "Type", "warning", check, "PASS" if branch_header else "MANUAL", "List branches with triggers and outcomes in a table if the skill has multiple paths."))
    else:
        findings.append(manual_finding("T04", "Type", "warning", check, "If the skill has multiple paths, list branches with triggers and outcomes."))
    return findings


def check_scope(body: str) -> list[dict]:
    findings = []
    in_scope = re.search(r"(?i)##\s*in scope", body) or re.search(r"(?i)##\s*when to use", body)
    out_scope = re.search(r"(?i)##\s*out of scope", body)
    objective = re.search(r"(?i)##\s*(purpose|objective|what this skill does)", body)

    findings.append(finding("S01", "Scope", "blocker", "One core objective is stated", "PASS" if objective else "MANUAL", "State a single core objective in a Purpose or Objective section."))
    findings.append(finding("S02", "Scope", "blocker", "In-scope is explicit and bounded", "PASS" if in_scope else "FAIL", "Add an explicit 'In scope' or 'When to use' section."))
    findings.append(finding("S03", "Scope", "blocker", "Out-of-scope is explicit", "PASS" if out_scope else "FAIL", "Add an explicit 'Out of scope' section."))
    findings.append(manual_finding("S04", "Scope", "warning", "Scope boundaries do not contradict each other", "Review in-scope and out-of-scope lists for overlap."))
    return findings


def check_structure(skill_dir: Path, skill_md: Path, body: str, files: list[Path]) -> list[dict]:
    findings = []
    check = "`SKILL.md` exists"
    if skill_md and skill_md.is_file():
        findings.append(pass_finding("ST01", "Structure", "blocker", check))
    else:
        findings.append(fail_finding("ST01", "Structure", "blocker", check, "Create a `SKILL.md` file."))
        return findings

    empty_optional = []
    for d in ["references", "subagents", "scripts", "assets"]:
        dpath = skill_dir / d if skill_dir.is_dir() else None
        if dpath and dpath.exists() and not any(dpath.iterdir()):
            empty_optional.append(d)

    check = "Optional directories contain content if present"
    if empty_optional:
        findings.append(fail_finding("ST02", "Structure", "warning", check, f"Remove empty directories or add content: {', '.join(empty_optional)}."))
    else:
        findings.append(pass_finding("ST02", "Structure", "warning", check))

    readme = (skill_dir / "README.md") if skill_dir.is_dir() else None
    has_extras = any(
        (skill_dir / d).exists() for d in ["references", "subagents", "scripts"]
    ) if skill_dir.is_dir() else False

    check = "`README.md` exists for non-trivial skills"
    if readme and readme.is_file():
        findings.append(pass_finding("ST03", "Structure", "warning", check))
    elif has_extras:
        findings.append(fail_finding("ST03", "Structure", "warning", check, "Add a `README.md` because the skill has supporting directories."))
    else:
        findings.append(manual_finding("ST03", "Structure", "warning", check, "Add a `README.md` if the skill has multiple files or patterns."))

    # Check links in SKILL.md and all reference markdown files.
    md_files = [f for f in files if f.suffix == ".md"]
    broken = []
    for md_file in md_files:
        try:
            text = md_file.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        links = find_markdown_links(text)
        for label, target in links:
            if not resolve_link(md_file, target):
                broken.append(f"{md_file.name}:{label} -> {target}")
    check = "Reference links resolve"
    if broken:
        findings.append(fail_finding("ST04", "Structure", "blocker", check, f"Fix broken internal links: {', '.join(broken[:5])}."))
    else:
        findings.append(pass_finding("ST04", "Structure", "blocker", check))

    findings.append(manual_finding("ST05", "Structure", "warning", "Progressive disclosure is used correctly", "Keep deep detail in `references/` and top-level guidance focused."))
    return findings


def check_form_and_style(files: list[Path], body: str) -> list[dict]:
    findings = []
    for fid, severity, check, recommendation in [
        ("FS01", "warning", "Every line is load-bearing", "Review whether each line changes behavior; remove sediment."),
        ("FS02", "warning", "No duplication with context files or other skills", "Remove guidance that belongs in workspace context files or other skills."),
        ("FS03", "warning", "Completion criteria are checkable", "Ensure every step ends with an observable completion criterion."),
        ("FS04", "suggestion", "Leading words are used where appropriate", "Anchor key concepts in compact, reusable terms."),
        ("FS05", "warning", "Negations are paired with positive directives", "Pair every 'do not X' with a 'do Y' counterpart."),
    ]:
        findings.append(manual_finding(fid, "Form and style", severity, check, recommendation))

    check = "Language is harness-agnostic and project-agnostic"
    has_harness = any(re.search(p, body) for p in HARNESS_COMMANDS)
    if has_harness:
        findings.append(fail_finding("FS06", "Form and style", "blocker", check, "Avoid hardcoded harness commands in the portable core; use detection or config."))
    else:
        findings.append(manual_finding("FS06", "Form and style", "blocker", check, "Avoid hardcoded harness commands in the portable core; use detection or config."))

    check = "No harness-specific product references or active local skills used as examples"
    md_text = ""
    for f in files:
        if f.suffix == ".md":
            try:
                md_text += f.read_text(encoding="utf-8", errors="replace") + "\n"
            except Exception:
                pass
    has_pi = any(re.search(p, md_text, re.IGNORECASE) for p in PI_REFERENCES)
    if has_pi:
        findings.append(fail_finding("FS07", "Form and style", "blocker", check, "Remove references to agent harness names or active local skills in standards-facing docs; use fictional examples."))
    else:
        findings.append(pass_finding("FS07", "Form and style", "blocker", check))
    return findings


def check_security(skill_dir: Path, files: list[Path]) -> list[dict]:
    findings = []
    secrets_found = []
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
            if any(pat.search(text) for pat in SECRET_PATTERNS):
                secrets_found.append(str(f))
        except Exception:
            pass

    check = "No secrets in files"
    if secrets_found:
        findings.append(fail_finding("SE01", "Security", "blocker", check, f"Remove potential secrets from: {', '.join(secrets_found[:5])}."))
    else:
        findings.append(pass_finding("SE01", "Security", "blocker", check))

    body_text = ""
    if files:
        try:
            body_text = files[0].read_text(encoding="utf-8", errors="replace")
        except Exception:
            pass
    check = "Destructive actions require confirmation"
    has_confirmation = any(kw in body_text.lower() for kw in ["confirm", "approval", "approve", "explicit"])
    if has_confirmation:
        findings.append(pass_finding("SE02", "Security", "blocker", check))
    else:
        findings.append(manual_finding("SE02", "Security", "blocker", check, "Gate writes, overwrites, deletes, and installs behind explicit user approval."))

    findings.append(manual_finding("SE03", "Security", "blocker", "Fail closed on missing capabilities", "Stop and explain when a required tool, binary, or environment variable is missing."))
    findings.append(manual_finding("SE04", "Security", "warning", "Untrusted projects are handled safely", "Prefer read-only inspection when project trust is unknown."))
    return findings


def check_dependencies(skill_dir: Path, body: str) -> list[dict]:
    findings = []
    has_skills_json = (skill_dir / "skills.json").is_file() if skill_dir.is_dir() else False
    has_deps_md = (skill_dir / "references" / "DEPENDENCIES.md").is_file() if skill_dir.is_dir() else False
    deps_declared = has_skills_json or has_deps_md

    for fid, severity, check, recommendation in [
        ("D01", "blocker", "Required tools are declared", "List required tools in `skills.json` or `references/DEPENDENCIES.md`."),
        ("D02", "blocker", "Required binaries are declared", "List required binaries in `requirements.binaries`."),
        ("D03", "blocker", "Required MCP servers are declared", "List required MCP servers by name and capability."),
        ("D04", "blocker", "Skill dependencies are declared", "List required skills in `requirements.skills`."),
        ("D05", "warning", "Environment variables are declared", "List environment variables used by the skill."),
    ]:
        if fid in ("D01", "D02", "D03", "D04"):
            result = "PASS" if deps_declared else "MANUAL"
        else:
            result = "MANUAL"
        findings.append(finding(fid, "Dependencies", severity, check, result, recommendation))
    return findings


def _discover_skill_names(skill_dir: Path) -> set[str]:
    """Return the set of skill directory names in the surrounding skills/ directory."""
    skills_root = None
    if skill_dir.is_dir():
        candidate = skill_dir.parent
        if candidate.name == "skills":
            skills_root = candidate
    if not skills_root:
        return set()
    return {d.name for d in skills_root.iterdir() if d.is_dir() and (d / "SKILL.md").is_file()}


def _referenced_skill_names(skill_dir: Path, files: list[Path]) -> set[str]:
    """Scan Python files for runtime references to other skill scripts or directories."""
    references = set()
    skill_names = _discover_skill_names(skill_dir)
    for f in files:
        if f.suffix != ".py":
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for skill_name in skill_names:
            if skill_name == skill_dir.name:
                continue
            # Look for the skill name inside a filesystem path or command string.
            # This catches imports via importlib and subprocess calls to other skill scripts.
            pattern = re.compile(
                r'["\'][^"\']*' + re.escape(skill_name) + r'[/\\][^"\']*["\']'
            )
            if pattern.search(text):
                references.add(skill_name)
    return references


def check_dependency_references(skill_dir: Path, fm: dict, files: list[Path]) -> list[dict]:
    """Check that runtime references to other skills are declared in `depends`."""
    findings = []
    depends = fm.get("depends", []) or []
    if not isinstance(depends, list):
        depends = []
    declared = set(depends)

    referenced = _referenced_skill_names(skill_dir, files)
    missing = referenced - declared

    check = "Runtime references to other skills are declared in `depends`"
    if missing:
        findings.append(fail_finding("D06", "Dependencies", "blocker", check, f"Add {sorted(missing)} to `depends` in `SKILL.md` frontmatter."))
    else:
        findings.append(pass_finding("D06", "Dependencies", "blocker", check))
    return findings


def check_portability(skill_dir: Path, body: str) -> list[dict]:
    findings = []
    check = "No hardcoded project-specific paths"
    has_hardcoded = any(p.search(body) for p in HARDCODED_PATH_PATTERNS)
    if has_hardcoded:
        findings.append(fail_finding("P01", "Portability", "blocker", check, "Use detection, config, or ask the user instead of hardcoding paths."))
    else:
        findings.append(manual_finding("P01", "Portability", "blocker", check, "Use detection, config, or ask the user instead of hardcoding paths."))

    findings.append(manual_finding("P02", "Portability", "warning", "Global/pluggable skills detect environment", "Global skills should use `detect-project-context` or equivalent."))
    findings.append(manual_finding("P03", "Portability", "suggestion", "Degradation behavior is documented", "Document what happens when a feature is unsupported by the harness."))
    return findings


def check_evaluation(skill_dir: Path, fm: dict) -> list[dict]:
    findings = []
    invocation = fm.get("invocation", "")
    has_evals = (skill_dir / "evals" / "evals.json").is_file() if skill_dir.is_dir() else False
    check = "Model-invoked skills have trigger evals"

    if invocation == "model-invoked":
        if has_evals:
            findings.append(pass_finding("E01", "Evaluation", "warning", check))
        else:
            findings.append(fail_finding("E01", "Evaluation", "warning", check, "Create `evals/evals.json` with should-trigger and should-not-trigger cases."))
    else:
        findings.append(na_finding("E01", "Evaluation", "warning", check))

    for fid, severity, check, recommendation in [
        ("E02", "suggestion", "Behavioral evals compare with-skill vs baseline", "Add behavioral evals that compare output with and without the skill."),
        ("E03", "warning", "Discipline skills have pressure tests", "Add pressure tests against the documented failure pattern."),
        ("E04", "warning", "Composition tests exist for composable skills", "Add composition tests for conductor and building-block skills."),
    ]:
        findings.append(manual_finding(fid, "Evaluation", severity, check, recommendation))
    return findings


def check_governance(fm: dict) -> list[dict]:
    findings = []
    check = "License is declared if distributed"
    if fm.get("license"):
        findings.append(pass_finding("G01", "Governance", "warning", check))
    else:
        findings.append(manual_finding("G01", "Governance", "warning", check, "Add a `license` field if the skill is distributed."))

    metadata = fm.get("metadata", {})
    check = "Verification level is declared if distributed"
    if isinstance(metadata, dict) and metadata.get("verification_level"):
        findings.append(pass_finding("G02", "Governance", "warning", check))
    else:
        findings.append(manual_finding("G02", "Governance", "warning", check, "Add `metadata.verification_level` if the skill is distributed."))

    return findings


def audit(skill_path: str) -> dict:
    skill_dir = Path(skill_path).expanduser().resolve()
    skill_md = find_skill_md(skill_dir)

    if not skill_md:
        return {
            "skill": skill_dir.name,
            "summary": {"blockers": 1, "warnings": 0, "suggestions": 0, "overall": "FAIL"},
            "findings": [{
                "id": "ST01",
                "category": "Structure",
                "severity": "blocker",
                "check": "`SKILL.md` exists",
                "result": "FAIL",
                "recommendation": "No SKILL.md found in the target path.",
            }],
            "remediation": ["Create a SKILL.md file in the skill directory."],
        }

    fm = parse_frontmatter(skill_md)
    body = extract_body(skill_md)
    files = collect_files(skill_dir if skill_dir.is_dir() else skill_dir.parent)

    findings = []
    findings.extend(check_identities(skill_dir if skill_dir.is_dir() else skill_dir.parent, skill_md, fm))
    findings.extend(check_type_and_shape(skill_dir if skill_dir.is_dir() else skill_dir.parent, body))
    findings.extend(check_scope(body))
    findings.extend(check_structure(skill_dir if skill_dir.is_dir() else skill_dir.parent, skill_md, body, files))
    findings.extend(check_form_and_style(files, body))
    findings.extend(check_security(skill_dir if skill_dir.is_dir() else skill_dir.parent, files))
    findings.extend(check_dependencies(skill_dir if skill_dir.is_dir() else skill_dir.parent, body))
    findings.extend(check_dependency_references(skill_dir if skill_dir.is_dir() else skill_dir.parent, fm, files))
    findings.extend(check_portability(skill_dir if skill_dir.is_dir() else skill_dir.parent, body))
    findings.extend(check_evaluation(skill_dir if skill_dir.is_dir() else skill_dir.parent, fm))
    findings.extend(check_governance(fm))

    counts = {"blockers": 0, "warnings": 0, "suggestions": 0, "manual": 0}
    remediation = []
    severity_key = {"blocker": "blockers", "warning": "warnings", "suggestion": "suggestions"}
    for f in findings:
        if f["result"] == "FAIL":
            key = severity_key.get(f["severity"].lower(), f["severity"].lower())
            counts[key] = counts.get(key, 0) + 1
            remediation.append(f"{f['id']}: {f['recommendation']}")
        elif f["result"] == "MANUAL":
            counts["manual"] = counts.get("manual", 0) + 1
            remediation.append(f"{f['id']}: {f['recommendation']}")

    overall = "FAIL" if counts["blockers"] > 0 else "PASS"
    return {
        "skill": skill_dir.name,
        "summary": {
            "blockers": counts["blockers"],
            "warnings": counts["warnings"],
            "suggestions": counts["suggestions"],
            "overall": overall,
        },
        "findings": findings,
        "remediation": remediation,
    }


def render_markdown(report: dict) -> str:
    lines = [
        f"# Audit report: {report['skill']}",
        "",
        "## Summary",
        f"- Blockers: {report['summary']['blockers']}",
        f"- Warnings: {report['summary']['warnings']}",
        f"- Suggestions: {report['summary']['suggestions']}",
        f"- Overall: {report['summary']['overall']}",
        "",
        "## Findings",
        "| ID | Category | Severity | Check | Result | Recommendation |",
        "|---|---|---|---|---|---|",
    ]
    for f in report["findings"]:
        lines.append(
            f"| {f['id']} | {f['category']} | {f['severity']} | {f['check']} | {f['result']} | {f['recommendation']} |"
        )
    lines.extend([
        "",
        "## Remediation plan",
    ])
    for r in report["remediation"]:
        lines.append(f"- {r}")
    if not report["remediation"]:
        lines.append("- No remediation required.")
    return "\n".join(lines)


def main():
    # Ensure UTF-8 output on platforms that default to a legacy code page.
    sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Audit a skill against the fundamentals.")
    parser.add_argument("skill_path", help="Path to the skill directory or SKILL.md file.")
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    args = parser.parse_args()

    report = audit(args.skill_path)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(render_markdown(report))


if __name__ == "__main__":
    main()
