#!/usr/bin/env python3
"""
Tests for discover-tools.py.

Regression guards:
- the capabilities requested by pr-review (`reviews`, `changed-files`,
  `checkout`) must resolve from the bundled registry;
- MCP matching must use both `keywords` (server names) and `identifiers`
  (tool names) found in MCP config files;
- unknown capabilities must exit 1 and invalid JSON must exit 2, both with
  the {"status": "error", "errors": [...]} envelope on stdout.

No network calls are made; MCP configs are faked on disk.

Run with:
    python -m pytest skills/blocks/project/tool-discovery/scripts/tests/
    python skills/blocks/project/tool-discovery/scripts/tests/test_discover_tools.py
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "discover-tools.py"


def run(payload: dict = None, raw: str = None):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=raw if raw is not None else json.dumps(payload),
        capture_output=True,
        text=True,
    )
    try:
        return proc.returncode, json.loads(proc.stdout)
    except json.JSONDecodeError:
        return proc.returncode, {"_raw": proc.stdout + proc.stderr}


def config_dir(tmp_path: Path, mcp_config: dict = None) -> Path:
    """Create an isolated config dir, optionally with a fake mcp.json."""
    cfg = tmp_path / "cfg"
    cfg.mkdir(exist_ok=True)
    if mcp_config is not None:
        (cfg / "mcp.json").write_text(json.dumps(mcp_config), encoding="utf-8")
    return cfg


# ---------------------------------------------------------------------------
# bundled registry covers the capabilities pr-review requests
# ---------------------------------------------------------------------------

def test_reviews_capability_resolves(tmp_path):
    code, out = run({"operation": "discover", "capability": "reviews", "config_dir": str(config_dir(tmp_path))})
    assert code == 0
    assert out["status"] == "found"
    assert any(t["name"] == "manual" for t in out["tools"])


def test_changed_files_capability_resolves(tmp_path):
    code, out = run({"operation": "discover", "capability": "changed-files", "config_dir": str(config_dir(tmp_path))})
    assert code == 0
    assert out["status"] == "found"
    assert any(t["name"] == "manual" for t in out["tools"])


def test_checkout_capability_resolves(tmp_path):
    code, out = run({"operation": "discover", "capability": "checkout", "config_dir": str(config_dir(tmp_path))})
    assert code == 0
    assert out["status"] == "found"
    assert any(t["name"] == "git-worktree-inspector" for t in out["tools"])


# ---------------------------------------------------------------------------
# MCP matching via keywords and identifiers
# ---------------------------------------------------------------------------

def test_mcp_keyword_matching(tmp_path):
    cfg = config_dir(tmp_path, {"mcpServers": {"github": {"command": "docker"}}})
    code, out = run({"operation": "discover", "capability": "pr-source", "config_dir": str(cfg)})
    assert code == 0
    mcp = next(t for t in out["tools"] if t["category"] == "mcp")
    assert mcp["name"] == "github-mcp"
    assert mcp["available"] is True
    assert mcp["confidence"] == "high"
    assert mcp["detail"] == "MCP keywords github matched"


def test_mcp_identifier_matching(tmp_path):
    cfg = config_dir(tmp_path, {
        "mcpServers": {"review-tools": {"command": "run", "args": ["github_get_pull_request_reviews"]}},
    })
    code, out = run({"operation": "discover", "capability": "reviews", "config_dir": str(cfg)})
    assert code == 0
    mcp = next(t for t in out["tools"] if t["category"] == "mcp")
    assert mcp["name"] == "github-mcp"
    assert mcp["available"] is True
    assert mcp["detail"] == "MCP identifiers github_get_pull_request_reviews matched"


def test_mcp_no_match_reports_neither_signal(tmp_path):
    cfg = config_dir(tmp_path, {"mcpServers": {"unrelated": {"command": "true"}}})
    code, out = run({"operation": "discover", "capability": "pr-source", "config_dir": str(cfg)})
    assert code == 0
    assert all(t["category"] != "mcp" for t in out["tools"])


# ---------------------------------------------------------------------------
# input validation and exit codes
# ---------------------------------------------------------------------------

def test_unknown_capability_exit_1(tmp_path):
    code, out = run({"operation": "discover", "capability": "no-such-capability", "config_dir": str(config_dir(tmp_path))})
    assert code == 1
    assert out["status"] == "error"
    assert "no-such-capability" in out["errors"][0]


def test_invalid_json_exit_2(tmp_path):
    code, out = run(raw="not json")
    assert code == 2
    assert out["status"] == "error"
    assert out["errors"]


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        with tempfile.TemporaryDirectory() as inner:
            test(Path(inner))
    print(f"All {len(tests)} tests passed.")


if __name__ == "__main__":
    main()
