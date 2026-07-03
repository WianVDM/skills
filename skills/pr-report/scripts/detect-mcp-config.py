#!/usr/bin/env python3
"""Detect an MCP config file from a list of candidate paths.

Accepts candidate paths as command-line arguments or from the PR_REPORT_MCP_CONFIGS
environment variable (paths separated by the OS path separator).

Outputs a JSON object:
    {"found": true, "path": "<path>", "type": "<json|yaml|unknown>"}

If no config is found:
    {"found": false, "path": null, "type": null}

This script only checks file existence and basic structure. It does not parse or
inspect secrets.
"""

import argparse
import json
import os
import sys
from pathlib import Path

DEFAULT_CANDIDATES = [
    ".pi/agent/mcp-config.json",
    ".pi/mcp-config.json",
    ".pi/agent/mcpServers.json",
    ".cursor/mcp.json",
    ".vscode/mcp.json",
    ".aider/mcp.yml",
    "mcp-config.json",
    "mcp-config.yaml",
    "mcp-config.yml",
]


def _split_env_paths(value):
    """Split an environment variable value into a list of paths."""
    if not value:
        return []
    return [p.strip() for p in value.split(os.pathsep) if p.strip()]


def _detect_type(path):
    """Detect the config file type from extension and basic content inspection."""
    suffix = path.suffix.lower()
    if suffix == ".json":
        return "json"
    if suffix in (".yaml", ".yml"):
        return "yaml"

    # Try a lightweight content sniff only for type detection
    try:
        text = path.read_text(encoding="utf-8", errors="ignore").strip()
        if text.startswith("{"):
            return "json"
        if text.startswith("---") or text.startswith("mcpServers:"):
            return "yaml"
    except OSError:
        pass

    return "unknown"


def detect_mcp_config(candidates):
    """Return the first existing candidate path and its detected type."""
    for candidate in candidates:
        path = Path(candidate)
        if not path.is_absolute():
            path = Path.cwd() / path

        if path.exists() and path.is_file():
            return {
                "found": True,
                "path": str(path.resolve()),
                "type": _detect_type(path),
            }

    return {"found": False, "path": None, "type": None}


def main():
    parser = argparse.ArgumentParser(
        description="Detect an MCP config file from candidate paths."
    )
    parser.add_argument(
        "candidates",
        nargs="*",
        help="Candidate config file paths. If omitted, uses default candidates and PR_REPORT_MCP_CONFIGS.",
    )
    args = parser.parse_args()

    candidates = list(args.candidates)
    if not candidates:
        env_candidates = _split_env_paths(os.environ.get("PR_REPORT_MCP_CONFIGS"))
        candidates = env_candidates + DEFAULT_CANDIDATES

    # Remove duplicates while preserving order
    seen = set()
    unique_candidates = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            unique_candidates.append(c)

    result = detect_mcp_config(unique_candidates)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
