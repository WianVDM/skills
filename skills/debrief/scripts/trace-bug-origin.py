#!/usr/bin/env python3
"""Trace a bug to its original feature commit.

Uses git log and git blame to identify the commit that introduced the lines
most likely related to the bug. This is a heuristic, not a definitive root
cause analysis.

Tries, in order:
    1. If files are provided, run `git blame` on the relevant lines and
       follow the commit back to the first non-fix commit.
    2. Search `git log` for commits mentioning the ticket key or related
       keywords to find the feature introduction.

Outputs JSON:
    {
      "origin_commit": "abc1234",
      "origin_message": "Add auth guard",
      "confidence": "high|medium|low",
      "reason": "..."
    }

If no origin can be determined, returns:
    {"origin_commit": "", "origin_message": "", "confidence": "low", "reason": "..."}

The script is read-only, deterministic, and safe to run in any project.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


FIX_KEYWORDS = [
    "fix",
    "bug",
    "patch",
    "hotfix",
    "regression",
    "repair",
    "correct",
    "issue",
]


def _run_git(args: list, cwd: Path, timeout: int = 10) -> str:
    """Run a git command and return stdout, or empty string on failure."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
        return result.stdout.strip()
    except (subprocess.SubprocessError, OSError, FileNotFoundError):
        return ""


def _is_fix_commit(message: str) -> bool:
    """Return True if the commit message looks like a fix or bug commit."""
    lower = message.lower()
    return any(kw in lower for kw in FIX_KEYWORDS)


def _find_origin_from_blame(file_path: str, line_number: int, cwd: Path) -> dict:
    """Trace the origin of a specific line via git blame."""
    blame = _run_git(
        ["blame", "-L", f"{line_number},{line_number}", "--porcelain", file_path],
        cwd,
    )
    if not blame:
        return {}

    # Extract commit hash from first line
    first_line = blame.splitlines()[0]
    match = re.match(r"^([a-f0-9]+)", first_line)
    if not match:
        return {}

    commit = match.group(1)

    # Walk back through commits on this file until we find a non-fix commit
    visited = set()
    while commit and commit not in visited:
        visited.add(commit)
        message = _run_git(["log", "-1", "--format=%s", commit], cwd)
        if not _is_fix_commit(message):
            return {
                "origin_commit": commit[:7],
                "origin_message": message,
                "confidence": "medium",
                "reason": "first non-fix commit found via git blame",
            }
        # Get parent commit
        parents = _run_git(["rev-list", "--parents", "-n", "1", commit], cwd)
        parts = parents.split()
        commit = parts[1] if len(parts) > 1 else None

    return {}


def _find_origin_from_log(ticket: str, keywords: list, cwd: Path) -> dict:
    """Search git log for the feature commit that likely introduced the bug."""
    search_terms = [ticket] + [kw for kw in (keywords or []) if kw]
    if not search_terms:
        return {}

    for term in search_terms:
        log = _run_git(
            ["log", "--oneline", "--all", "--grep", term, "--reverse"],
            cwd,
            timeout=15,
        )
        for line in log.splitlines():
            if not line.strip():
                continue
            parts = line.split(" ", 1)
            commit = parts[0]
            message = parts[1] if len(parts) > 1 else ""
            if not _is_fix_commit(message):
                return {
                    "origin_commit": commit[:7],
                    "origin_message": message,
                    "confidence": "low",
                    "reason": f"earliest matching commit for '{term}'",
                }

    return {}


def trace_bug_origin(
    ticket: str,
    file_path: str = None,
    line_number: int = None,
    keywords: list = None,
    cwd: Path = None,
) -> dict:
    """Return the best-effort origin commit for the bug."""
    if cwd is None:
        cwd = Path.cwd()

    if file_path and line_number:
        result = _find_origin_from_blame(file_path, line_number, cwd)
        if result:
            return result

    result = _find_origin_from_log(ticket, keywords, cwd)
    if result:
        return result

    return {
        "origin_commit": "",
        "origin_message": "",
        "confidence": "low",
        "reason": "could not trace bug origin from provided inputs",
    }


def main():
    parser = argparse.ArgumentParser(
        description="Trace a bug to its original feature commit."
    )
    parser.add_argument("--ticket", required=True, help="Ticket key.")
    parser.add_argument("--file", help="File path to blame.")
    parser.add_argument(
        "--line",
        type=int,
        help="Line number in the file to blame.",
    )
    parser.add_argument(
        "--keywords",
        help="Comma-separated keywords to search for in git log.",
    )
    parser.add_argument(
        "--cwd",
        help="Override the working directory. Default: current directory.",
    )
    args = parser.parse_args()

    keywords = [k.strip() for k in args.keywords.split(",")] if args.keywords else []
    cwd = Path(args.cwd).resolve() if args.cwd else Path.cwd()

    try:
        result = trace_bug_origin(
            ticket=args.ticket,
            file_path=args.file,
            line_number=args.line,
            keywords=keywords,
            cwd=cwd,
        )
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:  # pragma: no cover - safety net
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
