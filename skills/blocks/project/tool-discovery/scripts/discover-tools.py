#!/usr/bin/env python3
"""discover-tools.py

Discover and rank available tools for a capability, detect the hosting
platform, and manage the per-project recipe cache.

Operations:
  discover          Return ranked tools for a capability.
  cache-get         Read the cached recipe for a capability.
  cache-put         Write or update the cached recipe for a capability.
  cache-invalidate  Remove the cached recipe for a capability.

Input JSON on stdin:
  {"operation": "discover", "capability": "pr-source", "config_dir": "...",
   "preference": "auto", "probe": false, "project_root": "."}

Output JSON to stdout:
  {"status": "found", "capability": "pr-source", "platform": "github", "tools": [...]}

Notes:
  - The model running in-session sees more than this script (connected MCP
    tools, harness tools). Treat script output as a floor, not a ceiling.
    Prefer model-first detection; use this script as the offline fallback.
  - Auth probes ("probe": true) run `<cli> auth status` for known CLIs.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


# Default ranking order for tool categories when preference is auto.
CATEGORY_ORDER = ["mcp", "cli", "api", "harness", "manual"]

CONFIDENCE_ORDER = {"high": 0, "medium": 1, "low": 2}

# MCP config locations, relative to the user's home directory.
MCP_CONFIG_LOCATIONS_HOME = [
    ".pi/agent/mcp.json",
    ".claude.json",
    ".claude/mcp.json",
    ".cursor/mcp.json",
    ".codeium/windsurf/mcp_config.json",
]

# MCP config locations, relative to the project root.
MCP_CONFIG_LOCATIONS_PROJECT = [
    "mcp.json",
    "mcp.yaml",
    "mcp.yml",
    ".mcp.json",
    ".cursor/mcp.json",
    ".vscode/mcp.json",
    ".pi/agent/mcp.json",
]

# Directories searched for harness skills (relative to home or project).
SKILL_DIRS_HOME = [
    ".pi/agent/skills",
    ".claude/skills",
]
SKILL_DIRS_PROJECT = [
    "skills",
    ".claude/skills",
    ".pi/skills",
]

# Auth probe commands for known CLIs.
CLI_AUTH_PROBES = {
    "gh": ["gh", "auth", "status"],
    "glab": ["glab", "auth", "status"],
}

# Platform host markers, most specific first.
PLATFORM_HOSTS = [
    ("github", ["github.com", "github."]),
    ("gitlab", ["gitlab.com", "gitlab."]),
    ("azure", ["dev.azure.com", "visualstudio.com", "azure."]),
    ("bitbucket", ["bitbucket.org", "bitbucket."]),
]


def _help() -> str:
    return """discover-tools.py — discover tools, detect platform, manage the recipe cache

Operations:
  discover          {"operation":"discover","capability":"pr-source","config_dir":"...","preference":"auto","probe":false,"project_root":"."}
  cache-get         {"operation":"cache-get","capability":"pr-source","config_dir":"..."}
  cache-put         {"operation":"cache-put","capability":"pr-source","config_dir":"...","entry":{...}}
  cache-invalidate  {"operation":"cache-invalidate","capability":"pr-source","config_dir":"..."}
"""


def _default_registry_path() -> Path:
    """Return the path to the bundled capability registry."""
    return Path(__file__).with_name("capability-registry.yaml").resolve()


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


def _find_mcp_configs(config_dir: Path, project_root: Path, scope: str = "all") -> list[Path]:
    """Find MCP config files in the config dir, project root, and (scope=all) harness locations."""
    found = set()
    candidates: list[Path] = []

    if config_dir.exists():
        for directory in (config_dir, config_dir.parent):
            for name in ("mcp.json", "mcp.yaml", "mcp.yml"):
                candidates.append(directory / name)

    if scope == "all":
        home = Path.home()
        candidates.extend(home / rel for rel in MCP_CONFIG_LOCATIONS_HOME)
    candidates.extend(project_root / rel for rel in MCP_CONFIG_LOCATIONS_PROJECT)

    for candidate in candidates:
        try:
            if candidate.is_file():
                found.add(candidate.resolve())
        except OSError:
            continue
    return sorted(found)


def _extract_mcp_tokens(path: Path) -> set[str]:
    """Extract matchable tokens from an MCP config file.

    JSON files with an `mcpServers` object yield server names plus tokens from
    their stringified config. Everything else falls back to full-text
    tokenization (yaml configs, unknown formats).
    """
    text = _read_text(path)
    if not text:
        return set()
    if path.suffix.lower() == ".json":
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = None
        if isinstance(data, dict):
            servers = data.get("mcpServers")
            if isinstance(servers, dict) and servers:
                tokens = set(servers.keys())
                blob = json.dumps(servers).lower()
                tokens.update(re.split(r"[^a-z0-9_-]+", blob))
                return {t for t in tokens if t}
            # JSON without mcpServers: tokenize whole document.
    tokens = set(re.split(r"[^a-z0-9_-]+", text.lower()))
    return {t for t in tokens if t}


def _detect_mcp_tools(config_dir: Path, project_root: Path, scope: str = "all") -> set[str]:
    """Return the set of tokens found across all known MCP config locations."""
    found: set[str] = set()
    for config_path in _find_mcp_configs(config_dir, project_root, scope):
        found.update(_extract_mcp_tokens(config_path))
    return found


def _matches_mcp(tool: dict, mcp_tokens: set[str]) -> tuple[bool, list[str], list[str]]:
    """Check an MCP tool's keywords and identifiers against MCP config tokens.

    Keywords match configured MCP server names; identifiers match concrete
    tool names when the config lists them. Either signal is sufficient.
    """
    keywords = [kw for kw in tool.get("keywords", []) if kw]
    identifiers = [i for i in tool.get("identifiers", []) if i]
    matched_keywords = [kw for kw in keywords if kw.lower() in mcp_tokens]
    matched_identifiers = [i for i in identifiers if i.lower() in mcp_tokens]
    return bool(matched_keywords or matched_identifiers), matched_keywords, matched_identifiers


def _detect_cli_tools(identifiers: list[str]) -> bool:
    """Return True if any of the listed binaries is on PATH."""
    return any(shutil.which(name) for name in identifiers if name)


def _probe_cli_auth(binary: str, timeout: float = 5.0) -> str:
    """Probe a known CLI's auth state. Returns authenticated | not_authenticated | unknown."""
    command = CLI_AUTH_PROBES.get(binary)
    if not command or not shutil.which(binary):
        return "unknown"
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    return "authenticated" if result.returncode == 0 else "not_authenticated"


