#!/usr/bin/env python3
"""
list-available-skills.py

Discover skills already available in the project and user scope by scanning
canonical skill directories and parsing SKILL.md frontmatter.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


PROJECT_CANDIDATES = [
    ".agents/skills",
    ".pi/skills",
    "agents/skills",
    ".claude/skills",
    ".codex/skills",
    ".cursor/skills",
    "skills",
]

USER_CANDIDATES = [
    "~/.agents/skills",
    "~/.pi/skills",
    "~/.claude/skills",
    "~/.codex/skills",
    "~/.cursor/skills",
]


def parse_frontmatter(skill_md: Path) -> dict:
    """Load the shared frontmatter parser lazily and parse a SKILL.md file."""
    parser_path = (
        Path(__file__).resolve().parents[5]
        / "skills"
        / "blocks"
        / "authoring"
        / "parse-skill-frontmatter"
        / "scripts"
        / "parse-skill-frontmatter.py"
    )
    spec = importlib.util.spec_from_file_location(
        "parse_skill_frontmatter", parser_path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.parse_frontmatter(skill_md)

def discover_skills(root: Path, candidates: list[str]) -> list[Path]:
    found = []
    for rel in candidates:
        cand = (root / rel).expanduser().resolve()
        if not cand.is_dir():
            continue
        # Search recursively for SKILL.md files, supporting flat, categorized,
        # and multi-level source layouts like skills/{category}/{subcategory}/{skill}/.
        for skill_md in cand.rglob("SKILL.md"):
            found.append(skill_md)
    return found


def build_record(skill_md: Path, data: dict) -> dict:
    skill_dir = skill_md.parent
    return {
        "name": data.get("name") or skill_dir.name,
        "path": str(skill_dir),
        "invocation": data.get("invocation", "unknown"),
        "version": data.get("version"),
    }


def main():
    parser = argparse.ArgumentParser(
        description="List available skills in the project and user scope."
    )
    parser.add_argument(
        "--project-root", default=".", help="Project root to search from."
    )
    parser.add_argument(
        "--include-user",
        action="store_true",
        default=True,
        help="Include user-scope skill directories.",
    )
    parser.add_argument(
        "--exclude-user",
        action="store_true",
        help="Exclude user-scope skill directories.",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    include_user = args.include_user and not args.exclude_user

    project_files = discover_skills(root, PROJECT_CANDIDATES)
    user_files = []
    if include_user:
        user_root = Path.home()
        user_files = discover_skills(user_root, USER_CANDIDATES)

    records = []
    errors = []

    for skill_md in project_files + user_files:
        try:
            data = parse_frontmatter(skill_md)
            records.append(build_record(skill_md, data))
        except Exception as e:
            errors.append({"path": str(skill_md), "error": str(e)})

    # Deduplicate by path
    seen = set()
    unique_records = []
    for r in records:
        if r["path"] in seen:
            continue
        seen.add(r["path"])
        unique_records.append(r)

    report = {
        "project_scope": [str(f) for f in project_files],
        "user_scope": [str(f) for f in user_files],
        "skills": unique_records,
        "errors": errors,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Project scope: {len(project_files)}")
        print(f"User scope: {len(user_files)}")
        print("Skills:")
        for s in unique_records:
            print(f"  - {s['name']} ({s['invocation']}) at {s['path']}")
        if errors:
            print("Errors:")
            for e in errors:
                print(f"  - {e['path']}: {e['error']}")


if __name__ == "__main__":
    main()
