#!/usr/bin/env python3
"""Detect available issue trackers for the current project.

Reads JSON from stdin: {"cwd": "<path>", "config_dir": "<path>"}
  - cwd is required; it is the working directory for the project.
  - config_dir is required; the conductor must provide it from detect-project-context.

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
from pathlib import Path
from typing import Optional

MCP_KEYWORDS = {
    "jira": ["jira"],
    "github": ["github"],
    "linear": ["linear"],
}

ENV_VARS = {
    "jira": [("JIRA_SERVER_URL", "JIRA_USERNAME", "JIRA_API_TOKEN")],
    "github": [("GITHUB_TOKEN",)],
    "linear": [("LINEAR_API_TOKEN",)],
}


def _help() -> str:
    return """detect-issue-tracker.py — detect available issue trackers

Input JSON (stdin):
  {"cwd": "<working-directory>", "config_dir": "<config-directory>"}

  - cwd is required; it is the working directory for the project.
  - config_dir is required; the conductor must provide it from detect-project-context.

Output JSON (stdout):
  {"trackers": [{"name": "...", "available": true|false, "source": "...", "confidence": "...", "detail": "..."}]}

The config_dir is used to locate MCP config files (mcp.json / mcp.yaml).
"""


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _find_mcp_configs(config_dir: Optional[Path] = None) -> list[Path]:
    """Find MCP config files under the provided config directory.

    The caller is responsible for discovering the project config directory
    (e.g. via detect-project-context) and passing it as config_dir.
    """
    if config_dir is None or not config_dir.exists():
        return []

    found = set()
    # Search the config directory and its parent (e.g., .agents/config and .agents).
    for directory in (config_dir, config_dir.parent):
        if not directory.exists():
            continue
        for name in ("mcp.json", "mcp.yaml", "mcp.yml"):
            candidate = directory / name
            if candidate.is_file():
                found.add(candidate.resolve())

    return sorted(found)


def _detect_mcp_servers(config_dir: Optional[Path] = None) -> dict:
    results = {name: [] for name in MCP_KEYWORDS}
    for config_path in _find_mcp_configs(config_dir):
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
    config_dir = data.get("config_dir")
    if not config_dir:
        return {"error": "config_dir is required; the conductor must provide it from detect-project-context"}
    config_dir_path = Path(config_dir).resolve()

    mcp_results = _detect_mcp_servers(config_dir_path)
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
    import sys

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
