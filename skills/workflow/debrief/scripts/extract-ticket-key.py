#!/usr/bin/env python3
"""Extract a ticket/issue key from a branch name or arbitrary text.

Reads JSON from stdin:
  {"branch": "feature/OC-4644-auth-guard", "text": "Some text OC-123"}

Writes JSON to stdout:
  {"status": "found"|"not_found", "key": "OC-4644", "project": "OC", "source": "branch"|"text"}

If no key is found, status is "not_found" and a reason is included.
"""

import json
import re
import sys

TICKET_RE = re.compile(r"[A-Z][A-Z0-9]+-\d+")


def _help() -> str:
    return """extract-ticket-key.py — extract ticket key from branch or text

Input JSON (stdin):
  {"branch": "feature/OC-4644-auth-guard", "text": "..."}

Output JSON (stdout):
  {"status": "found"|"not_found", "key": "OC-4644", "project": "OC", "source": "branch"|"text"}
"""


def _extract_keys(text: str) -> list:
    """Return all unique ticket keys found in text, in order of appearance."""
    return list(dict.fromkeys(TICKET_RE.findall(text)))


def _run(data: dict) -> dict:
    branch = data.get("branch", "")
    text = data.get("text", "")

    branch_keys = _extract_keys(branch) if branch else []
    text_keys = _extract_keys(text) if text else []

    if branch_keys:
        key = branch_keys[0]
        source = "branch"
    elif text_keys:
        key = text_keys[0]
        source = "text"
    else:
        return {
            "status": "not_found",
            "key": None,
            "project": None,
            "source": None,
            "reason": "no ticket key found in branch or text",
        }

    project = key.split("-", 1)[0]
    return {
        "status": "found",
        "key": key,
        "project": project,
        "source": source,
    }


if __name__ == "__main__":
    if any(arg in ("-h", "--help") for arg in sys.argv[1:]):
        print(_help())
        sys.exit(0)

    try:
        data = json.load(sys.stdin)
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "not_found",
                    "key": None,
                    "project": None,
                    "source": None,
                    "reason": f"invalid JSON input: {exc}",
                }
            ),
            file=sys.stderr,
        )
        sys.exit(2)

    result = _run(data)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] == "found" else 1)
