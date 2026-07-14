#!/usr/bin/env python3
"""Decide whether a ticket describes verifiable state that baseline can capture.

Reads JSON from stdin:
  {
    "summary": "Auth guard race condition",
    "description": "When navigating between protected routes...",
    "labels": ["auth", "bug"],
    "task_type": "code"
  }

Writes JSON to stdout:
  {
    "status": "verifiable"|"not_verifiable",
    "verifiable": true|false,
    "reason": "...",
    "verify_scope": "...",
    "confidence": "high"|"medium"|"low"
  }

Uses semantic signals and task_type rather than a simple keyword list.
"""

import json
import re
import sys


# Semantic signal patterns grouped by category. Patterns are phrase oriented
# where possible to avoid keyword-only triggers.
SEMANTIC_SIGNALS = [
    ("reproduction scenario", [
        r"\bsteps\s+to\s+reproduce\b",
        r"\breproduc(?:e|es|ed|ing|ible)\b",
        r"\bobserved\s+behavior\b",
        r"\bactual\s+behavior\b",
        r"\bexpected\s+behavior\b",
    ]),
    ("runtime error", [
        r"\berror\s+(?:message|occurs|happens)\b",
        r"\bexception\b",
        r"\bcrash(?:es|ed)?\b",
        r"\bstack\s+trace\b",
        r"\bfailure\b",
    ]),
    ("UI behavior", [
        r"\bui(?:\s+behavior)?\b",
        r"\bbutton\b",
        r"\bmodal\b",
        r"\bscreen\b",
        r"\bpage(?:\s+load)?\b",
        r"\bnavigat(?:e|es|ed|ing|ion)\b",
        r"\brender(?:s|ing|ed)?\b",
        r"\bdisplay(?:s|ed)?\b",
        r"\bvisual\b",
        r"\bcomponent\b",
        r"\bform\b",
        r"\bclick(?:s|ed)?\b",
        r"\btap(?:s|ped)?\b",
        r"\bdropdown\b",
        r"\bmenu\b",
    ]),
    ("API behavior", [
        r"\bapi\s+(?:call|endpoint|request|response)\b",
        r"\bendpoint\b",
        r"\brequest(?:s|ed)?\b",
        r"\bresponse(?:s|ed)?\b",
        r"\bstatus\s+code\b",
        r"\bhttp\b",
        r"\breturns?\b",
        r"\bpayload\b",
    ]),
    ("test behavior", [
        r"\btest(?:s)?\s+(?:fail|fails|failure|case)\b",
        r"\bfailing\s+test\b",
        r"\bunit\s+test\b",
        r"\bintegration\s+test\b",
    ]),
    ("performance metric", [
        r"\bperformance\b",
        r"\blatency\b",
        r"\bslow(?:ness)?\b",
        r"\bthroughput\b",
        r"\bmetric\b",
        r"\bbenchmark\b",
    ]),
    ("observable output", [
        r"\blog(?:s|ged)?\b",
        r"\bconsole\b",
        r"\boutput(?:s|ted)?\b",
        r"\bprinted\b",
    ]),
]


def _help() -> str:
    return """detect-verifiable-state.py — decide whether a ticket describes verifiable state

Input JSON (stdin):
  {"summary": "...", "description": "...", "labels": ["..."], "task_type": "code"|"ui"|"docs"|"process"}

Output JSON (stdout):
  {"status": "verifiable"|"not_verifiable", "verifiable": true|false, "reason": "...", "verify_scope": "...", "confidence": "high"|"medium"|"low"}
"""


def _normalized_labels(labels) -> list:
    if not labels:
        return []
    return [str(label).lower().strip() for label in labels if label]


def _detect_signals(text: str) -> list:
    """Return matched semantic categories."""
    matched = []
    for category, patterns in SEMANTIC_SIGNALS:
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE):
                matched.append(category)
                break
    return matched


def _first_sentence(text: str) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return sentences[0] if sentences else text


def _run(data: dict) -> dict:
    summary = (data.get("summary") or "").strip()
    description = (data.get("description") or "").strip()
    labels = _normalized_labels(data.get("labels"))
    task_type = (data.get("task_type") or "").lower().strip()

    text = f"{summary} {description}".lower()

    # Non-verifiable task types override almost everything
    if task_type in ("docs", "process"):
        return {
            "status": "not_verifiable",
            "verifiable": False,
            "reason": f"task_type '{task_type}' indicates non-implementation work without observable behavior",
            "verify_scope": "",
            "confidence": "high",
        }

    if "docs" in labels:
        return {
            "status": "not_verifiable",
            "verifiable": False,
            "reason": "label 'docs' indicates documentation work",
            "verify_scope": "",
            "confidence": "high",
        }

    # Label overrides that force verifiable state
    if any(label in ("baseline", "regression", "ui") for label in labels):
        scope = summary or _first_sentence(description)
        return {
            "status": "verifiable",
            "verifiable": True,
            "reason": "labels indicate observable behavior should be baselined",
            "verify_scope": scope,
            "confidence": "high",
        }

    signals = _detect_signals(text)
    scope = summary or _first_sentence(description)

    if task_type in ("code", "ui", "feature", "bug"):
        if not signals:
            return {
                "status": "not_verifiable",
                "verifiable": False,
                "reason": f"task_type '{task_type}' but no concrete observable behavior described",
                "verify_scope": "",
                "confidence": "low",
            }
        if len(signals) >= 2 or "reproduction scenario" in signals or "test behavior" in signals:
            confidence = "high"
        else:
            confidence = "medium"
        return {
            "status": "verifiable",
            "verifiable": True,
            "reason": f"task_type '{task_type}' and description indicates observable behavior: {', '.join(signals[:3])}",
            "verify_scope": scope,
            "confidence": confidence,
        }

    # Unknown task type: rely on semantic signals alone
    if signals:
        confidence = "high" if len(signals) >= 2 else "medium"
        return {
            "status": "verifiable",
            "verifiable": True,
            "reason": f"description indicates observable behavior: {', '.join(signals[:3])}",
            "verify_scope": scope,
            "confidence": confidence,
        }

    return {
        "status": "not_verifiable",
        "verifiable": False,
        "reason": "no observable behavior or implementation context found",
        "verify_scope": "",
        "confidence": "low",
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
                    "status": "not_verifiable",
                    "verifiable": False,
                    "reason": f"invalid JSON input: {exc}",
                    "verify_scope": "",
                    "confidence": "low",
                }
            ),
            file=sys.stderr,
        )
        sys.exit(2)

    result = _run(data)
    print(json.dumps(result, indent=2))
    sys.exit(0)
