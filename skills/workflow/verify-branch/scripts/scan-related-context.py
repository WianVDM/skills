#!/usr/bin/env python3
"""Scan .agents/context/ for reports relevant to verify-branch.

Accepts --branch, --commit, optional --ticket, and optional --cwd.
Recursively scans .agents/context/ for Markdown files whose filename or
frontmatter matches the current branch or ticket. Reads the frontmatter and
extracts skill, version, ticket, key, scope, branch, generated_at, and summary.

Excludes reports where the producing skill is "verify-branch" to avoid
circular self-reference.

Outputs JSON to stdout:
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

Relevance scoring:
    - high: exact match in frontmatter branch/ticket/key/scope or filename.
    - medium: search term appears in the report summary.
    - low: search term appears in the filename (but not as an exact match and not in summary).

The script is read-only, deterministic, safe, and failure-explicit.
"""

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

CONTEXT_DIR = ".agents/context"
SELF_SKILL = "verify-branch"


def _legacy_parse_frontmatter(text: str) -> dict:
    """Fallback parser for simple key: value frontmatter when PyYAML is absent."""
    data = {}
    for raw in text.splitlines():
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        key = key.strip().lower()
        value = value.strip().strip('"').strip("'")
        data[key] = value
    return data


def _coerce_frontmatter_value(value):
    """Convert parsed YAML scalars to JSON-safe strings."""
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    if isinstance(value, datetime.date):
        return value.isoformat()
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse the first YAML frontmatter block and return the rest of the body."""
    if not text.startswith("---"):
        return {}, text

    end = text.find("---", 3)
    if end == -1:
        return {}, text

    fm_text = text[3:end].strip()
    body = text[end + 3 :].lstrip()
    if not fm_text:
        return {}, body

    if yaml is not None:
        try:
            data = yaml.safe_load(fm_text) or {}
        except yaml.YAMLError:
            data = {}
    else:
        data = _legacy_parse_frontmatter(fm_text)

    if not isinstance(data, dict):
        data = {}

    return {str(k).lower(): _coerce_frontmatter_value(v) for k, v in data.items()}, body


def _body_summary(body: str, max_chars: int = 400) -> str:
    """Return a short summary from the body text when frontmatter lacks one."""
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    if not lines:
        return ""
    summary = " ".join(lines)
    if len(summary) > max_chars:
        summary = summary[:max_chars].rsplit(" ", 1)[0] + "..."
    return summary


def _normalise(term: str) -> str:
    """Normalise a string for comparison."""
    return re.sub(r"[^A-Z0-9]", "", term.upper())


def _matches_exact(term: str, value: str) -> bool:
    if not term or not value:
        return False
    return term.upper() == value.upper() or _normalise(term) == _normalise(value)


def _matches_substring(term: str, value: str) -> bool:
    if not term or not value:
        return False
    return term.upper() in value.upper() or _normalise(term) in _normalise(value)


def _calculate_relevance(path: Path, frontmatter: dict, summary: str, terms: list[str]) -> str | None:
    """Return the highest relevance for a file against the given terms, or None."""
    stem = path.stem

    for term in terms:
        if not term:
            continue

        # High: exact match in frontmatter fields or exact filename match.
        if _matches_exact(term, stem):
            return "high"
        for field in ("branch", "ticket", "key", "scope"):
            if _matches_exact(term, frontmatter.get(field, "")):
                return "high"

        # Medium: term appears in the report summary.
        if _matches_substring(term, summary):
            return "medium"

        # Low: term appears in the filename (non-exact).
        if _matches_substring(term, stem):
            return "low"

    return None


def _scan(context_dir: Path, terms: list[str]) -> list[dict]:
    """Scan the context directory and return matching reports."""
    if not context_dir.exists():
        return []

    matches: list[dict] = []
    for path in sorted(context_dir.rglob("*.md")):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        frontmatter, body = _parse_frontmatter(text)

        # Exclude verify-branch's own outputs to avoid circular self-reference.
        if frontmatter.get("skill", "").lower() == SELF_SKILL:
            continue

        summary = frontmatter.get("summary", "")
        if not summary:
            summary = _body_summary(body)

        relevance = _calculate_relevance(path, frontmatter, summary, terms)
        if relevance is None:
            continue

        matches.append(
            {
                "path": str(path.resolve()),
                "skill": frontmatter.get("skill", ""),
                "summary": summary,
                "relevance": relevance,
                "generated_at": frontmatter.get("generated_at", ""),
            }
        )

    relevance_order = {"high": 0, "medium": 1, "low": 2}
    matches.sort(key=lambda m: (relevance_order.get(m["relevance"], 3), m["path"]))
    return matches


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scan .agents/context/ for reports relevant to verify-branch."
    )
    parser.add_argument("--branch", required=True, help="Current branch being verified.")
    parser.add_argument("--commit", help="Current HEAD commit (optional, for context only).")
    parser.add_argument("--ticket", help="Ticket key, if known.")
    parser.add_argument("--cwd", help="Project root directory. Default: current working directory.")
    parser.add_argument(
        "--context-dir",
        help="Override the context directory. Default: <cwd>/.agents/context/",
    )
    args = parser.parse_args()

    cwd = Path(args.cwd).resolve() if args.cwd else Path.cwd()
    context_dir = Path(args.context_dir).resolve() if args.context_dir else cwd / CONTEXT_DIR

    terms = [t for t in (args.branch, args.ticket) if t]

    try:
        matches = _scan(context_dir, terms)
        print(json.dumps({"matches": matches}, indent=2))
        return 0
    except Exception as exc:  # pragma: no cover - safety net
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
