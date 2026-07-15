#!/usr/bin/env python3
"""check-freshness.py

Check whether a context report or chainlog observation is fresh enough to reuse.

Supports two modes:
  --report <path>     Read a markdown report and check its frontmatter.
  --observation <json>  Check a provided chainlog observation directly.

Accepts JSON on stdin as an alternative to CLI flags. CLI flags override stdin.

Output JSON to stdout:
  {
    "fresh": true | false,
    "reason": "...",
    "dimensions": {
      "branch": { "fresh": true | false, ... },
      "commit": { "fresh": true | false, ... },
      "source_timestamp": { "fresh": true | false, ... },
      "generated_timestamp": { "fresh": true | false, ... },
      "schema_version": { "fresh": true | false, ... },
      "age": { "fresh": true | false, ... }
    }
  }

Exit codes:
  0 — fresh
  1 — stale or error
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


# Common frontmatter keys mapped to canonical artifact fields.
REPORT_KEY_ALIASES = {
    "artifact_branch": ["artifact_branch", "branch", "report_branch"],
    "artifact_commit": ["artifact_commit", "commit", "report_commit"],
    "artifact_generated_at": ["artifact_generated_at", "generated_at", "updated_at", "created_at", "collected_at"],
    "artifact_source_updated_at": ["artifact_source_updated_at", "source_updated_at", "ticket_updated_at"],
    "artifact_schema_version": ["artifact_schema_version", "schema_version", "schema"],
}

OBSERVATION_KEY_ALIASES = {
    "artifact_branch": ["branch", "artifact_branch"],
    "artifact_commit": ["commit", "artifact_commit"],
    "artifact_generated_at": ["collected_at", "generated_at", "updated_at", "created_at"],
    "artifact_source_updated_at": ["source_updated_at", "ticket_updated_at"],
    "artifact_schema_version": ["schema_version", "schema"],
}


def _help() -> str:
    return """check-freshness.py — check whether a context report or chainlog observation is fresh

CLI:
  check-freshness.py --report <path> [--branch <branch>] [--commit <commit>] [--cwd <cwd>] [--json]
  check-freshness.py --observation <json> [--branch <branch>] [--commit <commit>] [--cwd <cwd>] [--json]

Stdin JSON:
  {"mode": "report", "report_path": "...", "branch": "...", "commit": "...", "source_updated_at": "...", "freshness_hours": 24, "schema_version": "...", "cwd": "..."}
