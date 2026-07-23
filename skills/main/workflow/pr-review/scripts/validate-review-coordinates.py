#!/usr/bin/env python3
"""validate-review-coordinates.py

Validate that review-comment line coordinates fall inside changed diff hunks.

Deterministic half of the posting gate: the model proposes comments, this
script proves or disproves that each coordinate is postable.

Input JSON on stdin:
  {
    "diff": "<unified diff text>",
    "comments": [{"path": "src/x.ts", "line": 42, "side": "RIGHT"}]
  }

Output JSON to stdout:
  {
    "status": "ok" | "invalid",
    "invalid_count": 0,
    "results": [{"path": "src/x.ts", "line": 42, "side": "RIGHT",
                 "valid": true, "detail": "..."}]
  }

Rules:
  - RIGHT-side lines are checked against the new-file ranges of each hunk.
  - LEFT-side lines are checked against the old-file ranges.
  - Context lines inside a hunk are valid for both sides.
  - Renamed files validate RIGHT-side comments against the new path.
"""

from __future__ import annotations

import json
import re
import sys


HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def _help() -> str:
    return """validate-review-coordinates.py — check comment coordinates against diff hunks

Input JSON (stdin):
  {"diff": "<unified diff>", "comments": [{"path": "src/x.ts", "line": 42, "side": "RIGHT"}]}

Output JSON (stdout):
  {"status": "ok"|"invalid", "invalid_count": N, "results": [...]}
"""


def parse_diff(diff_text: str) -> dict:
    """Parse a unified diff into per-file hunk ranges.

    Returns {new_path: {"right": [(start, end)], "left": [(start, end)], "old_path": str}}.
    Ranges are inclusive line intervals.
    """
    files: dict[str, dict] = {}
    current = None

    for raw_line in diff_text.splitlines():
        if raw_line.startswith("diff --git"):
            current = None
            continue
        if raw_line.startswith("--- "):
            continue
        if raw_line.startswith("+++ "):
            new_path = raw_line[4:].strip()
            if new_path.startswith("b/"):
                new_path = new_path[2:]
            if new_path == "/dev/null":
                current = None
                continue
            current = files.setdefault(new_path, {"right": [], "left": []})
            continue

        match = HUNK_RE.match(raw_line)
        if match and current is not None:
            old_start = int(match.group(1))
            old_count = int(match.group(2) or "1")
            new_start = int(match.group(3))
            new_count = int(match.group(4) or "1")
            if old_count > 0:
                current["left"].append((old_start, old_start + old_count - 1))
            if new_count > 0:
                current["right"].append((new_start, new_start + new_count - 1))

    return files


def validate(diff_text: str, comments: list) -> list:
    files = parse_diff(diff_text)
    results = []

    for comment in comments:
        path = comment.get("path", "")
        line = comment.get("line")
        side = str(comment.get("side", "RIGHT")).upper()

        entry = files.get(path)
        if entry is None:
            results.append({
                "path": path, "line": line, "side": side,
                "valid": False,
                "detail": f"path '{path}' not present in the diff",
            })
            continue

        if not isinstance(line, int) or line < 1:
            results.append({
                "path": path, "line": line, "side": side,
                "valid": False,
                "detail": f"line '{line}' is not a positive integer",
            })
            continue

        ranges = entry["left"] if side == "LEFT" else entry["right"]
        hit = next((r for r in ranges if r[0] <= line <= r[1]), None)
        if hit:
            results.append({
                "path": path, "line": line, "side": side,
                "valid": True,
                "detail": f"line {line} inside {side.lower()}-side range {hit[0]}-{hit[1]}",
            })
        else:
            results.append({
                "path": path, "line": line, "side": side,
                "valid": False,
                "detail": f"line {line} outside {side.lower()}-side hunks ({', '.join(f'{a}-{b}' for a, b in ranges) or 'none'})",
            })

    return results


def _main() -> int:
    if any(arg in ("-h", "--help") for arg in sys.argv[1:]):
        print(_help())
        return 0

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(json.dumps({"status": "error", "errors": [f"invalid JSON input: {exc}"]}))
        return 2

    if not isinstance(data, dict) or "diff" not in data or "comments" not in data:
        print(json.dumps({"status": "error", "errors": ["input must contain 'diff' and 'comments'"]}))
        return 2

    try:
        results = validate(data["diff"], data["comments"])
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"status": "error", "errors": [f"runtime failure: {exc}"]}))
        return 1

    invalid = [r for r in results if not r["valid"]]
    print(json.dumps({
        "status": "invalid" if invalid else "ok",
        "invalid_count": len(invalid),
        "results": results,
    }, indent=2))
    return 1 if invalid else 0


if __name__ == "__main__":
    sys.exit(_main())
