#!/usr/bin/env python3
"""Decide whether a ticket involves verifiable state that baseline can capture.

A ticket involves verifiable state when it describes something that can be
observed, reproduced, or measured in the running system or codebase. Examples:
- UI behavior, bug reproduction, visual state.
- API response or error.
- Code-level output, test result, or performance metric.

Non-verifiable examples:
- Documentation changes.
- Process or policy decisions.
- Pure requirements clarification without implementation.

Outputs JSON:
    {
      "verifiable": true,
      "reason": "..."
    }

On failure:
    {"error": "..."}

The script is read-only, deterministic, and safe to run in any project.
"""

import argparse
import json
import sys

VERIFIABLE_INDICATORS = [
    "ui",
    "button",
    "screen",
    "modal",
    "page",
    "render",
    "display",
    "visual",
    "api",
    "endpoint",
    "response",
    "request",
    "error",
    "exception",
    "crash",
    "reproduce",
    "reproduction",
    "steps",
    "test",
    "performance",
    "latency",
    "throughput",
    "metric",
    "logs",
    "console",
    "network",
    "browser",
    "mobile",
    "device",
    "observed",
    "actual",
    "expected",
]

NON_VERIFIABLE_TYPES = {"docs", "process"}


def detect_verifiable_state(summary: str = "", description: str = "", task_type: str = "") -> dict:
    """Return whether the ticket involves verifiable state."""
    combined = f"{summary} {description}".lower()

    if task_type.lower() in NON_VERIFIABLE_TYPES:
        return {
            "verifiable": False,
            "reason": f"task type '{task_type}' is classified as non-verifiable",
        }

    hits = [kw for kw in VERIFIABLE_INDICATORS if kw in combined]
    if hits:
        return {
            "verifiable": True,
            "reason": f"verifiable indicators found: {', '.join(hits[:5])}",
        }

    return {
        "verifiable": False,
        "reason": "no verifiable state indicators found in summary or description",
    }


def main():
    parser = argparse.ArgumentParser(
        description="Decide whether a ticket involves verifiable state."
    )
    parser.add_argument("--summary", help="Ticket summary.")
    parser.add_argument("--description", help="Ticket description.")
    parser.add_argument("--task-type", help="Task type from infer-ticket-type.py.")
    args = parser.parse_args()

    try:
        result = detect_verifiable_state(
            summary=args.summary or "",
            description=args.description or "",
            task_type=args.task_type or "",
        )
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:  # pragma: no cover - safety net
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
