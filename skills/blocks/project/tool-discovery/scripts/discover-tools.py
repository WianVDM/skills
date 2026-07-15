#!/usr/bin/env python3
"""discover-tools.py

Discover and rank available tools for a given capability.

Operations:
  discover  Return ranked tools for a capability.

Input JSON on stdin:
  {"operation": "discover", "capability": "pr-source", "context_dir": "...", "config_dir": "...", "preference": "auto"}

Output JSON to stdout:
  {"status": "found", "capability": "pr-source", "tools": [...]}
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml


# Default ranking order for tool categories when preference is auto.
CATEGORY_ORDER = ["mcp", "cli", "api", "harness", "manual"]

CONFIDENCE_ORDER = {"high": 0, "medium": 1, "low": 2}


def _help() -> str:
    return """discover-tools.py — discover available tools for a capability

Input JSON (stdin):
  {"operation": "discover", "capability": "pr-source", "context_dir": "...", "config_dir": "...", "preference": "auto"}

Output JSON (stdout):
  {"status": "found", "capability": "pr-source", "tools": [...]}
"""


def _default_registry_path() -> Path:
    """Return the path to the bundled capability registry."""
    return Path(__file__).with_name("capability-registry.yaml").resolve()


def _find_mcp_configs(config_dir: Path) -> list[Path]:
    """Find MCP config files under the provided config directory."""
    found = set()
    if not config_dir.exists():
        return []
    for directory in (config_dir, config_dir.parent):
        if not directory.exists():
            continue
        for name in ("mcp.json", "mcp.yaml", "mcp.yml"):
            candidate = directory / name
            if candidate.is_file():
                found.add(candidate.resolve())
    return sorted(found)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _load_registry(path: Path) -> dict:
    text = _read_text(path)
    if not text:
        return {"capabilities": {}}
    try:
        data = yaml.safe_load(text) or {"capabilities": {}}
    except yaml.YAMLError as exc:
        return {"error": f"invalid registry YAML: {exc}"}
    return data


def _detect_mcp_tools(config_dir: Path) -> set[str]:
    """Return a set of keywords found in MCP config files."""
    found = set()
    for config_path in _find_mcp_configs(config_dir):
        text = _read_text(config_path).lower()
        # Use a simple tokenizer that splits on common delimiters.
        tokens = set(re.split(r"[^a-z0-9_-]+", text))
        found.update(tokens)
    return found


def _matches_mcp(tool: dict, mcp_tokens: set[str]) -> tuple[bool, list[str]]:
    """Check whether an MCP tool's keywords are present in MCP config."""
    keywords = tool.get("keywords", tool.get("identifiers", []))
    matched = [kw for kw in keywords if kw.lower() in mcp_tokens]
    return bool(matched), matched


def _detect_cli_tools(identifiers: list[str]) -> bool:
    """Return True if any of the listed binaries is on PATH."""
    return any(shutil.which(name) for name in identifiers if name)


def _detect_api_tools(identifiers: list[str]) -> bool:
    """Return True if all required env vars are present."""
    if not identifiers:
        return False
    return all(os.environ.get(name) for name in identifiers if name)


def _detect_harness_tool(identifiers: list[str]) -> bool:
    """Harness tools cannot be detected from a script; assume available if listed."""
    return bool(identifiers)


def _discover_tool(tool: dict, mcp_tokens: set[str]) -> dict:
    """Return a discovered tool entry with availability and detail."""
    category = tool.get("category", "manual")
    name = tool.get("name", "unknown")
    confidence = tool.get("confidence", "low")
    identifiers = tool.get("identifiers", [])

    if category == "mcp":
        available, matched = _matches_mcp(tool, mcp_tokens)
        detail = f"MCP keywords {', '.join(matched)} matched" if matched else "no matching MCP keywords detected"
        if matched and confidence == "low":
            confidence = "high"
    elif category == "cli":
        available = _detect_cli_tools(identifiers)
        detail = f"binary {', '.join(identifiers)} found on PATH" if available else f"binary {', '.join(identifiers)} not found"
    elif category == "api":
        available = _detect_api_tools(identifiers)
        detail = f"env vars {', '.join(identifiers)} present" if available else f"env vars {', '.join(identifiers)} missing"
    elif category == "harness":
        available = _detect_harness_tool(identifiers)
        detail = "harness capability available" if available else "harness capability not listed"
    else:
        # manual fallback
        available = True
        detail = "user-provided fallback"

    return {
        "name": name,
        "category": category,
        "available": available,
        "confidence": confidence if available else "low",
        "detail": detail,
    }


