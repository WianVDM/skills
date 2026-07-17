#!/usr/bin/env python3
"""
scan-context.py

Deterministic scanner for related context reports. Reads a JSON request from
stdin and writes a JSON response to stdout.

Input:
    {
        "context_dir": "/path/to/.agents/context",
        "ticket_key": "OC-4644",
        "project": "OC",
        "branch": "feature/OC-4644",
        "report_types": ["baseline", "handoff", "debrief"],
        "artifact_freshness_hours": 24,
        "top_n": 10
    }

Output:
    {
        "status": "complete",
        "reports": [
            {
                "path": "/path/to/.agents/context/baseline/OC-4644.md",
                "type": "baseline",
                "ticket_key": "OC-4644",
                "branch": "feature/OC-4644",
                "generated_at": "2026-07-08T10:00:00Z",
                "relevance": "High",
                "matched_by": "ticket_key",
                "fresh": true
            }
        ]
    }
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def _parse_scalar(value: str):
    """Parse a simple YAML scalar value (vendored from debrief/_frontmatter.py)."""
    value = value.strip()
    if not value or value in ("null", "Null", "NULL", "None", "none", "~"):
        return None
    low = value.lower()
    if low in ("true", "yes"):
        return True
    if low in ("false", "no"):
        return False
    if low in ("null", "none", "~"):
        return None
    if len(value) >= 2 and (
        (value.startswith('"') and value.endswith('"'))
        or (value.startswith("'") and value.endswith("'"))
    ):
        return value[1:-1]
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def _fallback_parse(fm_text: str) -> dict:
    """Parse a simple YAML-like frontmatter block (vendored from debrief/_frontmatter.py).

    Supports:
      - key: value
      - key:
          - item1
          - item2
      - key:
          nested_key: value
      - list-of-dicts under a key

    Does not support multi-line scalars, anchors, aliases, or complex types.
    """
    data = {}
    current_key = None
    current_list = None
    current_dict = None

    def _flush():
        if current_key is None:
            return
        if current_list:
            data[current_key] = current_list
        elif current_dict:
            data[current_key] = current_dict
        else:
            data[current_key] = None

    for raw_line in fm_text.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        indent = len(line) - len(stripped)

        if indent == 0 and ":" in stripped:
            _flush()
            key, sep, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()
            if not value:
                current_key = key
                current_list = []
                current_dict = {}
            else:
                data[key] = _parse_scalar(value)
                current_key = None
                current_list = None
                current_dict = None
            continue

        if current_key is not None and indent > 0:
            if stripped.startswith("- "):
                item = stripped[2:].strip()
                if ":" in item:
                    k, sep, v = item.partition(":")
                    k = k.strip()
                    v = v.strip()
                    current_list.append({k: _parse_scalar(v)})
                else:
                    current_list.append(_parse_scalar(item))
            elif ":" in stripped:
                k, sep, v = stripped.partition(":")
                k = k.strip()
                v = v.strip()
                current_dict[k] = _parse_scalar(v)
            continue

    _flush()
    return data


def _parse_frontmatter(path: Path) -> dict:
    """Extract YAML frontmatter from a markdown file.

    Uses PyYAML when available; otherwise falls back to a vendored parser that
    handles the scalar and nested fields used by baseline and debrief reports.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return {}

    end = text.find("\n---", 3)
    if end == -1:
        return {}

    block = text[3:end].strip()
    if not block:
        return {}

    try:
        import yaml

        data = yaml.safe_load(block)
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    return _fallback_parse(block)


def _report_ticket_key(frontmatter: dict) -> str | None:
    """Return the best available ticket key from frontmatter."""
    return (
        frontmatter.get("key")
        or frontmatter.get("ticket_key")
        or frontmatter.get("ticket")
    )


def _report_timestamp(frontmatter: dict) -> str | datetime | None:
    """Return the best available timestamp from frontmatter."""
    return (
        frontmatter.get("generated_at")
        or frontmatter.get("baselined_at")
        or frontmatter.get("updated_at")
    )


def _extract_project(ticket_key: str | None) -> str | None:
    """Return the project prefix from a ticket key, e.g. 'OC-4644' -> 'OC'."""
    if not ticket_key:
        return None
    match = re.match(r"^([A-Za-z]+)", ticket_key)
    return match.group(1).upper() if match else None


