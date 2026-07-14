#!/usr/bin/env python3
"""Scan the project context directory for reports related to a baseline scope.

Accepts --scope, --branch, and --ticket arguments. Recursively scans the
detected context directory for Markdown files whose filename or frontmatter
matches one of the provided terms. Reads the frontmatter of each match and
extracts skill, version, ticket, key, scope, branch, and summary.

By default the script uses `detect-project-context` to locate the context
directory. Override with --context-dir.

Excludes reports where the producing skill is "baseline" to avoid circular
self-reference, and also excludes files inside the baseline output directory
(`{context_dir}/baseline/`) by path.

Outputs JSON:
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

The script is read-only, deterministic, and safe to run in any project.
"""

from typing import Optional
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

RELEVANCE_ORDER = {"high": 0, "medium": 1, "low": 2}


def _detect_context_dir(start: Path) -> Path:
    """Use detect-project-context to find the recommended context directory.

    Raises RuntimeError if the context directory cannot be detected, so that
    the caller can fail closed rather than silently falling back to a
    hardcoded harness-specific path.
    """
    detect_script = Path(__file__).resolve().parents[2] / "detect-project-context" / "scripts" / "detect-project-context.py"
    if detect_script.is_file():
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(detect_script),
                    "--start",
                    str(start),
                    "--json",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if data.get("error"):
                    raise RuntimeError(
                        f"detect-project-context failed: {data['error']}"
                    )
                context_dir = data.get("recommended_context_dir")
                if context_dir:
                    return Path(context_dir)
        except subprocess.SubprocessError as exc:
            raise RuntimeError(
                f"detect-project-context subprocess failed: {exc}"
            ) from exc
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"detect-project-context returned invalid JSON: {exc}"
            ) from exc

    raise RuntimeError(
        "Could not detect the project context directory. "
        "Provide --context-dir explicitly."
    )


def _parse_frontmatter(text: str) -> dict:
    """Parse a YAML-like frontmatter block into a dict.

    Tries PyYAML if available; otherwise falls back to a simple line-based parser
    that handles single-line key: value pairs. Multiline values and complex
    structures may be skipped by the fallback. Install PyYAML for full accuracy.
    """
    if not text.startswith("---"):
        return {}

    end = text.find("---", 3)
    if end == -1:
        return {}

    fm = text[3:end].strip()
    if not fm:
        return {}

    try:
        import yaml  # type: ignore
        return yaml.safe_load(fm) or {}
    except Exception:
        pass

    data = {}
    for line in fm.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip().strip('"').strip("'")
        data[key] = value
    return data


def _normalise(term: str) -> str:
    """Normalise a search term for comparison."""
    return term.strip().upper()


def _calculate_relevance(path: Path, frontmatter: dict, terms: list) -> Optional[str]:
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

        # Exact frontmatter match
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

    baseline_output_dir = context_dir / "baseline"
    matches = []
    for path in sorted(context_dir.rglob("*.md")):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        frontmatter = _parse_frontmatter(text)

        # Exclude baseline's own outputs to avoid circular self-reference.
        # Exclude by frontmatter skill and by output directory path.
        if frontmatter.get("skill", "").lower() == "baseline":
            continue
        if baseline_output_dir in path.parents:
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
            }
        )

    matches.sort(key=lambda m: (RELEVANCE_ORDER.get(m["relevance"], 3), m["path"]))
    return matches


def main():
    parser = argparse.ArgumentParser(
        description="Scan the project context directory for reports related to a baseline scope."
    )
    parser.add_argument("--scope", help="Scope or feature name to search for.")
    parser.add_argument("--branch", help="Branch name to search for.")
    parser.add_argument("--ticket", help="Ticket key to search for.")
    parser.add_argument(
        "--context-dir",
        help="Override the context directory. Default: detected via detect-project-context.",
    )
    parser.add_argument(
        "--start",
        default=".",
        help="Directory to start from when detecting the context directory. Default: current directory.",
    )
    args = parser.parse_args()

    terms = [t for t in (args.scope, args.branch, args.ticket) if t]
    if not terms:
        print(
            json.dumps({"error": "at least one of --scope, --branch, or --ticket is required"}),
            file=sys.stderr,
        )
        return 1

    if args.context_dir:
        context_dir = Path(args.context_dir).resolve()
    else:
        try:
            context_dir = _detect_context_dir(Path(args.start).resolve())
        except RuntimeError as exc:
            print(
                json.dumps({"error": str(exc), "status": "blocked"}),
                file=sys.stderr,
            )
            return 1

    try:
        matches = scan_related_context(terms, context_dir)
        print(json.dumps({"matches": matches}, indent=2))
        return 0
    except Exception as exc:  # pragma: no cover - safety net
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
