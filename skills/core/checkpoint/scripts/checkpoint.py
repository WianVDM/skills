#!/usr/bin/env python3
"""checkpoint.py — deterministic state manager for long-running conductor skills.

Reads JSON from stdin and writes JSON to stdout. Supports create, update, resume,
and validate operations for checkpoint state files.

Usage:
    echo '{"operation":"create",...}' | python checkpoint.py
    python checkpoint.py --help
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Allow importing the shared _frontmatter parser from the debrief skill.
_DEBRIEF_SCRIPTS = Path(__file__).resolve().parents[3] / "workflow" / "debrief" / "scripts"
if str(_DEBRIEF_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_DEBRIEF_SCRIPTS))

try:
    import _frontmatter  # type: ignore
except ImportError as _exc:  # pragma: no cover
    sys.stderr.write(f"ERROR: cannot import _frontmatter parser: {_exc}\n")
    sys.exit(2)


DEFAULT_MAX_HISTORY_ROWS = 20
REQUIRED_FRONTMATTER_KEYS = ["skill", "version", "state_schema", "owner", "key", "updated_at"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _fail(errors: list[str], **extra: Any) -> dict:
    result: dict[str, Any] = {"status": "error", "errors": errors}
    result.update(extra)
    return result


def _ok(**extra: Any) -> dict:
    result: dict[str, Any] = {"status": "complete"}
    result.update(extra)
    return result


def _phase_item_text(index: int, phase: str) -> str:
    """Return the canonical checklist item text for a phase."""
    stripped = phase.strip()
    if re.match(r"(?i)^phase\s+\d+\s*:", stripped):
        return stripped
    return f"Phase {index}: {stripped}"


def _extract_phase_name(item_text: str) -> str:
    """Extract the phase name from a checklist item like 'Phase 0: Bootstrap'."""
    match = re.match(r"(?i)^phase\s+\d+\s*:\s*(.+)$", item_text.strip())
    if match:
        return match.group(1).strip()
    return item_text.strip()


# ---------------------------------------------------------------------------
# State parsing and rendering
# ---------------------------------------------------------------------------


def _parse_phase_checklist(section_text: str) -> list[dict]:
    items: list[dict] = []
    for line in section_text.splitlines():
        match = re.match(r"^-\s*\[([ x/])\]\s*(.+)$", line.strip())
        if not match:
            continue
        status_char = match.group(1).lower()
        if status_char == "x":
            status = "completed"
        elif status_char == "/":
            status = "in-progress"
        else:
            status = "pending"
        text = match.group(2).strip()
        items.append({"text": text, "status": status, "phase": _extract_phase_name(text)})
    return items


def _parse_session_history(section_text: str) -> list[dict]:
    rows: list[dict] = []
    for line in section_text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.split("|")]
        # Remove leading/trailing empty cells caused by the outer pipes.
        cells = [c for c in cells if c]
        if not cells or cells[0] in ("#", "-"):
            continue
        try:
            number = int(cells[0])
        except (ValueError, IndexError):
            continue
        if len(cells) < 4:
            continue
        rows.append({
            "number": number,
            "timestamp": cells[1],
            "action": cells[2],
            "focus_after": cells[3],
        })
    return rows


def _parse_state_body(body: str) -> dict:
    """Parse the markdown body into structured sections."""
    sections: dict[str, str] = {}
    current_heading: str | None = None
    current_lines: list[str] = []

    for line in body.splitlines():
        heading_match = re.match(r"^##\s+(.+)$", line)
        if heading_match:
            if current_heading is not None:
                sections[current_heading] = "\n".join(current_lines).strip()
            current_heading = heading_match.group(1).strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_heading is not None:
        sections[current_heading] = "\n".join(current_lines).strip()

    phase_checklist = _parse_phase_checklist(sections.get("Phase Checklist", ""))
    current_focus = sections.get("Current Focus", "").strip()
    last_action = sections.get("Last Completed Action", "").strip()
    history = _parse_session_history(sections.get("Session History", ""))

    owner_sections = sections.get("Owner Sections", "")
    return {
        "phase_checklist": phase_checklist,
        "current_focus": current_focus,
        "last_action": last_action,
        "history": history,
        "owner_sections": owner_sections,
    }


def _render_checklist_item(item: dict) -> str:
    if item["status"] == "completed":
        marker = "x"
    elif item["status"] == "in-progress":
        marker = "/"
    else:
        marker = " "
    return f"- [{marker}] {item['text']}"


def _render_body(
    phase_checklist: list[dict],
    current_focus: str,
    last_action: str,
    history: list[dict],
    owner_sections: str,
) -> str:
    lines = ["# Checkpoint State"]

    lines.append("")
    lines.append("## Phase Checklist")
    for item in phase_checklist:
        lines.append(_render_checklist_item(item))

    lines.append("")
    lines.append("## Current Focus")
    lines.append(current_focus)

    lines.append("")
    lines.append("## Last Completed Action")
    lines.append(last_action)

    lines.append("")
    lines.append("## Session History")
    lines.append("| # | Timestamp | Action | Focus After |")
    lines.append("|---|-----------|--------|-------------|")
    for row in history:
        lines.append(
            f"| {row['number']} | {row['timestamp']} | {row['action']} | {row['focus_after']} |"
        )

    lines.append("")
    lines.append("## Owner Sections")
    if owner_sections:
        lines.append(owner_sections)
    else:
        lines.append("<!-- The owner skill can add arbitrary sections below this marker. -->")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# State file I/O
# ---------------------------------------------------------------------------


def _read_state(path: str) -> tuple[dict, dict, str]:
    """Read and parse a state file.

    Returns (frontmatter, parsed_body, raw_body).
    """
    state_path = Path(path)
    if not state_path.exists():
        raise FileNotFoundError(f"state file not found: {path}")
    text = state_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"state file is missing YAML frontmatter: {path}")
    frontmatter = _frontmatter.parse_frontmatter(text)
    end = text.find("---", 3)
    body = text[end + 3 :].lstrip("\n") if end != -1 else ""
    parsed_body = _parse_state_body(body)
    return frontmatter, parsed_body, body


def _write_state(path: str, frontmatter: dict, body: str) -> None:
    state_path = Path(path)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    # dump_frontmatter with empty text returns only the frontmatter block.
    fm_text = _frontmatter.dump_frontmatter(frontmatter, "").rstrip()
    text = f"{fm_text}\n\n{body}"
    state_path.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _validate_state(frontmatter: dict, parsed_body: dict) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED_FRONTMATTER_KEYS:
        if key not in frontmatter:
            errors.append(f"missing required frontmatter key: {key}")
    if frontmatter.get("skill") != "checkpoint":
        errors.append(f"expected skill 'checkpoint', got {frontmatter.get('skill')!r}")
    if not parsed_body["phase_checklist"]:
        errors.append("phase checklist is empty")
    for item in parsed_body["phase_checklist"]:
        if item["status"] not in ("pending", "in-progress", "completed"):
            errors.append(f"invalid phase status: {item['status']}")
    in_progress = [item for item in parsed_body["phase_checklist"] if item["status"] == "in-progress"]
    if len(in_progress) > 1:
        errors.append(f"multiple in-progress phases: {[i['text'] for i in in_progress]}")
    return errors


# ---------------------------------------------------------------------------
# History archiving
# ---------------------------------------------------------------------------


def _archive_history(state_path: str, history: list[dict], max_rows: int) -> list[dict]:
    """Archive oldest rows when history exceeds max_rows. Returns the kept rows."""
    if len(history) <= max_rows:
        return history

    kept = history[-max_rows:]
    archived = history[:-max_rows]

    archive_path = Path(f"{state_path}.history.md")
    archive_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    if archive_path.exists():
        lines.append("")
        lines.append(f"## Archive entry {_now_iso()}")
    else:
        lines.append("# Checkpoint Session History Archive")
        lines.append("")
        lines.append("| # | Timestamp | Action | Focus After |")
        lines.append("|---|-----------|--------|-------------|")

    for row in archived:
        lines.append(
            f"| {row['number']} | {row['timestamp']} | {row['action']} | {row['focus_after']} |"
        )

    with archive_path.open("a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    # Renumber kept rows so they start at 1 in the active file.
    for i, row in enumerate(kept, start=1):
        row["number"] = i
    return kept


# ---------------------------------------------------------------------------
# Operations
# ---------------------------------------------------------------------------


def _op_create(data: dict) -> dict:
    state_path = data.get("state_path")
    owner = data.get("owner")
    key = data.get("key")
    phases = data.get("phases")
    focus = data.get("focus")
    max_history_rows = int(data.get("max_history_rows", DEFAULT_MAX_HISTORY_ROWS))

    if not state_path:
        return _fail(["missing required input: state_path"])
    if not owner:
        return _fail(["missing required input: owner"])
    if not key:
        return _fail(["missing required input: key"])
    if not phases or not isinstance(phases, list):
        return _fail(["missing or invalid input: phases (list required)"])

    if Path(state_path).exists():
        return _fail([f"state file already exists: {state_path}"])

    phase_checklist = [
        {"text": _phase_item_text(i, phase), "status": "pending", "phase": phase.strip()}
        for i, phase in enumerate(phases)
    ]

    if focus is None and phase_checklist:
        focus = _extract_phase_name(phase_checklist[0]["text"])

    frontmatter = {
        "skill": "checkpoint",
        "version": "1.0.0",
        "state_schema": "1.0.0",
        "owner": owner,
        "key": key,
        "updated_at": _now_iso(),
    }

    body = _render_body(
        phase_checklist=phase_checklist,
        current_focus=focus or "",
        last_action="",
        history=[],
        owner_sections="",
    )

    _write_state(state_path, frontmatter, body)
    return _ok(state_path=state_path)


def _op_update(data: dict) -> dict:
    state_path = data.get("state_path")
    if not state_path:
        return _fail(["missing required input: state_path"])

    try:
        frontmatter, parsed, _ = _read_state(state_path)
    except (FileNotFoundError, ValueError) as exc:
        return _fail([str(exc)])

    errors = _validate_state(frontmatter, parsed)
    if errors:
        return _fail(errors)

    checklist = parsed["phase_checklist"]
    completed_phase = data.get("completed_phase")
    in_progress_phase = data.get("in_progress_phase")
    current_focus = data.get("current_focus", parsed["current_focus"])
    last_action = data.get("last_action", parsed["last_action"])
    owner_sections = data.get("owner_sections", parsed["owner_sections"])
    max_history_rows = int(data.get("max_history_rows", DEFAULT_MAX_HISTORY_ROWS))

    def _match_phase(name: str) -> dict | None:
        target = name.strip().lower()
        for item in checklist:
            if item["phase"].lower() == target:
                return item
        # Fallback: substring match.
        for item in checklist:
            if target in item["text"].lower():
                return item
        return None

    if completed_phase:
        item = _match_phase(completed_phase)
        if item is None:
            return _fail([f"completed_phase not found in checklist: {completed_phase}"])
        item["status"] = "completed"
        # A completed phase cannot also be in-progress.
        if item["status"] == "in-progress":
            item["status"] = "completed"

    if in_progress_phase:
        # Clear any existing in-progress marker first.
        for item in checklist:
            if item["status"] == "in-progress":
                item["status"] = "pending"
        item = _match_phase(in_progress_phase)
        if item is None:
            return _fail([f"in_progress_phase not found in checklist: {in_progress_phase}"])
        if item["status"] != "completed":
            item["status"] = "in-progress"
        else:
            return _fail([f"cannot mark completed phase as in-progress: {in_progress_phase}"])

    # Append to session history if a last_action was provided.
    if data.get("last_action"):
        next_number = (parsed["history"][-1]["number"] + 1) if parsed["history"] else 1
        parsed["history"].append({
            "number": next_number,
            "timestamp": _now_iso(),
            "action": last_action,
            "focus_after": current_focus,
        })

    parsed["history"] = _archive_history(state_path, parsed["history"], max_history_rows)

    frontmatter["updated_at"] = _now_iso()
    body = _render_body(
        phase_checklist=checklist,
        current_focus=current_focus,
        last_action=last_action,
        history=parsed["history"],
        owner_sections=owner_sections,
    )
    _write_state(state_path, frontmatter, body)

    pending = [item for item in checklist if item["status"] == "pending"]
    next_pending_phase = pending[0]["phase"] if pending else None

    return _ok(
        state_path=state_path,
        phase_checklist=[
            {"phase": item["phase"], "status": item["status"]} for item in checklist
        ],
        current_focus=current_focus,
        next_pending_phase=next_pending_phase,
    )


def _op_resume(data: dict) -> dict:
    state_path = data.get("state_path")
    if not state_path:
        return _fail(["missing required input: state_path"])

    try:
        frontmatter, parsed, _ = _read_state(state_path)
    except (FileNotFoundError, ValueError) as exc:
        return _fail([str(exc)])

    errors = _validate_state(frontmatter, parsed)
    if errors:
        return _fail(errors)

    completed = [item["phase"] for item in parsed["phase_checklist"] if item["status"] == "completed"]
    pending = [item["phase"] for item in parsed["phase_checklist"] if item["status"] == "pending"]
    in_progress_items = [item for item in parsed["phase_checklist"] if item["status"] == "in-progress"]
    in_progress_phase = in_progress_items[0]["phase"] if in_progress_items else None
    next_pending_phase = pending[0] if pending else None

    return _ok(
        completed_phases=completed,
        pending_phases=pending,
        in_progress_phase=in_progress_phase,
        current_focus=parsed["current_focus"],
        last_action=parsed["last_action"],
        next_pending_phase=next_pending_phase,
        owner_sections=parsed["owner_sections"],
    )


def _op_validate(data: dict) -> dict:
    state_path = data.get("state_path")
    if not state_path:
        return _fail(["missing required input: state_path"])

    try:
        frontmatter, parsed, _ = _read_state(state_path)
    except (FileNotFoundError, ValueError) as exc:
        return _fail([str(exc)])

    errors = _validate_state(frontmatter, parsed)
    return _ok(valid=len(errors) == 0, errors=errors)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def _help() -> str:
    return """checkpoint.py — maintain phase checklists and resume state for conductor skills

Reads JSON from stdin:
  {"operation": "create", "state_path": "...", "owner": "...", "key": "...", "phases": [...]}
  {"operation": "update", "state_path": "...", "completed_phase": "...", "current_focus": "...", "last_action": "..."}
  {"operation": "resume", "state_path": "..."}
  {"operation": "validate", "state_path": "..."}

Writes JSON to stdout.
"""


def _run(data: dict) -> dict:
    operation = data.get("operation")
    if not operation:
        return _fail(["missing required input: operation"])

    if operation == "create":
        return _op_create(data)
    if operation == "update":
        return _op_update(data)
    if operation == "resume":
        return _op_resume(data)
    if operation == "validate":
        return _op_validate(data)

    return _fail([f"unknown operation: {operation}"])


def main() -> int:
    if any(arg in ("-h", "--help") for arg in sys.argv[1:]):
        print(_help())
        return 0

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(json.dumps(_fail([f"invalid JSON input: {exc}"])), file=sys.stderr)
        return 2

    result = _run(data)
    print(json.dumps(result, indent=2))
    return 0 if result.get("status") == "complete" else 1


if __name__ == "__main__":
    sys.exit(main())
