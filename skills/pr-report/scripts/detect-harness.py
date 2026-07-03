#!/usr/bin/env python3
"""Detect the current agent harness from environment variables or known config files.

Outputs a JSON object describing the detected harness:
    {"harness": "<name>", "confidence": "high|medium|low", "source": "<description>"}

If no harness can be detected, outputs:
    {"harness": "unknown"}

This script is read-only and safe to run in any project. It never modifies files
or asks for user input.
"""

import json
import os
import sys
from pathlib import Path


def _detect_from_env():
    """Check environment variables that indicate a specific harness."""
    env = os.environ

    # Direct harness identifiers
    if env.get("PI_CODING_AGENT") or env.get("PI_AGENT_NAME") or env.get("PI_VERSION"):
        return "pi", "high", "PI_* environment variables"

    if env.get("CLAUDE_CODE") or env.get("CLAUDE_CODE_VERSION"):
        return "claude-code", "high", "CLAUDE_CODE environment variable"

    if env.get("CURSOR_AGENT") or env.get("CURSOR_TRACE_ID"):
        return "cursor", "high", "CURSOR_AGENT environment variable"

    if env.get("COPILOT_AGENT") or env.get("GITHUB_COPILOT"):
        return "github-copilot", "high", "GITHUB_COPILOT environment variable"

    if env.get("AIDER_CHAT") or env.get("AIDER_VERSION"):
        return "aider", "high", "AIDER_* environment variable"

    # Generic agent indicators with lower confidence
    if env.get("AGENT_HARNESS") or env.get("AGENT_NAME"):
        return env.get("AGENT_HARNESS") or env.get("AGENT_NAME"), "medium", "AGENT_* environment variable"

    return None


def _detect_from_config_files():
    """Check known config files that indicate a specific harness."""
    cwd = Path.cwd()

    configs = [
        (cwd / ".pi" / "agent" / "AGENTS.md", "pi", "high"),
        (cwd / ".pi" / "config.yaml", "pi", "medium"),
        (cwd / ".claude" / "CLAUDE.md", "claude-code", "high"),
        (cwd / ".cursor" / "rules", "cursor", "medium"),
        (cwd / ".cursor" / ".cursorrules", "cursor", "medium"),
        (cwd / ".github" / "copilot-instructions.md", "github-copilot", "medium"),
        (cwd / ".aider" / "config.yml", "aider", "medium"),
        (cwd / ".aider.conf.yml", "aider", "medium"),
    ]

    for path, harness, confidence in configs:
        if path.exists():
            return harness, confidence, str(path)

    return None


def detect_harness():
    """Return a tuple of (harness, confidence, source) or None."""
    env_result = _detect_from_env()
    if env_result:
        return env_result

    config_result = _detect_from_config_files()
    if config_result:
        return config_result

    return None


def main():
    result = detect_harness()
    if result is None:
        output = {"harness": "unknown"}
    else:
        harness, confidence, source = result
        output = {"harness": harness, "confidence": confidence, "source": source}

    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
