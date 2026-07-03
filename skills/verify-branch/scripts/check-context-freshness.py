#!/usr/bin/env python3
"""Check whether a context report is fresh for the current branch/commit.

Accepts:
    --report      Path to the Markdown report to check (required).
    --branch      Current branch (optional; falls back to git).
    --commit      Current commit (optional; falls back to git).
    --cwd         Project root directory (optional).

Reads the report frontmatter to extract branch, commit, and generated_at.
A report is fresh when:
    - its branch matches the current branch, and
    - its commit matches the current commit, and
    - its generated_at timestamp is not older than the last commit on the current branch.

Outputs JSON to stdout:
    {
      "fresh": true|false,
      "reason": "...",
      "report_branch": "...",
      "current_branch": "...",
      "report_commit": "...",
      "current_commit": "...",
      "report_generated_at": "..."
    }

The script is read-only, deterministic, safe, and failure-explicit.
"""

import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


def _run_git(args: list[str], cwd: Path) -> str:
    """Run a git command and return stripped stdout, raising on failure."""
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def _current_git_branch(cwd: Path) -> str:
    return _run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd)


def _current_git_commit(cwd: Path) -> str:
    return _run_git(["rev-parse", "HEAD"], cwd)


def _last_commit_timestamp(cwd: Path) -> datetime.datetime | None:
    """Return the committer timestamp of the last commit on the current branch."""
    try:
        iso = _run_git(["log", "-1", "--format=%cI"], cwd)
    except RuntimeError:
        return None
    if not iso:
        return None
    try:
        return _parse_iso_timestamp(iso)
    except ValueError:
        return None


def _parse_iso_timestamp(value: str) -> datetime.datetime:
    """Parse an ISO 8601 timestamp, treating a trailing Z as UTC."""
    value = value.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.datetime.fromisoformat(value)


def _legacy_parse_frontmatter(text: str) -> dict:
    """Fallback parser for simple key: value frontmatter when PyYAML is absent."""
    data = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
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


def _parse_frontmatter(text: str) -> dict:
    """Parse a YAML frontmatter block into a dict."""
    if not text.startswith("---"):
        return {}

    end = text.find("---", 3)
    if end == -1:
        return {}

    fm_text = text[3:end].strip()
    if not fm_text:
        return {}

    if yaml is not None:
        try:
            data = yaml.safe_load(fm_text) or {}
        except yaml.YAMLError:
            data = {}
    else:
        data = _legacy_parse_frontmatter(fm_text)

    if not isinstance(data, dict):
        data = {}

    return {str(k).lower(): _coerce_frontmatter_value(v) for k, v in data.items()}


def _check_freshness(report_path: Path, current_branch: str, current_commit: str, cwd: Path) -> dict:
    """Compare a report to the current branch/commit and return a freshness result."""
    try:
        text = report_path.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        return {
            "fresh": False,
            "reason": f"Could not read report: {exc}",
            "report_branch": "",
            "current_branch": current_branch,
            "report_commit": "",
            "current_commit": current_commit,
            "report_generated_at": "",
        }

    frontmatter = _parse_frontmatter(text)

    report_branch = frontmatter.get("branch", "")
    report_commit = frontmatter.get("commit", "")
    report_generated_at = frontmatter.get("generated_at", "")

    result = {
        "fresh": True,
        "reason": "",
        "report_branch": report_branch,
        "current_branch": current_branch,
        "report_commit": report_commit,
        "current_commit": current_commit,
        "report_generated_at": report_generated_at,
    }

    if not report_branch or not report_commit or not report_generated_at:
        result["fresh"] = False
        result["reason"] = "Report is missing branch, commit, or generated_at."
        return result

    if report_branch != current_branch:
        result["fresh"] = False
        result["reason"] = (
            f"Branch mismatch: report is '{report_branch}', current is '{current_branch}'."
        )
        return result

    if report_commit != current_commit:
        result["fresh"] = False
        result["reason"] = (
            f"Commit mismatch: report is '{report_commit}', current is '{current_commit}'."
        )
        return result

    try:
        generated_dt = _parse_iso_timestamp(report_generated_at)
    except ValueError as exc:
        result["fresh"] = False
        result["reason"] = f"Could not parse generated_at '{report_generated_at}': {exc}."
        return result

    last_commit_dt = _last_commit_timestamp(cwd)
    if last_commit_dt is not None and generated_dt < last_commit_dt:
        result["fresh"] = False
        result["reason"] = (
            f"Report generated_at ({report_generated_at}) is older than the last commit on the branch."
        )
        return result

    result["reason"] = "Branch and commit match and the report is not older than the last commit."
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check whether a context report is fresh for the current branch/commit."
    )
    parser.add_argument("--report", required=True, help="Path to the Markdown report to check.")
    parser.add_argument("--branch", help="Current branch. Default: git rev-parse --abbrev-ref HEAD.")
    parser.add_argument("--commit", help="Current commit. Default: git rev-parse HEAD.")
    parser.add_argument("--cwd", help="Project root directory. Default: current working directory.")
    args = parser.parse_args()

    cwd = Path(args.cwd).resolve() if args.cwd else Path.cwd()
    report_path = Path(args.report).resolve()

    try:
        current_branch = args.branch if args.branch else _current_git_branch(cwd)
        current_commit = args.commit if args.commit else _current_git_commit(cwd)
    except Exception as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1

    try:
        result = _check_freshness(report_path, current_branch, current_commit, cwd)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:  # pragma: no cover - safety net
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
