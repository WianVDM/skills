#!/usr/bin/env python3
"""Detect available issue trackers for the current project.

Inspects the project and environment to decide which issue trackers are
viable: jira, github, linear, or manual.

Checks performed:
    - MCP server configurations (mcp.json or mcp.yaml) containing known tracker servers.
    - Environment variables:
        JIRA_URL + JIRA_USERNAME + JIRA_API_TOKEN
        GITHUB_TOKEN
        LINEAR_API_KEY

Outputs JSON:
    {
      "trackers": [
        {
          "name": "jira|github|linear|manual",
          "available": true|false,
          "source": "mcp|env|config",
          "confidence": "high|medium|low"
        }
      ]
    }

If no tracker is found, "manual" is still reported as available with low confidence.

The script is read-only, deterministic, and safe to run in any project.
"""

import argparse
import json
import os
import sys
from pathlib import Path

MCP_PATHS = [
    ".cursor/mcp.json",
    ".vscode/mcp.json",
    ".claude/mcp.json",
    ".pi/mcp.json",
    "mcp.json",
    ".agents/config/mcp.json",
    ".cursor/mcp.yaml",
    ".vscode/mcp.yaml",
    ".claude/mcp.yaml",
    ".pi/mcp.yaml",
    "mcp.yaml",
    ".agents/config/mcp.yaml",
]

MCP_KEYWORDS = {
    "jira": ["jira"],
    "github": ["github"],
    "linear": ["linear"],
}

ENV_VARS = {
    "jira": [("JIRA_URL", "JIRA_USERNAME", "JIRA_API_TOKEN")],
    "github": [("GITHUB_TOKEN",)],
    "linear": [("LINEAR_API_KEY",)],
}


def _read_text(path: Path) -> str:
    """Read text safely, returning an empty string on failure."""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _find_mcp_configs(cwd: Path) -> list:
    """Return a list of absolute paths for existing MCP config files."""
    found = []
    for rel in MCP_PATHS:
        path = cwd / rel
        if path.exists():
            found.append(path.resolve())
    return found


def _detect_mcp_servers(cwd: Path) -> dict:
    """Detect tracker names mentioned in MCP config files."""
    results = {name: [] for name in MCP_KEYWORDS}
    for config_path in _find_mcp_configs(cwd):
        text = _read_text(config_path).lower()
        for tracker, keywords in MCP_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    results[tracker].append(str(config_path))
                    break
    return results


def _detect_env_vars() -> dict:
    """Detect tracker availability from environment variables."""
    results = {name: [] for name in ENV_VARS}
    for tracker, var_groups in ENV_VARS.items():
        for group in var_groups:
            if all(os.environ.get(var) for var in group):
                results[tracker].extend(group)
    return results


def detect_trackers(cwd: Path = None) -> list:
    """Return a list of tracker result dicts."""
    if cwd is None:
        cwd = Path.cwd()

    mcp_results = _detect_mcp_servers(cwd)
    env_results = _detect_env_vars()

    trackers = []
    for name in ("jira", "github", "linear"):
        mcp_sources = mcp_results.get(name, [])
        env_sources = env_results.get(name, [])

        if mcp_sources and env_sources:
            available = True
            source = "mcp"
            confidence = "high"
            source_detail = f"MCP config and env vars: {', '.join(sorted(set(env_sources)))}"
        elif mcp_sources:
            available = True
            source = "mcp"
            confidence = "high"
            source_detail = f"MCP config: {', '.join(sorted(set(mcp_sources)))}"
        elif env_sources:
            available = True
            source = "env"
            confidence = "medium"
            source_detail = f"env vars: {', '.join(sorted(set(env_sources)))}"
        else:
            available = False
            source = "config"
            confidence = "low"
            source_detail = "no MCP config or env vars detected"

        trackers.append({
            "name": name,
            "available": available,
            "source": source,
            "confidence": confidence,
            "detail": source_detail,
        })

    # Manual fallback is always available with low confidence.
    trackers.append({
        "name": "manual",
        "available": True,
        "source": "config",
        "confidence": "low",
        "detail": "user-provided fallback",
    })

    return trackers


def main():
    parser = argparse.ArgumentParser(
        description="Detect available issue trackers for the current project."
    )
    parser.add_argument(
        "--cwd",
        help="Override the working directory to inspect. Default: current directory.",
    )
    args = parser.parse_args()

    cwd = Path(args.cwd).resolve() if args.cwd else Path.cwd()
    try:
        trackers = detect_trackers(cwd)
        print(json.dumps({"trackers": trackers}, indent=2))
        return 0
    except Exception as exc:  # pragma: no cover - safety net
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
