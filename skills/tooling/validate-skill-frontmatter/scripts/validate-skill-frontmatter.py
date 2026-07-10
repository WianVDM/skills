#!/usr/bin/env python3
"""
validate-skill-frontmatter.py

Validate SKILL.md YAML frontmatter against the skill-frontmatter JSON schema.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def check_dependencies():
    try:
        import yaml  # noqa: F401
        import jsonschema  # noqa: F401
    except ImportError as e:
        print(
            f"ERROR: Missing dependency {e.name}. "
            "Install with: pip install pyyaml jsonschema",
            file=sys.stderr,
        )
        sys.exit(2)


def extract_frontmatter(skill_md: Path) -> tuple[dict, str, int]:
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return {}, text, 0
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text, 0
    block = text[3:end]
    return {"text": block, "start_line": 1}, text, end + 4


def parse_yaml(block: str) -> dict:
    import yaml
    try:
        return yaml.safe_load(block) or {}
    except yaml.YAMLError as e:
        return {"_yaml_error": str(e)}


def build_line_map(block: str) -> dict:
    """Build a rough mapping from top-level keys to line numbers in the frontmatter block."""
    line_map = {}
    for i, line in enumerate(block.splitlines(), start=1):
        stripped = line.lstrip()
        if stripped and not stripped.startswith("#") and ":" in stripped and not line[0].isspace():
            key = stripped.split(":", 1)[0].strip()
            line_map[key] = i
    return line_map


def validate(skill_md: Path, schema_path: Path) -> dict:
    import jsonschema

    fm_info, _, _ = extract_frontmatter(skill_md)
    if "_yaml_error" in fm_info:
        return {"valid": False, "errors": [{"message": fm_info["_yaml_error"], "path": "", "line": 1}]}

    block = fm_info.get("text", "")
    line_map = build_line_map(block)
    data = parse_yaml(block)

    if "_yaml_error" in data:
        return {"valid": False, "errors": [{"message": data["_yaml_error"], "path": "", "line": 1}]}

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    errors = []
    for err in validator.iter_errors(data):
        path = "/".join(str(p) for p in err.path) if err.path else "(root)"
        key = str(err.path[0]) if err.path else ""
        line = line_map.get(key, 1)
        errors.append({
            "message": err.message,
            "path": path,
            "line": line,
        })

    return {"valid": len(errors) == 0, "errors": errors}


def render_markdown(report: dict, skill_md: Path) -> str:
    lines = [f"# Frontmatter validation: {skill_md.name}", ""]
    if report["valid"]:
        lines.extend(["## Result: VALID", "", "No schema errors found."])
    else:
        lines.extend([
            "## Result: INVALID",
            "",
            f"**Errors:** {len(report['errors'])}",
            "",
            "| Line | Path | Message |",
            "|---|---|---|",
        ])
        for e in report["errors"]:
            lines.append(f"| {e['line']} | {e['path']} | {e['message']} |")
    return "\n".join(lines)


def _resolve_schema_path(provided: str) -> Path | None:
    """Resolve the schema path, falling back to the portable copy shipped with audit-skill."""
    path = Path(provided).expanduser().resolve()
    if path.is_file():
        return path
    script_dir = Path(__file__).resolve().parent
    fallback = (
        script_dir.parents[2]
        / "authoring"
        / "audit-skill"
        / "references"
        / "skill-frontmatter.schema.json"
    )
    if fallback.is_file():
        return fallback
    return None


def main():
    check_dependencies()

    parser = argparse.ArgumentParser(description="Validate SKILL.md frontmatter against the schema.")
    parser.add_argument("skill_md", help="Path to SKILL.md.")
    parser.add_argument(
        "--schema",
        default="docs/skill-standards/schemas/skill-frontmatter.schema.json",
        help="Path to the skill-frontmatter JSON schema. Falls back to the shipped copy if not found.",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    args = parser.parse_args()

    skill_md = Path(args.skill_md).expanduser().resolve()
    schema_path = _resolve_schema_path(args.schema)

    if not skill_md.is_file():
        print(f"ERROR: {skill_md} is not a file.", file=sys.stderr)
        sys.exit(1)
    if not schema_path:
        print(f"ERROR: Schema not found at {args.schema} or in the shipped fallback.", file=sys.stderr)
        sys.exit(1)

    report = validate(skill_md, schema_path)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(render_markdown(report, skill_md))

    sys.exit(0 if report["valid"] else 1)


if __name__ == "__main__":
    main()
