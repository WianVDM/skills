#!/usr/bin/env python3
"""
parse-skill-frontmatter.py

Extract the canonical frontmatter fields from a SKILL.md file.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

CANONICAL_FIELDS = ("name", "description", "version", "invocation", "depends")
HINT_FIELDS = ("allowed-tools", "disallowed-tools", "globs", "paths", "disable-model-invocation")


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
            result = {k: data.get(k) for k in CANONICAL_FIELDS}
            result.update({k: data.get(k) for k in HINT_FIELDS})
            # Normalize missing collections to None for consistency.
            if result.get("depends") is None:
                result["depends"] = None
            return result
    except Exception:
        pass

    # Minimal fallback parser for standard-library-only environments.
    result = {k: None for k in CANONICAL_FIELDS}
    result.update({k: None for k in HINT_FIELDS})

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
        elif key == "depends" or key in HINT_FIELDS:
            if key == "disable-model-invocation":
                result[key] = value.lower() in ("true", "yes", "1")
                i += 1
                continue

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
                result[key] = values
            elif value:
                result[key] = [value]
            else:
                result[key] = None
            continue
        i += 1

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Extract canonical frontmatter fields from a SKILL.md file."
    )
    parser.add_argument("skill_md", help="Path to SKILL.md.")
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    args = parser.parse_args()

    result = parse_frontmatter(Path(args.skill_md).expanduser().resolve())
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for key, value in result.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()
