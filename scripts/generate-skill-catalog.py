#!/usr/bin/env python3
"""
generate-skill-catalog.py

Generate docs/skill-catalog.md from skills.json and each skill's SKILL.md frontmatter.

Usage:
    python scripts/generate-skill-catalog.py

The script reads the skill bundle manifest (skills.json), parses each SKILL.md
frontmatter, and writes a grouped markdown catalog to docs/skill-catalog.md.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_JSON = REPO_ROOT / "skills.json"
OUTPUT = REPO_ROOT / "docs" / "skill-catalog.md"

CANONICAL_FIELDS = ("name", "description", "version", "invocation", "depends")


def parse_frontmatter(skill_md: Path) -> dict:
    """Extract canonical frontmatter fields from a SKILL.md file."""
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return {}

    end = text.find("\n---", 3)
    if end == -1:
        return {}

    block = text[3:end].strip()

    # Prefer PyYAML for full and correct parsing.
    try:
        import yaml

        data = yaml.safe_load(block) or {}
        if isinstance(data, dict):
            return {k: data.get(k) for k in CANONICAL_FIELDS}
    except Exception:
        pass

    # Minimal fallback parser for standard-library-only environments.
    result = {k: None for k in CANONICAL_FIELDS}
    lines = block.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            i += 1
            continue
        if line[0].isspace():
            i += 1
            continue
        key, _, value = stripped.partition(":")
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key in CANONICAL_FIELDS and key != "depends":
            result[key] = value
        elif key == "depends":
            values = []
            i += 1
            while i < len(lines):
                next_line = lines[i]
                next_stripped = next_line.strip()
                if not next_stripped or next_stripped.startswith("#"):
                    i += 1
                    continue
                if next_line[0].isspace() and next_stripped.startswith("- "):
                    values.append(next_stripped[2:].strip().strip('"').strip("'"))
                    i += 1
                else:
                    break
            if values:
                result["depends"] = values
            elif value:
                result["depends"] = [value]
            else:
                result["depends"] = None
            continue
        i += 1

    return result


def group_key(skill_path: str) -> tuple[str, str | None, str]:
    """Return (kind, domain, name) for sorting and grouping.

    Most paths look like skills/main/workflow/debrief.
    Setup paths look like skills/setup/setup-wian-skills, so there is no domain.
    """
    parts = Path(skill_path).parts
    kind = parts[1] if len(parts) > 1 else ""
    if kind == "setup":
        return kind, None, parts[2] if len(parts) > 2 else ""
    domain = parts[2] if len(parts) > 2 else ""
    name = parts[3] if len(parts) > 3 else ""
    return kind, domain, name


def format_invocation(frontmatter: dict, name: str) -> str:
    """Return a short invocation string for a skill."""
    invocation = frontmatter.get("invocation") or ""
    if invocation == "user-invoked":
        return f"/{name}"
    if invocation == "model-invoked":
        return "model-invoked"
    return invocation or "model-invoked"


def format_dependencies(deps: dict) -> str:
    """Return a markdown string of dependency categories."""
    required = deps.get("required", [])
    recommended = deps.get("recommended", [])
    optional = deps.get("optional", [])

    parts = []
    if required:
        parts.append(f"**Required:** {', '.join(required)}")
    if recommended:
        parts.append(f"**Recommended:** {', '.join(recommended)}")
    if optional:
        parts.append(f"**Optional:** {', '.join(optional)}")

    return "  \n".join(parts) if parts else "None."


def generate_catalog() -> str:
    """Generate the full markdown catalog."""
    manifest = json.loads(SKILLS_JSON.read_text(encoding="utf-8"))
    skill_paths = manifest["skills"]
    skill_dependencies = manifest.get("skill_dependencies", {})

    # Group by kind and domain.
    groups: dict[tuple[str, str | None], list[tuple[str, str, dict, dict]]] = {}
    for skill_path in skill_paths:
        kind, domain, name = group_key(skill_path)
        skill_dir = REPO_ROOT / skill_path
        skill_md = skill_dir / "SKILL.md"
        frontmatter = parse_frontmatter(skill_md) if skill_md.exists() else {}
        deps = skill_dependencies.get(name, {})
        groups.setdefault((kind, domain), []).append((name, skill_path, frontmatter, deps))

    # Sort each group alphabetically by skill name.
    for key in groups:
        groups[key].sort(key=lambda item: item[0])

    # Order kinds and domains for readability.
    kind_order = {"main": 0, "blocks": 1, "setup": 2}
    domain_order = {
        "main": ["workflow", "product", "engineering", "modes", "authoring"],
        "blocks": ["authoring", "project", "registry", "tokens"],
    }

    def sort_key(k):
        kind, domain = k
        kind_rank = kind_order.get(kind, 99)
        domains = domain_order.get(kind, [])
        domain_rank = domains.index(domain) if domain in domains else 99
        return (kind_rank, domain_rank)

    sorted_keys = sorted(groups.keys(), key=sort_key)

    lines = [
        "# Skill catalog",
        "",
        "This page lists every skill in the bundle. Skills are grouped into user-facing skills and building blocks.",
        "",
        "- **Main skills** are the ones you invoke directly.",
        "- **Block skills** are reused by other skills. You can invoke them on their own, but they are usually composed into conductors.",
        "",
        "For each skill, the entry shows the invocation, what it does, and its dependencies. For full behavior, read the linked `SKILL.md`.",
        "",
    ]

    current_kind = None
    for kind, domain in sorted_keys:
        if kind != current_kind:
            current_kind = kind
            kind_title = "Main skills" if kind == "main" else "Building blocks" if kind == "blocks" else "Setup"
            lines.append(f"## {kind_title}")
            lines.append("")

        if domain is not None:
            domain_title = domain.replace("-", " ").title()
            lines.append(f"### {domain_title}")
            lines.append("")

        for name, skill_path, frontmatter, deps in groups[(kind, domain)]:
            description = frontmatter.get("description") or ""
            invocation = format_invocation(frontmatter, name)
            rel_path = Path(os.path.relpath(REPO_ROOT / skill_path, OUTPUT.parent)).as_posix()

            lines.append(f"#### `{name}`")
            lines.append("")
            lines.append(f"{description}")
            lines.append("")
            lines.append(f"- **Invocation:** `{invocation}`")
            lines.append(f"- **Location:** `{rel_path}/`")
            dep_lines = format_dependencies(deps)
            if "\n" in dep_lines:
                lines.append("- **Dependencies:**")
                for dep_line in dep_lines.split("\n"):
                    lines.append(f"  - {dep_line.strip()}")
            else:
                lines.append(f"- **Dependencies:** {dep_lines}")
            lines.append(f"- **Details:** [{name}/SKILL.md]({rel_path}/SKILL.md)")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main():
    OUTPUT.write_text(generate_catalog(), encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
