#!/usr/bin/env python3
"""Check whether an existing debrief report is still fresh.

Reads the report's frontmatter to extract generated_at, branch, and commit.
Compares these values against:
    - The ticket's last updated time (--ticket-updated), if provided.
    - The current branch (--branch), if provided.
    - The current git HEAD commit, if the working directory is a git repository.

Outputs JSON:
    {
      "fresh": true|false,
      "reason": "...",
      "report_generated_at": "...",
      "current_commit": "..."
    }

The script is read-only, deterministic, and safe to run in any project.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def _parse_frontmatter(text: str) -> dict:
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


def _parse_iso_timestamp(value: str) -> datetime:
    """Parse an ISO 8601 timestamp, returning a timezone-aware datetime."""
    value = value.strip()
    # Replace trailing Z with +00:00 for fromisoformat compatibility.
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value)


def _short_commit(commit: str) -> str:
    """Return a normalised 7-character commit prefix, or the original value."""
    if not commit:
        return commit
    cleaned = re.sub(r"[^a-fA-F0-9]", "", commit)
    return cleaned[:7].lower() if cleaned else commit


def _get_git_head_commit(cwd: Path) -> str:
    """Return the short HEAD commit hash, or an empty string if not available."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        return result.stdout.strip()
    except (subprocess.SubprocessError, OSError, FileNotFoundError):
        return ""


def check_freshness(report_path: Path, ticket_updated: str = None, branch: str = None, cwd: Path = None) -> dict:
    """Return freshness status for the given report."""
    if not report_path.exists():
        return {"fresh": False, "reason": "report not found"}

    try:
        text = report_path.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        return {"fresh": False, "reason": f"failed to read report: {exc}"}

    frontmatter = _parse_frontmatter(text)
    generated_at = frontmatter.get("generated_at", "")
    report_branch = frontmatter.get("branch", "")
    report_commit = _short_commit(frontmatter.get("commit", ""))

    if cwd is None:
        cwd = report_path.parent

    current_commit = _get_git_head_commit(cwd)

    if ticket_updated:
        try:
            ticket_dt = _parse_iso_timestamp(ticket_updated)
            report_dt = _parse_iso_timestamp(generated_at) if generated_at else None
            if report_dt and ticket_dt > report_dt:
                return {
                    "fresh": False,
                    "reason": "ticket updated after debrief generated",
                    "report_generated_at": generated_at,
                    "current_commit": current_commit,
                }
        except ValueError:
            return {
                "fresh": False,
                "reason": f"invalid timestamp format: ticket_updated={ticket_updated}",
                "report_generated_at": generated_at,
                "current_commit": current_commit,
            }

    if branch and report_branch and branch != report_branch:
        return {
            "fresh": False,
            "reason": "current branch differs from report branch",
            "report_generated_at": generated_at,
            "current_commit": current_commit,
        }

    if current_commit and report_commit and current_commit != report_commit:
        return {
            "fresh": False,
            "reason": "current commit differs from report commit",
            "report_generated_at": generated_at,
            "current_commit": current_commit,
        }

    return {
        "fresh": True,
        "reason": "report is fresh",
        "report_generated_at": generated_at,
        "current_commit": current_commit,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Check whether an existing debrief report is still fresh."
    )
    parser.add_argument("--report", required=True, help="Path to the debrief report.")
    parser.add_argument(
        "--ticket-updated",
        help="ISO timestamp of the ticket's last update.",
    )
    parser.add_argument("--branch", help="Current branch name.")
    parser.add_argument(
        "--cwd",
        help="Override the working directory for git inspection. Default: report directory.",
    )
    args = parser.parse_args()

    report_path = Path(args.report).resolve()
    cwd = Path(args.cwd).resolve() if args.cwd else None

    try:
        result = check_freshness(
            report_path,
            ticket_updated=args.ticket_updated,
            branch=args.branch,
            cwd=cwd,
        )
        print(json.dumps(result, indent=2))
        return 0 if result.get("fresh") else 0
    except Exception as exc:  # pragma: no cover - safety net
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