"""


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
    value = str(value).strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    dt = datetime.datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt


def _short_commit(commit: str) -> str:
    """Return a normalised 7-character commit prefix, or the original value."""
    if not commit:
        return commit
    cleaned = re.sub(r"[^a-fA-F0-9]", "", commit)
    return cleaned[:7].lower() if cleaned else commit


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


def _coerce_frontmatter_value(value: Any) -> Any:
    """Convert parsed YAML scalars to JSON-safe strings."""
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    if isinstance(value, datetime.date):
        return value.isoformat()
    if value is None:
        return ""
    return value


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
    try:
        data = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError:
        data = _legacy_parse_frontmatter(fm_text)
    if not isinstance(data, dict):
        data = {}
    return {str(k).lower(): _coerce_frontmatter_value(v) for k, v in data.items()}


def _extract_value(data: dict, aliases: list[str]) -> Any:
    """Return the first present value from a list of key aliases."""
    for key in aliases:
        if key in data:
            return data[key]
    return None


def _extract_artifact_metadata(mode: str, report_path: Path | None, observation: dict | None, report_frontmatter: dict | None = None) -> dict:
    """Extract canonical artifact fields from a report or chainlog observation entry."""
    aliases = REPORT_KEY_ALIASES if mode == "report" else OBSERVATION_KEY_ALIASES
    raw: dict = {}

    if mode == "report":
        if report_frontmatter is not None:
            raw = {str(k).lower(): _coerce_frontmatter_value(v) for k, v in report_frontmatter.items()}
        elif report_path is not None and report_path.exists():
            text = report_path.read_text(encoding="utf-8", errors="ignore")
            raw = _parse_frontmatter(text)
        elif report_path is not None:
            raise FileNotFoundError(f"report file not found: {report_path}")
        else:
            raise ValueError("report_path or report_frontmatter is required for report mode")
    elif mode == "observation":
        if not isinstance(observation, dict):
            raise ValueError("observation must be a dict")
        raw = {str(k).lower(): _coerce_frontmatter_value(v) for k, v in observation.items()}
    else:
        raise ValueError(f"unknown mode: {mode}")

    return {
        "artifact_branch": _extract_value(raw, aliases["artifact_branch"]),
        "artifact_commit": _extract_value(raw, aliases["artifact_commit"]),
        "artifact_generated_at": _extract_value(raw, aliases["artifact_generated_at"]),
        "artifact_source_updated_at": _extract_value(raw, aliases["artifact_source_updated_at"]),
        "artifact_schema_version": _extract_value(raw, aliases["artifact_schema_version"]),
    }


def _check_dimension(
    name: str,
    fresh: bool,
    reason: str,
    details: dict,
) -> dict:
    return {
        "fresh": fresh,
        "reason": reason,
        **details,
    }


def _check_freshness(data: dict) -> dict:
    mode = data.get("mode", "report")
    report_path = Path(data["report_path"]).resolve() if data.get("report_path") else None
    observation = data.get("observation")
    report_frontmatter = data.get("report_frontmatter")
    cwd = Path(data.get("cwd", ".")).resolve()

    provided_branch = data.get("branch")
    provided_commit = data.get("commit")
    source_updated_at = data.get("source_updated_at")
    freshness_hours = data.get("freshness_hours")
    schema_version = data.get("schema_version")

    try:
        artifact = _extract_artifact_metadata(mode, report_path, observation, report_frontmatter)
    except Exception as exc:
        return {
            "fresh": False,
            "reason": str(exc),
            "dimensions": {},
        }

    dimensions: dict[str, dict] = {}

    # Branch dimension
    if provided_branch or artifact["artifact_branch"]:
        current_branch = provided_branch
        if not current_branch and cwd:
            try:
                current_branch = _current_git_branch(cwd)
            except RuntimeError:
                pass
        artifact_branch = artifact["artifact_branch"]
        if current_branch and artifact_branch:
            fresh = current_branch == artifact_branch
            dimensions["branch"] = _check_dimension(
                "branch",
                fresh,
                "branch matches" if fresh else f"branch mismatch: artifact is '{artifact_branch}', current is '{current_branch}'",
                {"report_branch": artifact_branch, "current_branch": current_branch},
            )
        else:
            dimensions["branch"] = _check_dimension(
                "branch",
                False,
                "missing branch for comparison",
                {"report_branch": artifact_branch, "current_branch": current_branch},
            )

    # Commit dimension
    if provided_commit or artifact["artifact_commit"]:
        current_commit = provided_commit
        if not current_commit and cwd:
            try:
                current_commit = _current_git_commit(cwd)
            except RuntimeError:
                pass
        artifact_commit = artifact["artifact_commit"]
        if current_commit and artifact_commit:
            fresh = _short_commit(current_commit) == _short_commit(artifact_commit)
            dimensions["commit"] = _check_dimension(
                "commit",
                fresh,
                "commit matches" if fresh else f"commit mismatch: artifact is '{artifact_commit}', current is '{current_commit}'",
                {"report_commit": artifact_commit, "current_commit": current_commit},
            )
        else:
            dimensions["commit"] = _check_dimension(
                "commit",
                False,
                "missing commit for comparison",
                {"report_commit": artifact_commit, "current_commit": current_commit},
            )

    # Source timestamp dimension
    if source_updated_at or artifact["artifact_source_updated_at"]:
        source_dt = None
        artifact_source_dt = None
        try:
            source_dt = _parse_iso_timestamp(source_updated_at) if source_updated_at else None
        except ValueError:
            pass
        try:
            artifact_source_dt = _parse_iso_timestamp(artifact["artifact_source_updated_at"]) if artifact["artifact_source_updated_at"] else None
        except ValueError:
            pass

        if source_dt and artifact_source_dt:
            fresh = artifact_source_dt >= source_dt
            dimensions["source_timestamp"] = _check_dimension(
                "source_timestamp",
                fresh,
                "source not updated since artifact" if fresh else "source was updated after artifact was generated",
                {
                    "source_updated_at": source_updated_at,
                    "artifact_source_updated_at": artifact["artifact_source_updated_at"],
                },
            )
        else:
            dimensions["source_timestamp"] = _check_dimension(
                "source_timestamp",
                False,
                "missing source timestamps for comparison",
                {
                    "source_updated_at": source_updated_at,
                    "artifact_source_updated_at": artifact["artifact_source_updated_at"],
                },
            )

    # Generated timestamp / age dimension
    if artifact["artifact_generated_at"]:
        try:
            generated_dt = _parse_iso_timestamp(artifact["artifact_generated_at"])
        except ValueError:
            generated_dt = None

        if generated_dt is not None:
            # Check against last commit timestamp if available.
            last_commit_dt = _last_commit_timestamp(cwd)
            if last_commit_dt is not None and generated_dt < last_commit_dt:
                dimensions["generated_timestamp"] = _check_dimension(
                    "generated_timestamp",
                    False,
                    "artifact is older than the last commit on the current branch",
                    {
                        "artifact_generated_at": artifact["artifact_generated_at"],
                        "last_commit_at": last_commit_dt.isoformat(),
                    },
                )
            else:
                dimensions["generated_timestamp"] = _check_dimension(
                    "generated_timestamp",
                    True,
                    "artifact is not older than the last commit on the current branch",
                    {
                        "artifact_generated_at": artifact["artifact_generated_at"],
                        "last_commit_at": last_commit_dt.isoformat() if last_commit_dt else None,
                    },
                )

            # Check age threshold if provided.
            if freshness_hours is not None:
                now = datetime.datetime.now(datetime.timezone.utc)
                age_hours = (now - generated_dt).total_seconds() / 3600
                fresh = age_hours <= freshness_hours
                dimensions["age"] = _check_dimension(
                    "age",
                    fresh,
                    f"artifact is within {freshness_hours} hours" if fresh else f"artifact is older than {freshness_hours} hours",
                    {
                        "artifact_generated_at": artifact["artifact_generated_at"],
                        "age_hours": age_hours,
                        "threshold_hours": freshness_hours,
                    },
                )
        else:
            dimensions["generated_timestamp"] = _check_dimension(
                "generated_timestamp",
                False,
                f"could not parse artifact generated_at '{artifact['artifact_generated_at']}'",
                {"artifact_generated_at": artifact["artifact_generated_at"]},
            )
    else:
        dimensions["generated_timestamp"] = _check_dimension(
            "generated_timestamp",
            False,
            "missing artifact generated_at",
            {"artifact_generated_at": None},
        )

    # Schema version dimension
    if schema_version or artifact["artifact_schema_version"]:
        if schema_version and artifact["artifact_schema_version"]:
            fresh = str(schema_version) == str(artifact["artifact_schema_version"])
            dimensions["schema_version"] = _check_dimension(
                "schema_version",
                fresh,
                "schema version matches" if fresh else "schema version mismatch",
                {
                    "expected_schema_version": schema_version,
                    "artifact_schema_version": artifact["artifact_schema_version"],
                },
            )
        else:
            dimensions["schema_version"] = _check_dimension(
                "schema_version",
                False,
                "missing schema version for comparison",
                {
                    "expected_schema_version": schema_version,
                    "artifact_schema_version": artifact["artifact_schema_version"],
                },
            )

    overall_fresh = all(d.get("fresh", False) for d in dimensions.values())

    if overall_fresh:
        reason = "all checked dimensions are fresh"
    else:
        stale = [name for name, d in dimensions.items() if not d.get("fresh", False)]
        reason = f"stale dimensions: {', '.join(stale)}"

    return {
        "fresh": overall_fresh,
        "reason": reason,
        "dimensions": dimensions,
    }


def _main() -> int:
    parser = argparse.ArgumentParser(
        description="Check whether a context report or chainlog observation is fresh.",
    )
    parser.add_argument("--report", help="Path to the markdown report to check.")
    parser.add_argument("--observation", help="JSON string with a chainlog observation entry.")
    parser.add_argument("--branch", help="Current branch.")
    parser.add_argument("--commit", help="Current commit.")
    parser.add_argument("--source-updated-at", help="Timestamp when the source was last updated.")
    parser.add_argument("--freshness-hours", type=int, help="Maximum age in hours.")
    parser.add_argument("--schema-version", help="Expected schema version.")
    parser.add_argument("--cwd", help="Project root directory. Default: current working directory.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable output.")
    args = parser.parse_args()

    stdin_data: dict = {}
    if not sys.stdin.isatty():
        try:
            stdin_data = json.load(sys.stdin)
        except json.JSONDecodeError:
            pass

    data = dict(stdin_data)
    if args.report:
        data["mode"] = "report"
        data["report_path"] = args.report
    elif args.observation:
        data["mode"] = "observation"
        try:
            data["observation"] = json.loads(args.observation)
        except json.JSONDecodeError as exc:
            print(json.dumps({"fresh": False, "reason": f"invalid --observation JSON: {exc}", "dimensions": {}}), file=sys.stderr)
            return 1
    if args.branch:
        data["branch"] = args.branch
    if args.commit:
        data["commit"] = args.commit
    if args.source_updated_at:
        data["source_updated_at"] = args.source_updated_at
    if args.freshness_hours is not None:
        data["freshness_hours"] = args.freshness_hours
    if args.schema_version:
        data["schema_version"] = args.schema_version
    if args.cwd:
        data["cwd"] = args.cwd

    if not data.get("mode"):
        print(json.dumps({"fresh": False, "reason": "either --report or --observation is required", "dimensions": {}}), file=sys.stderr)
        return 1

    try:
        result = _check_freshness(data)
    except Exception as exc:
        print(json.dumps({"fresh": False, "reason": str(exc), "dimensions": {}}), file=sys.stderr)
        return 1

    if args.json or not sys.stdout.isatty():
        print(json.dumps(result, indent=2))
    else:
        print(f"Fresh: {result['fresh']}")
        print(f"Reason: {result['reason']}")
        for name, dim in result["dimensions"].items():
            print(f"  {name}: {dim['fresh']} — {dim['reason']}")
    return 0 if result["fresh"] else 1


if __name__ == "__main__":
    sys.exit(_main())
