#!/usr/bin/env python3
"""Resolve issue-tracker credentials from environment variables and config.

Reads JSON from stdin:
  {"tracker": "jira", "tracker_config": {"token_env": "JIRA_API_TOKEN", ...}}

Writes JSON to stdout:
  {"status": "ready"|"missing"|"error", "credentials": {...}, "missing": []}

Secret token values are masked as "***" in the output. This script never
writes secrets to files and never prompts the user.
"""

import json
import os
import sys


def _help() -> str:
    return """resolve-tracker-credentials.py — resolve tracker credentials from env vars

Input JSON (stdin):
  {"tracker": "jira", "tracker_config": {"token_env": "JIRA_API_TOKEN", ...}}

Output JSON (stdout):
  {"status": "ready"|"missing"|"error", "credentials": {...}, "missing": ["..."]}

Token values are masked as "***" in the output.
"""


def _run(data: dict) -> dict:
    tracker = data.get("tracker")
    tracker_config = data.get("tracker_config")

    if not tracker:
        return {
            "status": "error",
            "credentials": {},
            "missing": [],
        }

    if not isinstance(tracker_config, dict):
        return {
            "status": "error",
            "credentials": {},
            "missing": [],
        }

    credentials = {}
    missing = []

    for key, value in tracker_config.items():
        if key.endswith("_env"):
            if not isinstance(value, str) or not value:
                missing.append(str(value) if value else key)
                credentials[key[:-4]] = None
                continue

            env_value = os.environ.get(value)
            if env_value is None or env_value == "":
                missing.append(value)
                credentials[key[:-4]] = None
                continue

            resolved_key = key[:-4]
            if resolved_key.lower() == "token" or "token" in resolved_key.lower():
                credentials[resolved_key] = "***"
            else:
                credentials[resolved_key] = env_value
        else:
            credentials[key] = value

    if missing:
        return {
            "status": "missing",
            "credentials": credentials,
            "missing": missing,
        }

    return {
        "status": "ready",
        "credentials": credentials,
        "missing": [],
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
                    "status": "error",
                    "credentials": {},
                    "missing": [],
                }
            ),
            file=sys.stderr,
        )
        sys.exit(2)

    result = _run(data)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] != "error" else 1)
