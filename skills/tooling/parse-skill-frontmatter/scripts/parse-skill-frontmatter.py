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


def _extract_metadata_value(data: dict, key: str):
    """Return a single value from metadata, or None/empty default."""
    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        return None
    return metadata.get(key)


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
            # Normalize missing collections to None for consistency.
            if result.get("depends") is None:
                result["depends"] = None
            tags = _extract_metadata_value(data, "tags") or []
            result["tags"] = tags if isinstance(tags, list) else []
            result["author"] = _extract_metadata_value(data, "author")
            return result
    except Exception:
        pass

    # Minimal fallback parser for standard-library-only environments.
    result = {k: None for k in CANONICAL_FIELDS}
    result["tags"] = []
    result["author"] = None
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        if line[0].isspace():
            continue
        key, _, value = stripped.partition(":")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key in CANONICAL_FIELDS:
            result[key] = value

    # Parse tags from metadata block
    tags = []
    in_metadata = False
    for line in block.splitlines():
        stripped = line.strip()
        if stripped == "metadata:":
            in_metadata = True
            continue
        if in_metadata:
            if stripped.startswith("tags:"):
                raw = stripped.split(":", 1)[1].strip()
                if raw.startswith("[") and raw.endswith("]"):
                    tags = [t.strip().strip('"').strip("'") for t in raw[1:-1].split(",")]
                    tags = [t for t in tags if t]
                break
            # author is a leaf scalar under metadata
            if stripped.startswith("author:"):
                result["author"] = stripped.split(":", 1)[1].strip().strip('"').strip("'")
            if stripped.endswith(":") and not line.startswith(" "):
                in_metadata = False

    result["tags"] = tags
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
