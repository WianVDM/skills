#!/usr/bin/env python3
"""chainlog.py

Append-only storage for observations collected by tools.

Operations:
  append        Add a new observation entry to a work-item chain.
  query_latest  Return the latest entry per capability (or for one capability).
  query_all     Return all entries for a work item, optionally filtered by capability.
  query_since   Return entries collected after a given timestamp.
  exists        Check whether a work item has any observations.
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


class InputError(ValueError):
    """Invalid caller input; maps to exit code 2."""


# Required frontmatter fields for an observation entry.
REQUIRED_ENTRY_FIELDS = [
    "work_item_type",
    "work_item_key",
    "capability",
    "source",
]


def _help() -> str:
    return """chainlog.py — append-only storage for tool observations

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


def _chain_path(context_dir: Path, work_item_type: str, work_item_key: str) -> Path:
    """Return the chain file path for a work item."""
    return context_dir / "chainlog" / work_item_type / f"{_slugify(work_item_key)}.chain.md"


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


# Fields that mark the start of a chain entry's frontmatter.
_ENTRY_START_FIELDS = set(REQUIRED_ENTRY_FIELDS) | {"observation_id", "stale", "collected_at"}


def _looks_like_entry_start(lines: list[str], i: int) -> bool:
    """An entry starts at a line exactly '---' followed by a frontmatter block
    that closes with '---' and parses to a dict holding at least one known field.
    This keeps opaque bodies (markdown, diffs, stack traces) from desyncing the
    parse: a '---' inside a body does not start an entry unless the following
    block really is observation frontmatter."""
    if lines[i] != "---":
        return False
    j = i + 1
    block: list[str] = []
    while j < len(lines) and lines[j] != "---":
        block.append(lines[j])
        j += 1
    if j >= len(lines) or not block:
        return False
    frontmatter = _parse_frontmatter("\n".join(block))
    return bool(frontmatter) and any(f in frontmatter for f in _ENTRY_START_FIELDS)


def _parse_chain(text: str) -> list[dict]:
    """Parse a chain file into a list of entries with frontmatter and body.

    State machine over lines: entry start (validated frontmatter), body up to
    the next entry start or EOF. Empty-bodied entries are preserved."""
    if not text.strip():
        return []

    lines = text.splitlines()
    entries: list[dict] = []
    i = 0
    n = len(lines)
    while i < n:
        if not _looks_like_entry_start(lines, i):
            i += 1
            continue
        j = i + 1
        block: list[str] = []
        while j < n and lines[j] != "---":
            block.append(lines[j])
            j += 1
        frontmatter = _parse_frontmatter("\n".join(block))
        j += 1  # skip the closing ---
        if j < n and lines[j].strip() == "":
            j += 1  # one blank line separates frontmatter from body
        body_lines: list[str] = []
        k = j
        while k < n:
            if lines[k] == "---" and _looks_like_entry_start(lines, k):
                break
            body_lines.append(lines[k])
            k += 1
        entries.append({"frontmatter": frontmatter, "body": "\n".join(body_lines).strip("\n")})
        i = k
    return entries


def _escape_body(body: str) -> str:
    """Render body lines that are exactly '---' as '--- ' (trailing space).

    Visually identical in markdown, but no longer an exact delimiter line, so a
    written body can never desync the chain parser."""
    return "\n".join(line + " " if line == "---" else line for line in body.split("\n"))


def _render_entry(entry: dict) -> str:
    """Render an observation entry as markdown text."""
    frontmatter = dict(entry.get("frontmatter", {}))
    body = _escape_body(entry.get("body", ""))
    fm_text = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False, allow_unicode=True)
    return f"---\n{fm_text}---\n\n{body}\n"


def _validate_entry(entry: dict) -> list[str]:
    """Validate required observation entry fields."""
    errors = []
    for field in REQUIRED_ENTRY_FIELDS:
        if field not in entry or entry[field] is None or entry[field] == "":
            errors.append(f"missing required field: {field}")
    return errors


def _entry_to_output(entry: dict) -> dict:
    """Convert an internal entry to the output format.

    The payload lives in the body. Legacy entries written with the payload in
    frontmatter (duplicated in the body) are normalized to the same shape."""
    frontmatter = dict(entry["frontmatter"])
    body = entry["body"]
    legacy_payload = frontmatter.pop("payload", None)
    if legacy_payload and not body:
        body = legacy_payload
    return {
        "frontmatter": frontmatter,
        "body": body,
    }


