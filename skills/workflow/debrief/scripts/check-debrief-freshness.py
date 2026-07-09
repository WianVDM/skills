#!/usr/bin/env python3
"""Check whether an existing debrief report is still fresh.

Reads JSON from stdin:
  {
    "report_path": "/path/to/.agents/context/debrief/OC-4644-auth-guard.md",
    "ticket_updated_at": "2026-07-07T12:00:00Z",
    "branch": "feature/OC-4644-auth-guard",
    "commit": "abc1234def5678",
    "freshness_hours": 24
  }

Writes JSON to stdout:
  {"fresh": true|false, "reason": "..."}

Exit codes:
  0 — fresh
  1 — not fresh
  2 — error (invalid input, missing file, corrupt frontmatter)

The script is read-only, deterministic, and non-interactive.
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from _frontmatter import parse_frontmatter


def _help() -> str:
    return """check-debrief-freshness.py — check if a debrief report is still fresh

Input JSON (stdin):
  {"report_path": "...", "ticket_updated_at": "...", "branch": "...", "commit": "...", "freshness_hours": 24}

Output JSON (stdout):
  {"fresh": true|false, "reason": "..."}

Exit codes:
  0 = fresh
  1 = not fresh
  2 = error
"""


def _parse_timestamp(value: str):
    """Parse an ISO 8601 timestamp into a timezone-aware datetime."""
    if not value:
        return None
    value = str(value).strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def _short_commit(commit: str) -> str:
    """Return a normalised 7-character commit prefix, or the original value."""
    if not commit:
        return commit
    cleaned = re.sub(r"[^a-fA-F0-9]", "", commit)
    return cleaned[:7].lower() if cleaned else commit


def _run(data: dict) -> dict:
    report_path = data.get("report_path")
    ticket_updated_at = data.get("ticket_updated_at")
    branch = data.get("branch")
    commit = data.get("commit")
    freshness_hours = data.get("freshness_hours")

    if not report_path:
        raise ValueError("report_path is required")

    path = Path(report_path)
    if not path.exists():
        raise FileNotFoundError(f"report file not found: {report_path}")

    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        raise RuntimeError(f"failed to read report: {exc}")

    try:
        frontmatter = parse_frontmatter(text)
    except Exception as exc:
        raise ValueError(f"failed to parse report frontmatter: {exc}")

    if not isinstance(frontmatter, dict):
        raise ValueError("report frontmatter is not a mapping")

    report_updated_at = frontmatter.get("updated_at") or frontmatter.get("generated_at")
    report_branch = frontmatter.get("branch")
    report_commit = frontmatter.get("commit")

    # Ticket update comparison
    if ticket_updated_at:
        ticket_dt = _parse_timestamp(ticket_updated_at)
        report_dt = _parse_timestamp(report_updated_at)
        if ticket_dt is None or report_dt is None:
            raise ValueError("invalid timestamp format")
        if ticket_dt > report_dt:
            return {
                "fresh": False,
                "reason": "Ticket was updated after the report was generated.",
            }

    # Branch comparison
    if branch and report_branch and branch != report_branch:
        return {
            "fresh": False,
            "reason": "current branch differs from report branch",
        }

    # Commit comparison
    if commit and report_commit:
        if _short_commit(commit) != _short_commit(report_commit):
            return {
                "fresh": False,
                "reason": "current commit differs from report commit",
            }

    # Age comparison
    if freshness_hours is not None:
        report_dt = _parse_timestamp(report_updated_at)
        if report_dt is None:
            raise ValueError("report has no valid timestamp")
        now = datetime.now(timezone.utc)
        age_hours = (now - report_dt).total_seconds() / 3600
        if age_hours > freshness_hours:
            return {
                "fresh": False,
                "reason": f"report is older than {freshness_hours} hours",
            }

    return {
        "fresh": True,
        "reason": "report is fresh",
    }


if __name__ == "__main__":
    if any(arg in ("-h", "--help") for arg in sys.argv[1:]):
        print(_help())
        sys.exit(0)

    try:
        data = json.load(sys.stdin)
    except Exception as exc:
        print(
            json.dumps({"fresh": False, "reason": f"invalid JSON input: {exc}"}),
            file=sys.stderr,
        )
        sys.exit(2)

    try:
        result = _run(data)
    except FileNotFoundError as exc:
        result = {"fresh": False, "reason": str(exc)}
        print(json.dumps(result, indent=2))
        sys.exit(1)
    except Exception as exc:
        print(json.dumps({"fresh": False, "reason": str(exc)}), file=sys.stderr)
        sys.exit(2)

    print(json.dumps(result, indent=2))
    sys.exit(0 if result["fresh"] else 1)
