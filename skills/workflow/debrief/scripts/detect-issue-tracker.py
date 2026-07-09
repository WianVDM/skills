#!/usr/bin/env python3
"""Detect available issue trackers for the current project.

Reads JSON from stdin: {"cwd": "<path>"}
Writes JSON to stdout:
  {
    "trackers": [
      {"name": "jira", "available": true, "source": "mcp|env|config", "confidence": "high|medium|low", "detail": "..."},
      ...
    ]
  }

The manual tracker is always reported as available with low confidence.
The script is read-only, deterministic, and non-interactive.
"""

import json
import os
import sys
from pathlib import Path

MCP_PATHS = [
    ".cursor/mcp.json",
    ".vscode/mcp.json",
    ".claude/mcp.json",
    ".pi/mcp.json",
    ".pi/config/mcp.json",
    "mcp.json",
    ".agents/config/mcp.json",
    "agents/config/mcp.json",
    ".cursor/mcp.yaml",
    ".vscode/mcp.yaml",
    ".claude/mcp.yaml",
    ".pi/mcp.yaml",
    ".pi/config/mcp.yaml",
    "mcp.yaml",
    ".agents/config/mcp.yaml",
    "agents/config/mcp.yaml",
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


def _help() -> str:
    return """detect-issue-tracker.py — detect available issue trackers

Input JSON (stdin):
  {"cwd": "<working-directory>"}

Output JSON (stdout):
  {"trackers": [{"name": "...", "available": true|false, "source": "...", "confidence": "...", "detail": "..."}]}
"""


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _find_mcp_configs(cwd: Path) -> list:
    found = []
    for rel in MCP_PATHS:
        path = cwd / rel
        if path.exists():
            found.append(path.resolve())
    return found


def _detect_mcp_servers(cwd: Path) -> dict:
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
    results = {name: [] for name in ENV_VARS}
    for tracker, var_groups in ENV_VARS.items():
        for group in var_groups:
            if all(os.environ.get(var) for var in group):
                results[tracker].extend(group)
    return results


def _run(data: dict) -> dict:
    cwd = data.get("cwd", str(Path.cwd()))
    cwd_path = Path(cwd).resolve()

    mcp_results = _detect_mcp_servers(cwd_path)
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

    trackers.append({
        "name": "manual",
        "available": True,
        "source": "config",
        "confidence": "low",
        "detail": "user-provided fallback",
    })

    return {"trackers": trackers}


if __name__ == "__main__":
    if any(arg in ("-h", "--help") for arg in sys.argv[1:]):
        print(_help())
        sys.exit(0)

    try:
        data = json.load(sys.stdin)
    except Exception as exc:
        print(
            json.dumps({"error": f"invalid JSON input: {exc}"}),
            file=sys.stderr,
        )
        sys.exit(2)

    try:
        result = _run(data)
    except Exception as exc:
        print(
            json.dumps({"error": str(exc)}),
            file=sys.stderr,
        )
        sys.exit(1)

    print(json.dumps(result, indent=2))
    sys.exit(0)
