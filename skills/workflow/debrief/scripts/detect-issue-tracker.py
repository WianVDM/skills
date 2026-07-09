#!/usr/bin/env python3
"""Detect available issue trackers for the current project.

Reads JSON from stdin: {"cwd": "<path>", "config_dir": "<path>"}
  - cwd is required; it is the working directory for the project.
  - config_dir is optional; when provided, it overrides detected paths.

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
import subprocess
import sys
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
  {"cwd": "<working-directory>", "config_dir": "<optional-config-directory>"}

Output JSON (stdout):
  {"trackers": [{"name": "...", "available": true|false, "source": "...", "confidence": "...", "detail": "..."}]}

The optional config_dir is used to locate MCP config files (mcp.json / mcp.yaml).
When omitted, the script discovers the config directory via detect-project-context.
"""


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _detect_config_dirs(cwd: Path) -> list[Path]:
    """Discover candidate config directories using detect-project-context.

    Falls back to the current working directory if detection is unavailable.
    """
    detect_script = (
        Path(__file__).resolve().parents[3]
        / "core"
        / "detect-project-context"
        / "scripts"
        / "detect-project-context.py"
    )
    if not detect_script.is_file():
        return [cwd]

    try:
        result = subprocess.run(
            [
                sys.executable,
                str(detect_script),
                "--start",
                str(cwd),
                "--json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            dirs = []
            for key in ("recommended_config_dir", "config_dir_candidates"):
                value = data.get(key)
                if not value:
                    continue
                if isinstance(value, list):
                    dirs.extend(value)
                else:
                    dirs.append(value)
            if dirs:
                return [Path(d) for d in dirs]
    except Exception:
        pass

    return [cwd]


def _find_mcp_configs(cwd: Path, config_dir: Optional[Path] = None) -> list[Path]:
    """Find MCP config files without hardcoding harness-specific paths.

    Searches the caller-supplied config directory, or the directories
    discovered by detect-project-context, for mcp.json / mcp.yaml files.
    """
    search_roots = [config_dir] if config_dir else _detect_config_dirs(cwd)
    found = set()

    for root in search_roots:
        if not root.exists():
            continue
        # Search the config directory and its parent (e.g., .agents/config and .agents).
        for directory in (root, root.parent):
            if not directory.exists():
                continue
            for name in ("mcp.json", "mcp.yaml", "mcp.yml"):
                candidate = directory / name
                if candidate.is_file():
                    found.add(candidate.resolve())

    return sorted(found)


def _detect_mcp_servers(cwd: Path, config_dir: Optional[Path] = None) -> dict:
    results = {name: [] for name in MCP_KEYWORDS}
    for config_path in _find_mcp_configs(cwd, config_dir):
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
    config_dir = data.get("config_dir")
    config_dir_path = Path(config_dir).resolve() if config_dir else None

    mcp_results = _detect_mcp_servers(cwd_path, config_dir_path)
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
