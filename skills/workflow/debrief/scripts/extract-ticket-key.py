#!/usr/bin/env python3
"""Extract a ticket/issue key from a branch name or arbitrary text.

Matches keys in the form [A-Z][A-Z0-9]+-d+ (e.g., OC-4644, SHB-362).
If multiple keys are found, prefers the first key in the branch (if provided),
otherwise the first key in the text.

Outputs JSON:
    {"key": "OC-4644", "project": "OC", "source": "branch|text"}

On failure:
    {"error": "..."}

The script is read-only, deterministic, and safe to run in any project.
"""

import argparse
import json
import re
import sys

TICKET_RE = re.compile(r"[A-Z][A-Z0-9]+-\d+")


def _extract_keys(text: str) -> list:
    """Return all unique ticket keys found in text, in order of appearance."""
    return list(dict.fromkeys(TICKET_RE.findall(text)))


def extract_ticket_key(branch: str = None, text: str = None) -> dict:
    """Extract a ticket key from branch and/or text."""
    branch_keys = _extract_keys(branch) if branch else []
    text_keys = _extract_keys(text) if text else []

    if branch_keys:
        key = branch_keys[0]
        source = "branch"
    elif text_keys:
        key = text_keys[0]
        source = "text"
    else:
        return {"error": "no ticket key found in branch or text"}

    project = key.split("-", 1)[0]
    return {"key": key, "project": project, "source": source}


def main():
    parser = argparse.ArgumentParser(
        description="Extract a ticket/issue key from a branch name or arbitrary text."
    )
    parser.add_argument("--branch", help="Branch name to search for a ticket key.")
    parser.add_argument("--text", help="Arbitrary text to search for a ticket key.")
    args = parser.parse_args()

    if not args.branch and not args.text:
        print(
            json.dumps({"error": "at least one of --branch or --text is required"}),
            file=sys.stderr,
        )
        return 1

    try:
        result = extract_ticket_key(branch=args.branch, text=args.text)
        if "error" in result:
            print(json.dumps(result), file=sys.stderr)
            return 1
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:  # pragma: no cover - safety net
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