def _rank_tools(tools: list[dict], preference: str) -> list[dict]:
    """Rank tools by preference, category order, and confidence."""
    available = [t for t in tools if t.get("available")]

    def sort_key(tool: dict) -> tuple:
        category = tool.get("category", "manual")
        confidence = tool.get("confidence", "low")
        # If preference matches the tool category, put it first.
        preferred = 0 if preference != "auto" and category == preference else 1
        category_rank = CATEGORY_ORDER.index(category) if category in CATEGORY_ORDER else 99
        confidence_rank = CONFIDENCE_ORDER.get(confidence, 99)
        return (preferred, category_rank, confidence_rank, tool.get("name", ""))

    return sorted(available, key=sort_key)


def _load_preference(config_dir: Path, capability: str) -> str:
    """Load preference from tool-discovery.yaml if present."""
    config_path = config_dir / "tool-discovery.yaml"
    if not config_path.exists():
        return "auto"
    try:
        data = yaml.safe_load(_read_text(config_path)) or {}
    except yaml.YAMLError:
        return "auto"
    if not isinstance(data, dict):
        return "auto"
    return str(data.get("tool-discovery", {}).get("tools", {}).get(capability, {}).get("provider", "auto"))


def _do_discover(data: dict) -> dict:
    capability = data.get("capability")
    if not capability:
        return {"status": "error", "errors": ["capability is required"]}

    context_dir = Path(data.get("context_dir", ".agents/context")).resolve()
    config_dir = Path(data.get("config_dir", ".agents/config")).resolve()
    preference = data.get("preference") or _load_preference(config_dir, capability)
    registry_path = Path(data.get("registry", _default_registry_path())).resolve()

    registry = _load_registry(registry_path)
    if "error" in registry:
        return {"status": "error", "errors": [registry["error"]]}

    capability_def = registry.get("capabilities", {}).get(capability)
    if not capability_def:
        return {
            "status": "error",
            "errors": [f"capability '{capability}' not found in registry"],
        }

    mcp_tokens = _detect_mcp_tools(config_dir)
    discovered = [_discover_tool(tool, mcp_tokens) for tool in capability_def.get("tools", [])]

    # Ensure manual fallback exists.
    if not any(t.get("category") == "manual" for t in discovered):
        discovered.append({
            "name": "manual",
            "category": "manual",
            "available": True,
            "confidence": "low",
            "detail": "user-provided fallback",
        })

    ranked = _rank_tools(discovered, preference)

    if not ranked:
        return {
            "status": "not_found",
            "capability": capability,
            "tools": [],
        }

    return {
        "status": "found",
        "capability": capability,
        "context_dir": str(context_dir),
        "config_dir": str(config_dir),
        "tools": ranked,
    }


def _run(data: dict) -> dict:
    operation = data.get("operation")
    if operation == "discover":
        return _do_discover(data)
    return {"status": "error", "errors": [f"unknown operation: {operation}"]}


def _main() -> int:
    if any(arg in ("-h", "--help") for arg in sys.argv[1:]):
        print(_help())
        return 0

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(
            json.dumps({"status": "error", "errors": [f"invalid JSON input: {exc}"]}),
            file=sys.stderr,
        )
        return 2

    result = _run(data)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] in ("found",) else 1


if __name__ == "__main__":
    sys.exit(_main())
