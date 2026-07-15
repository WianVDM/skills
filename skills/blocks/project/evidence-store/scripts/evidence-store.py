#!/usr/bin/env python3
"""evidence-store.py

Append-only storage for evidence collected by tools.

Operations:
  append        Add a new evidence entry to a work-item timeline.
  query_latest  Return the latest entry per capability (or for one capability).
  query_all     Return all entries for a work item, optionally filtered by capability.
  query_since   Return entries collected after a given timestamp.
  exists        Check whether a work item has any evidence.
  mark_stale    Record that a capability is stale.

Input JSON on stdin:
  {"operation": "append", "context_dir": "...", "entry": {...}}
  {"operation": "query_latest", "context_dir": "...", "work_item_type": "pr", "work_item_key": "42@owner-repo", "capability": "pr-source"}

Output JSON to stdout.
"""

from __future__ import annotations

import datetime
import json
import re
import sys
import uuid
from pathlib import Path
from typing import Any

import yaml


# Required frontmatter fields for an evidence entry.
REQUIRED_ENTRY_FIELDS = [
    "work_item_type",
    "work_item_key",
    "capability",
    "source",
]


def _help() -> str:
    return """evidence-store.py — append-only storage for tool evidence

Input JSON (stdin):
  {"operation": "append", "context_dir": "...", "entry": {...}}
  {"operation": "query_latest", "context_dir": "...", "work_item_type": "...", "work_item_key": "...", "capability": "..."}
  {"operation": "query_all", "context_dir": "...", "work_item_type": "...", "work_item_key": "...", "capability": "..."}
  {"operation": "query_since", "context_dir": "...", "work_item_type": "...", "work_item_key": "...", "capability": "...", "since": "2026-07-14T10:00:00Z"}
  {"operation": "exists", "context_dir": "...", "work_item_type": "...", "work_item_key": "..."}
  {"operation": "mark_stale", "context_dir": "...", "work_item_type": "...", "work_item_key": "...", "capability": "...", "reason": "..."}
"""


def _parse_iso_timestamp(value: str) -> datetime.datetime:
    """Parse an ISO 8601 timestamp, treating a trailing Z as UTC."""
    value = str(value).strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    dt = datetime.datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt


def _format_timestamp(value: datetime.datetime) -> str:
    """Format a datetime as ISO 8601 UTC."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=datetime.timezone.utc)
    return value.astimezone(datetime.timezone.utc).isoformat().replace("+00:00", "Z")


def _slugify(value: str) -> str:
    """Make a work-item key safe for use as a filename."""
    # Replace filesystem-prohibited characters with underscores.
    return re.sub(r'[\\/:*?"<>|]', "_", value)


def _timeline_path(context_dir: Path, work_item_type: str, work_item_key: str) -> Path:
    """Return the timeline file path for a work item."""
    return context_dir / "evidence" / work_item_type / f"{_slugify(work_item_key)}.timeline.md"


def _coerce_value(value: Any) -> Any:
    """Convert parsed YAML values to JSON-safe types."""
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    if isinstance(value, datetime.date):
        return value.isoformat()
    if value is None:
        return None
    return value


def _parse_frontmatter(text: str) -> dict:
    """Parse a YAML frontmatter block into a dict."""
    if not text.strip():
        return {}
    try:
        data = yaml.safe_load(text) or {}
    except yaml.YAMLError:
        return {}
    if not isinstance(data, dict):
        return {}
    return {str(k): _coerce_value(v) for k, v in data.items()}


def _parse_timeline(text: str) -> list[dict]:
    """Parse a timeline file into a list of entries with frontmatter and body."""
    if not text.strip():
        return []

    # Split by --- lines. The file alternates frontmatter and body.
    parts = re.split(r"\n---\s*\n", text.strip())
    # If the file starts with ---, the first split part may be empty.
    if parts and not parts[0].strip():
        parts = parts[1:]

    entries = []
    for i in range(0, len(parts), 2):
        frontmatter_text = parts[i]
        body = parts[i + 1] if i + 1 < len(parts) else ""
        frontmatter = _parse_frontmatter(frontmatter_text)
        if frontmatter:
            entries.append({
                "frontmatter": frontmatter,
                "body": body.strip("\n"),
            })
    return entries


def _render_entry(entry: dict) -> str:
    """Render an evidence entry as markdown text."""
    frontmatter = dict(entry.get("frontmatter", {}))
    body = entry.get("body", "")
    fm_text = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False, allow_unicode=True)
    return f"---\n{fm_text}---\n\n{body}\n"


def _validate_entry(entry: dict) -> list[str]:
    """Validate required evidence entry fields."""
    errors = []
    for field in REQUIRED_ENTRY_FIELDS:
        if field not in entry or entry[field] is None or entry[field] == "":
            errors.append(f"missing required field: {field}")
    return errors


def _entry_to_output(entry: dict) -> dict:
    """Convert an internal entry to the output format."""
    return {
        "frontmatter": entry["frontmatter"],
        "body": entry["body"],
    }


def _do_append(context_dir: Path, entry: dict) -> dict:
    """Append an evidence entry to the work-item timeline."""
    errors = _validate_entry(entry)
    if errors:
        return {"status": "error", "errors": errors}

    work_item_type = entry["work_item_type"]
    work_item_key = entry["work_item_key"]
    timeline_path = _timeline_path(context_dir, work_item_type, work_item_key)
    timeline_path.parent.mkdir(parents=True, exist_ok=True)

    # Ensure evidence_id and collected_at are present.
    if "evidence_id" not in entry or not entry["evidence_id"]:
        entry["evidence_id"] = str(uuid.uuid4())
    if "collected_at" not in entry or not entry["collected_at"]:
        entry["collected_at"] = _format_timestamp(datetime.datetime.now(datetime.timezone.utc))

    rendered = _render_entry({"frontmatter": entry, "body": entry.get("payload", "")})

    # Append to file.
    with timeline_path.open("a", encoding="utf-8") as f:
        f.write(rendered)

    return {
        "status": "appended",
        "evidence_id": entry["evidence_id"],
        "path": str(timeline_path),
    }


def _do_query(
    context_dir: Path,
    work_item_type: str,
    work_item_key: str,
    capability: str | None,
    since: str | None,
) -> dict:
    """Query evidence entries for a work item."""
    timeline_path = _timeline_path(context_dir, work_item_type, work_item_key)
    if not timeline_path.exists():
        return {
            "status": "not_found",
            "entries": [],
            "count": 0,
        }

    text = timeline_path.read_text(encoding="utf-8", errors="ignore")
    entries = _parse_timeline(text)

    if capability:
        entries = [e for e in entries if e["frontmatter"].get("capability") == capability]

    if since:
        try:
            since_dt = _parse_iso_timestamp(since)
        except ValueError as exc:
            return {"status": "error", "errors": [f"invalid since timestamp: {exc}"]}
        filtered = []
        for e in entries:
            collected_at = e["frontmatter"].get("collected_at")
            if collected_at:
                try:
                    collected_dt = _parse_iso_timestamp(collected_at)
                    if collected_dt >= since_dt:
                        filtered.append(e)
                except ValueError:
                    pass
        entries = filtered

    return {
        "status": "found",
        "entries": [_entry_to_output(e) for e in entries],
        "count": len(entries),
    }


def _do_query_latest(
    context_dir: Path,
    work_item_type: str,
    work_item_key: str,
    capability: str | None,
) -> dict:
    """Return the latest evidence entry per capability for a work item."""
    result = _do_query(context_dir, work_item_type, work_item_key, None, None)
    if result["status"] != "found":
        return result

    entries = result["entries"]
    latest_by_capability: dict[str, dict] = {}
    for e in entries:
        cap = e["frontmatter"].get("capability")
        if not cap:
            continue
        collected_at = e["frontmatter"].get("collected_at")
        if not collected_at:
            continue
        if cap not in latest_by_capability:
            latest_by_capability[cap] = e
            continue
        try:
            current_dt = _parse_iso_timestamp(latest_by_capability[cap]["frontmatter"]["collected_at"])
            new_dt = _parse_iso_timestamp(collected_at)
            if new_dt > current_dt:
                latest_by_capability[cap] = e
        except ValueError:
            pass

    if capability:
        if capability in latest_by_capability:
            return {
                "status": "found",
                "entries": [latest_by_capability[capability]],
                "count": 1,
            }
        return {
            "status": "not_found",
            "entries": [],
            "count": 0,
        }

    return {
        "status": "found",
        "entries": list(latest_by_capability.values()),
        "count": len(latest_by_capability),
    }


def _do_exists(context_dir: Path, work_item_type: str, work_item_key: str) -> dict:
    """Check whether a work item has any evidence."""
    timeline_path = _timeline_path(context_dir, work_item_type, work_item_key)
    if not timeline_path.exists():
        return {"status": "found", "exists": False, "path": str(timeline_path)}

    text = timeline_path.read_text(encoding="utf-8", errors="ignore")
    entries = _parse_timeline(text)
    return {
        "status": "found",
        "exists": len(entries) > 0,
        "path": str(timeline_path),
        "count": len(entries),
    }


def _do_mark_stale(
    context_dir: Path,
    work_item_type: str,
    work_item_key: str,
    capability: str,
    reason: str,
) -> dict:
    """Record a staleness marker for a capability."""
    entry = {
        "evidence_id": str(uuid.uuid4()),
        "work_item_type": work_item_type,
        "work_item_key": work_item_key,
        "capability": capability,
        "source": "stale-marker",
        "collected_at": _format_timestamp(datetime.datetime.now(datetime.timezone.utc)),
        "stale": True,
        "reason": reason,
    }
    return _do_append(context_dir, entry)


def _run(data: dict) -> dict:
    operation = data.get("operation")
    context_dir = Path(data.get("context_dir", ".agents/context")).resolve()

    if operation == "append":
        entry = data.get("entry")
        if not isinstance(entry, dict):
            return {"status": "error", "errors": ["entry is required for append"]}
        return _do_append(context_dir, entry)

    if operation == "query_latest":
        work_item_type = data.get("work_item_type")
        work_item_key = data.get("work_item_key")
        capability = data.get("capability")
        if not work_item_type or not work_item_key:
            return {"status": "error", "errors": ["work_item_type and work_item_key are required"]}
        return _do_query_latest(context_dir, work_item_type, work_item_key, capability)

    if operation == "query_all":
        work_item_type = data.get("work_item_type")
        work_item_key = data.get("work_item_key")
        capability = data.get("capability")
        if not work_item_type or not work_item_key:
            return {"status": "error", "errors": ["work_item_type and work_item_key are required"]}
        return _do_query(context_dir, work_item_type, work_item_key, capability, None)

    if operation == "query_since":
        work_item_type = data.get("work_item_type")
        work_item_key = data.get("work_item_key")
        capability = data.get("capability")
        since = data.get("since")
        if not work_item_type or not work_item_key:
            return {"status": "error", "errors": ["work_item_type and work_item_key are required"]}
        return _do_query(context_dir, work_item_type, work_item_key, capability, since)

    if operation == "exists":
        work_item_type = data.get("work_item_type")
        work_item_key = data.get("work_item_key")
        if not work_item_type or not work_item_key:
            return {"status": "error", "errors": ["work_item_type and work_item_key are required"]}
        return _do_exists(context_dir, work_item_type, work_item_key)

    if operation == "mark_stale":
        work_item_type = data.get("work_item_type")
        work_item_key = data.get("work_item_key")
        capability = data.get("capability")
        reason = data.get("reason", "")
        if not work_item_type or not work_item_key or not capability:
            return {"status": "error", "errors": ["work_item_type, work_item_key, and capability are required"]}
        return _do_mark_stale(context_dir, work_item_type, work_item_key, capability, reason)

    return {"status": "error", "errors": [f"unknown operation: {operation}"]}


def _main() -> int:
    if any(arg in ("-h", "--help") for arg in sys.argv[1:]):
        print(_help())
        return 0

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(
            json.dumps({"status": "error", "errors": [f"invalid JSON input: {exc}"]}),
            file=sys.stderr,
        )
        return 2

    result = _run(data)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] in ("appended", "found") else 1


if __name__ == "__main__":
    sys.exit(_main())