def _parse_iso_datetime(value: str | datetime | None) -> datetime | None:
    """Parse common ISO 8601 and related timestamp formats."""
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
    value = str(value).strip()
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        pass
    formats = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(value, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    return None


def _format_datetime(value: datetime | str | None) -> str | None:
    """Return an ISO 8601 string representation of a timestamp."""
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.strftime("%Y-%m-%dT%H:%M:%SZ")
    return str(value)


def _is_fresh(generated_at: datetime | None, threshold_hours: int) -> bool:
    """Return True if the report is within the freshness threshold."""
    if generated_at is None:
        return False
    now = datetime.now(timezone.utc)
    return (now - generated_at).total_seconds() <= threshold_hours * 3600


def _has_hidden_component(parts: tuple[str, ...]) -> bool:
    """Return True if any path component is hidden."""
    return any(part.startswith(".") for part in parts)


def _score_report(
    frontmatter: dict,
    ticket_key: str | None,
    project: str | None,
    branch: str | None,
) -> tuple[int, str, datetime | None]:
    """Return (relevance_score, matched_by, generated_at) for a report."""
    report_key = _report_ticket_key(frontmatter)
    report_branch = frontmatter.get("branch")
    report_project = _extract_project(report_key)

    timestamp = _parse_iso_datetime(_report_timestamp(frontmatter))

    if ticket_key and report_key and ticket_key.upper() == report_key.upper():
        return 3, "ticket_key", timestamp
    if branch and report_branch and branch.lower() == report_branch.lower():
        return 2, "branch", timestamp
    if project and report_project and project.upper() == report_project:
        return 1, "project", timestamp

    return 0, "recency", timestamp


def _report_type_for(context_dir: Path, file_path: Path) -> str:
    """Infer the report type from the first subdirectory under context_dir."""
    try:
        relative = file_path.parent.relative_to(context_dir)
        return relative.parts[0] if relative.parts else "unknown"
    except ValueError:
        return "unknown"


def scan_context(args: dict) -> dict:
    """Scan the context directory and return ranked matching reports."""
    context_dir = Path(args["context_dir"]).expanduser().resolve()
    if not context_dir.is_dir():
        return {"status": "empty", "reports": []}

    ticket_key = args.get("ticket_key")
    project = args.get("project") or _extract_project(ticket_key)
    branch = args.get("branch")
    report_types = args.get("report_types")
    threshold_hours = args.get("artifact_freshness_hours", 24)
    top_n = args.get("top_n", 10)

    if not isinstance(top_n, int) or top_n < 1:
        top_n = 10

    if report_types:
        directories = [context_dir / rt for rt in report_types]
    else:
        directories = [
            d for d in context_dir.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]

    reports = []
    for directory in directories:
        if not directory.is_dir():
            continue

        for file_path in directory.rglob("*.md"):
            if file_path.name.startswith("."):
                continue

            try:
                relative_parts = file_path.parent.relative_to(context_dir).parts
            except ValueError:
                continue

            if _has_hidden_component(relative_parts):
                continue

            frontmatter = _parse_frontmatter(file_path)
            report_type = relative_parts[0] if relative_parts else directory.name
            relevance_score, matched_by, generated_at = _score_report(
                frontmatter, ticket_key, project, branch
            )

            if relevance_score == 0:
                continue

            report_key = _report_ticket_key(frontmatter)
            timestamp = _report_timestamp(frontmatter)
            reports.append({
                "path": str(file_path),
                "type": report_type,
                "ticket_key": report_key,
                "branch": frontmatter.get("branch"),
                "generated_at": _format_datetime(timestamp),
                "relevance": {3: "High", 2: "Medium", 1: "Low"}.get(
                    relevance_score, "Low"
                ),
                "matched_by": matched_by,
                "fresh": _is_fresh(generated_at, threshold_hours),
                "scope": frontmatter.get("scope"),
                "method": frontmatter.get("method"),
                "parent": frontmatter.get("parent"),
            })

    def _sort_key(item: dict) -> tuple[int, float]:
        rel = {"High": 3, "Medium": 2, "Low": 1}.get(item["relevance"], 0)
        ts = _parse_iso_datetime(item.get("generated_at"))
        ts_value = ts.timestamp() if ts else 0.0
        return (rel, ts_value)

    reports.sort(key=_sort_key, reverse=True)

    return {
        "status": "complete" if reports else "empty",
        "reports": reports[:top_n],
    }


def _write_json(value: dict) -> None:
    json.dump(value, sys.stdout, indent=2)
    sys.stdout.write("\n")


def _error(message: str) -> dict:
    return {"status": "error", "errors": [message]}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Discover related context reports in a project's context directory.",
        prog="scan-context.py",
    )
    parser.parse_args()  # Only --help is supported; input comes from stdin.

    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        _write_json(_error(f"Invalid JSON input: {exc}"))
        return 2

    if not isinstance(input_data, dict):
        _write_json(_error("Input must be a JSON object."))
        return 2

    if "context_dir" not in input_data:
        _write_json(_error("Missing required field: context_dir."))
        return 2

    result = scan_context(input_data)
    _write_json(result)
    return 0 if result["status"] != "error" else 1


if __name__ == "__main__":
    sys.exit(main())