def _do_append(context_dir: Path, entry: dict) -> dict:
    """Append an observation entry to the work-item chain."""
    errors = _validate_entry(entry)
    if errors:
        return {"status": "error", "errors": errors}

    work_item_type = entry["work_item_type"]
    work_item_key = entry["work_item_key"]
    chain_path = _chain_path(context_dir, work_item_type, work_item_key)
    chain_path.parent.mkdir(parents=True, exist_ok=True)

    # Ensure observation_id and collected_at are present.
    if "observation_id" not in entry or not entry["observation_id"]:
        entry["observation_id"] = str(uuid.uuid4())
    if "collected_at" not in entry or not entry["collected_at"]:
        entry["collected_at"] = _format_timestamp(datetime.datetime.now(datetime.timezone.utc))

    # The payload is the body; it is not duplicated into frontmatter.
    payload = entry.pop("payload", "")
    rendered = _render_entry({"frontmatter": entry, "body": payload})

    # Append to file.
    with chain_path.open("a", encoding="utf-8") as f:
        f.write(rendered)

    return {
        "status": "appended",
        "observation_id": entry["observation_id"],
        "path": str(chain_path),
    }


def _do_query(
    context_dir: Path,
    work_item_type: str,
    work_item_key: str,
    capability: str | None,
    since: str | None,
) -> dict:
    """Query observation entries for a work item."""
    chain_path = _chain_path(context_dir, work_item_type, work_item_key)
    if not chain_path.exists():
        return {
            "status": "not_found",
            "entries": [],
            "count": 0,
        }

    text = chain_path.read_text(encoding="utf-8", errors="ignore")
    entries = _parse_chain(text)

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
    """Return the latest observation entry per capability for a work item."""
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
    """Check whether a work item has any observations."""
    chain_path = _chain_path(context_dir, work_item_type, work_item_key)
    if not chain_path.exists():
        return {"status": "found", "exists": False, "path": str(chain_path), "count": 0}

    text = chain_path.read_text(encoding="utf-8", errors="ignore")
    entries = _parse_chain(text)
    return {
        "status": "found",
        "exists": len(entries) > 0,
        "path": str(chain_path),
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
        "observation_id": str(uuid.uuid4()),
        "work_item_type": work_item_type,
        "work_item_key": work_item_key,
        "capability": capability,
        "source": "stale-marker",
        "collected_at": _format_timestamp(datetime.datetime.now(datetime.timezone.utc)),
        "stale": True,
        "reason": reason,
    }
    return _do_append(context_dir, entry)


def _require_work_item(data: dict, need_capability: bool = False) -> tuple[str, str]:
    work_item_type = data.get("work_item_type")
    work_item_key = data.get("work_item_key")
    if not work_item_type or not work_item_key:
        raise InputError("work_item_type and work_item_key are required")
    if need_capability and not data.get("capability"):
        raise InputError("work_item_type, work_item_key, and capability are required")
    return work_item_type, work_item_key


def _run(data: dict) -> dict:
    operation = data.get("operation")
    context_dir = Path(data.get("context_dir", ".agents/context")).resolve()

    if operation == "append":
        entry = data.get("entry")
        if not isinstance(entry, dict):
            raise InputError("entry is required for append")
        return _do_append(context_dir, entry)

    if operation == "query_latest":
        work_item_type, work_item_key = _require_work_item(data)
        return _do_query_latest(context_dir, work_item_type, work_item_key, data.get("capability"))

    if operation == "query_all":
        work_item_type, work_item_key = _require_work_item(data)
        return _do_query(context_dir, work_item_type, work_item_key, data.get("capability"), None)

    if operation == "query_since":
        work_item_type, work_item_key = _require_work_item(data)
        return _do_query(context_dir, work_item_type, work_item_key, data.get("capability"), data.get("since"))

    if operation == "exists":
        work_item_type, work_item_key = _require_work_item(data)
        return _do_exists(context_dir, work_item_type, work_item_key)

    if operation == "mark_stale":
        work_item_type, work_item_key = _require_work_item(data, need_capability=True)
        return _do_mark_stale(
            context_dir, work_item_type, work_item_key,
            data.get("capability"), data.get("reason", ""),
        )

    raise InputError(f"unknown operation: {operation}")


def _main() -> int:
    if any(arg in ("-h", "--help") for arg in sys.argv[1:]):
        print(_help())
        return 0

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(json.dumps({"status": "error", "errors": [f"invalid JSON input: {exc}"]}))
        return 2

    try:
        result = _run(data)
        code = 0 if result["status"] in ("appended", "found") else 1
    except InputError as exc:
        result = {"status": "error", "errors": [str(exc)]}
        code = 2

    print(json.dumps(result, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(_main())
