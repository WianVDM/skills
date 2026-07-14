#!/usr/bin/env python3
"""Scan the project for common standards document locations.

Checks well-known file paths and, for generic markdown files like AGENTS.md or
CONTRIBUTING.md, verifies that they reference standards before treating them as
a standards source. The script is read-only, deterministic, and safe to run in
any project.

Outputs JSON:
    {
      "sources": [
        {
          "path": "docs/coding-standards.md",
          "type": "markdown",
          "confidence": "high"
        }
      ]
    }

Usage:
    python detect-standards-docs.py
    python detect-standards-docs.py --cwd /path/to/project
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List


# Explicit high-confidence standards doc paths.
DIRECT_STANDARDS_CANDIDATES = [
    "docs/coding-standards.md",
    "docs/testing-standards.md",
    "docs/standards.md",
    "docs/development-standards.md",
    ".agents/config/standards.yaml",
    ".agents/config/standards.yml",
]

# Generic markdown files that may contain standards; require keyword match.
KEYWORD_STANDARDS_CANDIDATES = [
    "AGENTS.md",
    ".agents/AGENTS.md",
    "CONTRIBUTING.md",
]

# Keywords that indicate a file actually describes standards or conventions.
STANDARDS_KEYWORDS = [
    "coding standard",
    "testing standard",
    "development standard",
    "code standard",
    "style guide",
    "convention",
    "standards",
    "guidelines",
    "best practice",
]


def _read_text(path: Path) -> str:
    """Read text safely, returning an empty string on failure."""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _contains_standards_keyword(text: str) -> bool:
    """Return True if the text contains any standards-related keyword."""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in STANDARDS_KEYWORDS)


def _rel_path(path: Path, cwd: Path) -> str:
    """Return a POSIX-style path relative to the cwd."""
    return str(path.relative_to(cwd)).replace("\\", "/")


def _classify_path(path: Path, cwd: Path) -> Dict[str, str]:
    """Classify a candidate path into a standards source entry."""
    rel = _rel_path(path, cwd)
    ext = path.suffix.lower()
    if ext in (".yaml", ".yml"):
        return {"path": rel, "type": "yaml", "confidence": "high"}
    return {"path": rel, "type": "markdown", "confidence": "high"}


def detect_standards_docs(cwd: Path = None) -> Dict[str, List[Dict[str, str]]]:
    """Return all detected standards document sources for the given directory."""
    if cwd is None:
        cwd = Path.cwd()

    sources: List[Dict[str, str]] = []
    seen = set()

    for candidate in DIRECT_STANDARDS_CANDIDATES:
        path = cwd / candidate
        if path.exists() and str(path) not in seen:
            sources.append(_classify_path(path, cwd))
            seen.add(str(path))

    for candidate in KEYWORD_STANDARDS_CANDIDATES:
        path = cwd / candidate
        if not path.exists() or str(path) in seen:
            continue
        text = _read_text(path)
        if _contains_standards_keyword(text):
            sources.append({
                "path": _rel_path(path, cwd),
                "type": "markdown-frontmatter",
                "confidence": "medium",
            })
            seen.add(str(path))

    return {"sources": sources}


def main():
    parser = argparse.ArgumentParser(
        description="Scan the project for common standards document locations."
    )
    parser.add_argument(
        "--cwd",
        help="Override the working directory to inspect. Default: current directory.",
    )
    args = parser.parse_args()

    cwd = Path(args.cwd).resolve() if args.cwd else Path.cwd()
    try:
        result = detect_standards_docs(cwd)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:  # pragma: no cover - safety net
        print(json.dumps({"error": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