def _detect_api_tools(identifiers: list[str]) -> bool:
    """Return True if all required env vars are present."""
    if not identifiers:
        return False
    return all(os.environ.get(name) for name in identifiers if name)


def _find_skill_dirs(project_root: Path, scope: str = "all") -> list[Path]:
    """Return existing skill directories across known locations."""
    candidates = []
    if scope == "all":
        home = Path.home()
        candidates.extend(home / rel for rel in SKILL_DIRS_HOME)
    candidates.extend(project_root / rel for rel in SKILL_DIRS_PROJECT)
    found = []
    for directory in candidates:
        try:
            if directory.is_dir():
                found.append(directory.resolve())
        except OSError:
            continue
    return found


def _detect_harness_tool(identifiers: list[str], skills_dirs: list[Path]) -> tuple[bool, str]:
    """Check for a harness skill by looking for {identifier}/SKILL.md in skill dirs.

    Returns (available, detail). When no skill dirs exist at all, the check is
    unverifiable; report available at reduced confidence rather than claiming
    a negative we cannot prove.
    """
    names = [i for i in identifiers if i]
    if not names:
        return False, "harness capability not listed"
    if not skills_dirs:
        return True, "harness skill dirs not found; availability unverifiable"
    for directory in skills_dirs:
        for name in names:
            try:
                matches = list(directory.rglob(f"{name}/SKILL.md"))
            except OSError:
                matches = []
            if matches:
                return True, f"harness skill '{name}' found at {matches[0].parent}"
    return False, f"harness skill {', '.join(names)} not found in known skill dirs"


def _detect_platform(project_root: Path) -> str:
    """Detect the hosting platform from the origin remote URL."""
    if not shutil.which("git"):
        return "unknown"
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(project_root),
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    if result.returncode != 0:
        return "unknown"
    url = result.stdout.strip().lower()
    if not url:
        return "unknown"
    for platform, markers in PLATFORM_HOSTS:
        if any(marker in url for marker in markers):
            return platform
    return "unknown"


