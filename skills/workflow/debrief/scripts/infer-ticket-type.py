#!/usr/bin/env python3
"""Classify a ticket into a task type.

Uses keywords in the summary, description, and labels to classify the ticket
as one of: code, ui, docs, process, unknown.

Outputs JSON:
    {
      "task_type": "code",
      "confidence": 85,
      "reason": "..."
    }

On failure:
    {"error": "..."}

The script is read-only, deterministic, and safe to run in any project.
"""

import argparse
import json
import sys

TYPE_PATTERNS = {
    "ui": [
        "ui",
        "ux",
        "interface",
        "screen",
        "button",
        "modal",
        "dropdown",
        "visual",
        "design",
        "css",
        "component",
        "frontend",
        "layout",
        "icon",
        "theme",
        "style",
    ],
    "docs": [
        "doc",
        "documentation",
        "readme",
        "guide",
        "wiki",
        "comment",
        "adr",
        "explain",
    ],
    "process": [
        "process",
        "workflow",
        "pipeline",
        "policy",
        "procedure",
        "compliance",
        "audit",
        "ops",
        "operations",
        "oncall",
        "on-call",
    ],
    "code": [
        "bug",
        "fix",
        "refactor",
        "implement",
        "feature",
        "api",
        "endpoint",
        "service",
        "backend",
        "logic",
        "validation",
        "error",
        "exception",
        "performance",
        "race",
        "deadlock",
        "migration",
        "test",
    ],
}


def _score(text: str) -> dict:
    """Return a score map for each type based on keyword matches."""
    text_lower = text.lower()
    scores = {}
    for task_type, keywords in TYPE_PATTERNS.items():
        scores[task_type] = sum(1 for kw in keywords if kw in text_lower)
    return scores


def infer_ticket_type(summary: str = "", description: str = "", labels: str = "") -> dict:
    """Classify the ticket and return type plus confidence."""
    combined = f"{summary} {description} {labels}"
    if not combined.strip():
        return {"task_type": "unknown", "confidence": 0, "reason": "no input provided"}

    scores = _score(combined)
    best = max(scores, key=scores.get)
    best_score = scores[best]
    total = sum(scores.values())

    if best_score == 0:
        return {
            "task_type": "unknown",
            "confidence": 0,
            "reason": "no type indicators found",
        }

    # Confidence scales with the proportion of matching keywords.
    if total == best_score:
        confidence = 90
    else:
        confidence = min(95, 50 + int((best_score / total) * 50))

    return {
        "task_type": best,
        "confidence": confidence,
        "reason": f"matched {best_score} keywords for type '{best}'",
    }


def main():
    parser = argparse.ArgumentParser(
        description="Classify a ticket into a task type."
    )
    parser.add_argument("--summary", help="Ticket summary.")
    parser.add_argument("--description", help="Ticket description.")
    parser.add_argument(
        "--labels",
        help="Comma-separated labels or components.",
    )
    args = parser.parse_args()

    try:
        result = infer_ticket_type(
            summary=args.summary or "",
            description=args.description or "",
            labels=args.labels or "",
        )
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:  # pragma: no cover - safety net
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
