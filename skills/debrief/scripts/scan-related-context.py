#!/usr/bin/env python3
"""Scan the project context directory for reports related to a ticket or branch.

Accepts --ticket and optional --branch. Recursively scans the given context
directory for Markdown files whose filename or frontmatter matches the ticket
key or branch. Reads the frontmatter of each match and extracts skill, version,
ticket/scope/branch, summary, and generated_at.

Excludes reports where the producing skill is "debrief" to avoid self-reference.

Outputs JSON:
    {
      "matches": [
        {
          "path": "...",
          "skill": "...",
          "summary": "...",
          "relevance": "high|medium|low",
          "generated_at": "..."
        }
      ]
    }

The script is read-only, deterministic, and safe to run in any project.
"""

import argparse
import json
import re
import sys
from pathlib import Path

from _frontmatter import parse_frontmatter

CONTEXT_DIR = "context"
RELEVANCE_ORDER = {"high": 0, "medium": 1, "low": 2}

def _normalise(term: str) -> str:
    """Normalise a search term for comparison."""
    return term.strip().upper()


def _calculate_relevance(path: Path, frontmatter: dict, terms: list) -> str | None:
    """Calculate the highest relevance for a file against the given terms."""
    stem = path.stem.upper()

    for term in terms:
        if not term:
            continue
        norm = _normalise(term)
        if not norm:
            continue

        # Exact filename match
        if stem == norm:
            return "high"

        # Exact frontmatter match on common fields
        for field in ("ticket", "key", "scope", "branch"):
            if frontmatter.get(field, "").upper() == norm:
                return "high"

        # Filename contains term
        if norm in stem:
            return "medium"

        # Loose alphanumeric match
        loose_term = re.sub(r"[^A-Z0-9]", "", norm)
        loose_stem = re.sub(r"[^A-Z0-9]", "", stem)
        if loose_term and loose_term in loose_stem:
            return "low"

    return None


def scan_related_context(terms: list, context_dir: Path):
    """Scan the context directory and return matching reports."""
    if not context_dir.exists():
        return []

    matches = []
    for path in sorted(context_dir.rglob("*.md")):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        frontmatter = parse_frontmatter(text)

        # Exclude debrief's own outputs to avoid self-reference
        if frontmatter.get("skill", "").lower() == "debrief":
            continue

        relevance = _calculate_relevance(path, frontmatter, terms)
        if relevance is None:
            continue

        matches.append(
            {
                "path": str(path.resolve()),
                "skill": frontmatter.get("skill", ""),
                "summary": frontmatter.get("summary", ""),
                "relevance": relevance,
                "generated_at": frontmatter.get("generated_at", ""),
            }
        )

    matches.sort(key=lambda m: (RELEVANCE_ORDER.get(m["relevance"], 3), m["path"]))
    return matches


def main():
    parser = argparse.ArgumentParser(
        description="Scan the project context directory for reports related to a ticket or branch."
    )
    parser.add_argument("--ticket", help="Ticket key to search for.")
    parser.add_argument("--branch", help="Branch name to search for.")
    parser.add_argument(
        "--context-dir",
        help="Override the context directory. Default: {cwd}/context/",
    )
    args = parser.parse_args()

    terms = [t for t in (args.ticket, args.branch) if t]
    if not terms:
        print(
            json.dumps({"error": "at least one of --ticket or --branch is required"}),
            file=sys.stderr,
        )
        return 1

    context_dir = Path(args.context_dir).resolve() if args.context_dir else Path.cwd() / CONTEXT_DIR

    try:
        matches = scan_related_context(terms, context_dir)
        print(json.dumps({"matches": matches}, indent=2))
        return 0
    except Exception as exc:  # pragma: no cover - safety net
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