def _discover_tool(tool: dict, mcp_tokens: set[str], probe: bool, skills_dirs: list[Path]) -> dict:
    """Return a discovered tool entry with availability, auth state, and detail."""
    category = tool.get("category", "manual")
    name = tool.get("name", "unknown")
    confidence = tool.get("confidence", "low")
    identifiers = tool.get("identifiers", [])
    auth = None

    if category == "mcp":
        available, matched_kw, matched_ids = _matches_mcp(tool, mcp_tokens)
        parts = []
        if matched_kw:
            parts.append(f"MCP keywords {', '.join(matched_kw)} matched")
        if matched_ids:
            parts.append(f"MCP identifiers {', '.join(matched_ids)} matched")
        detail = "; ".join(parts) if parts else "no matching MCP keywords or identifiers detected"
        if available and confidence == "low":
            confidence = "high"
    elif category == "cli":
        available = _detect_cli_tools(identifiers)
        detail = f"binary {', '.join(identifiers)} found on PATH" if available else f"binary {', '.join(identifiers)} not found"
        if available and probe:
            states = {b: _probe_cli_auth(b) for b in identifiers if b}
            auth = next((s for s in states.values() if s == "authenticated"), None)
            if auth is None and states:
                auth = "not_authenticated" if "not_authenticated" in states.values() else "unknown"
            if auth == "authenticated":
                detail += "; authenticated"
                if confidence == "medium":
                    confidence = "high"
            elif auth == "not_authenticated":
                detail += "; installed but not authenticated"
                confidence = "low"
            else:
                detail += "; auth state unknown"
    elif category == "api":
        available = _detect_api_tools(identifiers)
        detail = f"env vars {', '.join(identifiers)} present" if available else f"env vars {', '.join(identifiers)} missing"
    elif category == "harness":
        available, detail = _detect_harness_tool(identifiers, skills_dirs)
        if "unverifiable" in detail and confidence == "high":
            confidence = "medium"
    else:
        # manual fallback
        available = True
        detail = "user-provided fallback"

    entry = {
        "name": name,
        "category": category,
        "available": available,
        "confidence": confidence if available else "low",
        "detail": detail,
    }
    if auth is not None:
        entry["auth"] = auth
    return entry


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

    config_dir = Path(data.get("config_dir", ".agents/config")).resolve()
    project_root = Path(data.get("project_root", ".")).resolve()
    preference = data.get("preference") or _load_preference(config_dir, capability)
    probe = bool(data.get("probe", False))
    scope = str(data.get("search_scope", "all"))
    if scope not in ("all", "project"):
        scope = "all"
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

    mcp_tokens = _detect_mcp_tools(config_dir, project_root, scope)
    skills_dirs = _find_skill_dirs(project_root, scope)
    discovered = [_discover_tool(tool, mcp_tokens, probe, skills_dirs) for tool in capability_def.get("tools", [])]

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
    platform = _detect_platform(project_root)

    if not ranked:
        return {
            "status": "not_found",
            "capability": capability,
            "platform": platform,
            "tools": [],
        }

    return {
        "status": "found",
        "capability": capability,
        "config_dir": str(config_dir),
        "platform": platform,
        "tools": ranked,
    }


def _cache_path(config_dir: Path) -> Path:
    return config_dir / "tool-recipes.yaml"


def _load_cache(config_dir: Path) -> dict:
    path = _cache_path(config_dir)
    if not path.exists():
        return {}
    try:
        data = yaml.safe_load(_read_text(path)) or {}
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def _write_cache(config_dir: Path, cache: dict) -> None:
    config_dir.mkdir(parents=True, exist_ok=True)
    path = _cache_path(config_dir)
    path.write_text(yaml.safe_dump(cache, sort_keys=False), encoding="utf-8")


def _do_cache_get(data: dict) -> dict:
    capability = data.get("capability")
    if not capability:
        return {"status": "error", "errors": ["capability is required"]}
    config_dir = Path(data.get("config_dir", ".agents/config")).resolve()
    entry = _load_cache(config_dir).get(capability)
    if entry is None:
        return {"status": "not_found", "capability": capability}
    return {"status": "found", "capability": capability, "entry": entry}


def _do_cache_put(data: dict) -> dict:
    capability = data.get("capability")
    entry = data.get("entry")
    if not capability or not isinstance(entry, dict):
        return {"status": "error", "errors": ["capability and entry (object) are required"]}
    config_dir = Path(data.get("config_dir", ".agents/config")).resolve()
    cache = _load_cache(config_dir)
    cache[capability] = entry
    try:
        _write_cache(config_dir, cache)
    except OSError as exc:
        return {"status": "error", "errors": [f"failed to write cache: {exc}"]}
    return {"status": "written", "capability": capability, "path": str(_cache_path(config_dir))}


def _do_cache_invalidate(data: dict) -> dict:
    capability = data.get("capability")
    if not capability:
        return {"status": "error", "errors": ["capability is required"]}
    config_dir = Path(data.get("config_dir", ".agents/config")).resolve()
    cache = _load_cache(config_dir)
    removed = cache.pop(capability, None)
    try:
        _write_cache(config_dir, cache)
    except OSError as exc:
        return {"status": "error", "errors": [f"failed to write cache: {exc}"]}
    return {"status": "invalidated" if removed is not None else "not_found", "capability": capability}


def _run(data: dict) -> dict:
    operation = data.get("operation")
    if operation == "discover":
        return _do_discover(data)
    if operation == "cache-get":
        return _do_cache_get(data)
    if operation == "cache-put":
        return _do_cache_put(data)
    if operation == "cache-invalidate":
        return _do_cache_invalidate(data)
    return {"status": "error", "errors": [f"unknown operation: {operation}"]}


def _main() -> int:
    if any(arg in ("-h", "--help") for arg in sys.argv[1:]):
        print(_help())
        return 0

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(json.dumps({"status": "error", "errors": [f"invalid JSON input: {exc}"]}))
        return 2

    if not isinstance(data, dict):
        print(json.dumps({"status": "error", "errors": ["input must be a JSON object"]}))
        return 2

    try:
        result = _run(data)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"status": "error", "errors": [f"runtime failure: {exc}"]}))
        return 1
    print(json.dumps(result, indent=2))
    ok_statuses = ("found", "written", "invalidated")
    return 0 if result["status"] in ok_statuses else 1


if __name__ == "__main__":
    sys.exit(_main())
