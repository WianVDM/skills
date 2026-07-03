#!/usr/bin/env python3
"""Scan .agents/context/ for reports related to a ticket or issue key.

Accepts a ticket/issue key as a positional argument. Recursively scans
.agents/context/ for Markdown files whose name contains the key. Reads the
frontmatter of each match and extracts skill, version, ticket, key, and summary.

Excludes reports where the producing skill is "pr-report" to avoid circular
self-reference.

Outputs a JSON object:
    {
      "matches": [
        {
          "path": "...",
          "skill": "...",
          "summary": "...",
          "relevance": "high|medium|low"
        }
      ]
    }

Relevance is derived from filename and frontmatter matches:
    - high: filename equals the key or frontmatter ticket/key matches exactly.
    - medium: filename contains the key.
    - low: filename loosely matches after normalisation.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

CONTEXT_DIR = ".agents/context"


def _parse_frontmatter(text):
    """Parse a simple YAML-like frontmatter block into a dict."""
    if not text.startswith("---"):
        return {}

    end = text.find("---", 3)
    if end == -1:
        return {}

    fm = text[3:end].strip()
    data = {}
    for line in fm.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip().strip('"').strip("'")
        data[key] = value
    return data


def _normalise_key(key):
    """Normalise a key for comparison (uppercase, strip whitespace)."""
    return key.strip().upper()


def _calculate_relevance(path, frontmatter, key):
    """Calculate relevance based on filename and frontmatter matches."""
    stem = path.stem.upper()
    norm_key = _normalise_key(key)

    # Exact filename match
    if stem == norm_key:
        return "high"

    # Frontmatter exact match
    for field in ("ticket", "key", "issue"):
        if frontmatter.get(field, "").upper() == norm_key:
            return "high"

    # Filename contains key
    if norm_key in stem:
        return "medium"

    # Loose match: alphanumeric key appears anywhere in filename
    loose_key = re.sub(r"[^a-zA-Z0-9]", "", norm_key)
    if loose_key and loose_key in re.sub(r"[^a-zA-Z0-9]", "", stem):
        return "low"

    return "low"


def scan_related_context(key, context_dir=None):
    """Scan context directory and return matching reports."""
    if context_dir is None:
        context_dir = Path.cwd() / CONTEXT_DIR
    else:
        context_dir = Path(context_dir)

    if not context_dir.exists():
        return []

    norm_key = _normalise_key(key)
    matches = []

    for path in context_dir.rglob("*.md"):
        if norm_key not in path.stem.upper():
            # Quick skip: key not in filename
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        frontmatter = _parse_frontmatter(text)

        # Exclude pr-report's own outputs
        if frontmatter.get("skill", "").lower() == "pr-report":
            continue

        relevance = _calculate_relevance(path, frontmatter, key)

        matches.append(
            {
                "path": str(path.resolve()),
                "skill": frontmatter.get("skill", ""),
                "summary": frontmatter.get("summary", ""),
                "relevance": relevance,
            }
        )

    # Sort by relevance then path
    relevance_order = {"high": 0, "medium": 1, "low": 2}
    matches.sort(key=lambda m: (relevance_order.get(m["relevance"], 3), m["path"]))

    return matches


def main():
    parser = argparse.ArgumentParser(
        description="Scan .agents/context/ for reports related to a ticket key."
    )
    parser.add_argument("key", help="Ticket or issue key to search for.")
    parser.add_argument(
        "--context-dir",
        help="Override the context directory to scan. Default: .agents/context/",
    )
    args = parser.parse_args()

    if not args.key or not args.key.strip():
        print(json.dumps({"error": "key is required"}), file=sys.stderr)
        return 1

    matches = scan_related_context(args.key, context_dir=args.context_dir)
    print(json.dumps({"matches": matches}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
