#!/usr/bin/env python3
"""Calculate an overall confidence score from assumptions and unresolved issues.

Reads JSON from stdin:
  {
    "assumptions": [{"text": "...", "status": "holds"|"challenged"|"unresolved"}, ...],
    "contradictions": ["...", ...],
    "unresolved_ambiguities": ["...", ...],
    "config": {
      "green_threshold": 85,
      "yellow_threshold": 60,
      "penalty_challenged": 10,
      "penalty_unresolved": 10,
      "penalty_contradiction": 15,
      "penalty_ambiguity": 5
    }
  }

Writes JSON to stdout:
  {"confidence_pct": 65, "confidence_level": "Yellow", "confidence_gap": ["..."]}
"""

import json
import sys


def _help() -> str:
    return """calculate-confidence.py — compute confidence score from assumptions and issues

Input JSON (stdin):
  {
    "assumptions": [{"text": "...", "status": "holds"|"challenged"|"unresolved"}],
    "contradictions": ["..."],
    "unresolved_ambiguities": ["..."],
    "config": {"green_threshold": 85, "yellow_threshold": 60,
               "penalty_challenged": 10, "penalty_unresolved": 10,
               "penalty_contradiction": 15, "penalty_ambiguity": 5}
  }

Output JSON (stdout):
  {"confidence_pct": 0-100, "confidence_level": "Green"|"Yellow"|"Red", "confidence_gap": ["..."]}
"""


def _run(data: dict) -> dict:
    assumptions = data.get("assumptions", []) or []
    contradictions = data.get("contradictions", []) or []
    ambiguities = data.get("unresolved_ambiguities", []) or []
    config = data.get("config", {}) or {}

    defaults = {
        "green_threshold": 85,
        "yellow_threshold": 60,
        "penalty_challenged": 10,
        "penalty_unresolved": 10,
        "penalty_contradiction": 15,
        "penalty_ambiguity": 5,
        "penalty_inconclusive": 5,
    }

    cfg = {**defaults, **config}

    try:
        green_threshold = int(cfg["green_threshold"])
        yellow_threshold = int(cfg["yellow_threshold"])
        penalty_challenged = int(cfg["penalty_challenged"])
        penalty_unresolved = int(cfg["penalty_unresolved"])
        penalty_contradiction = int(cfg["penalty_contradiction"])
        penalty_ambiguity = int(cfg["penalty_ambiguity"])
        penalty_inconclusive = int(cfg["penalty_inconclusive"])
    except (KeyError, TypeError, ValueError):
        return {
            "confidence_pct": 0,
            "confidence_level": "Red",
            "confidence_gap": ["Invalid confidence configuration"],
        }

    if green_threshold <= yellow_threshold:
        return {
            "confidence_pct": 0,
            "confidence_level": "Red",
            "confidence_gap": ["green_threshold must be greater than yellow_threshold"],
        }

    confidence = 100
    gap = []

    for assumption in assumptions:
        if isinstance(assumption, dict):
            text = assumption.get("text", "")
            status = assumption.get("status", "")
        else:
            text = str(assumption)
            status = ""

        if status == "challenged":
            confidence -= penalty_challenged
            gap.append(f"Assumption '{text}' is challenged.")
        elif status == "unresolved":
            confidence -= penalty_unresolved
            gap.append(f"Assumption '{text}' is unresolved.")
        elif status == "inconclusive":
            confidence -= penalty_inconclusive
            gap.append(f"Assumption '{text}' is inconclusive.")

    for contradiction in contradictions:
        confidence -= penalty_contradiction
        gap.append(f"Contradiction: {contradiction}")

    for ambiguity in ambiguities:
        confidence -= penalty_ambiguity
        gap.append(f"Unresolved ambiguity: {ambiguity}")

    confidence = max(0, min(100, confidence))
    if confidence == 100 and gap:
        confidence = 99

    if confidence >= green_threshold:
        level = "Green"
    elif confidence >= yellow_threshold:
        level = "Yellow"
    else:
        level = "Red"

    return {
        "confidence_pct": confidence,
        "confidence_level": level,
        "confidence_gap": gap,
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
                    "confidence_pct": 0,
                    "confidence_level": "Red",
                    "confidence_gap": [f"invalid JSON input: {exc}"],
                }
            ),
            file=sys.stderr,
        )
        sys.exit(2)

    result = _run(data)
    print(json.dumps(result, indent=2))
    sys.exit(0)
