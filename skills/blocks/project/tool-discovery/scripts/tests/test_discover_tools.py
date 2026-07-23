#!/usr/bin/env python3
"""
Tests for discover-tools.py.

Regression guards:
- the capabilities requested by pr-review (`reviews`, `changed-files`,
  `checkout`) must resolve from the bundled registry;
- MCP matching must use both `keywords` (server names) and `identifiers`
  (tool names) found in MCP config files;
- unknown capabilities must exit 1 and invalid JSON must exit 2, both with
  the {"status": "error", "errors": [...]} envelope on stdout;
- `search_scope: "project"` isolates discovery from the host environment
  (home MCP configs and skill dirs must not leak into results);
- platform detection reads the git origin remote;
- the recipe cache round-trips and invalidates per capability.

No network calls are made; MCP configs are faked on disk.

Run with:
    python -m pytest skills/blocks/project/tool-discovery/scripts/tests/
    python skills/blocks/project/tool-discovery/scripts/tests/test_discover_tools.py
"""

import json
import shutil
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


def isolated(tmp_path: Path, capability: str, cfg: Path, **extra) -> dict:
    """Discover payload scoped to the tmp project so host config cannot leak."""
    payload = {
        "operation": "discover",
        "capability": capability,
        "config_dir": str(cfg),
        "project_root": str(tmp_path),
        "search_scope": "project",
    }
    payload.update(extra)
    return payload


# ---------------------------------------------------------------------------
# bundled registry covers the capabilities pr-review requests
# ---------------------------------------------------------------------------

def test_reviews_capability_resolves(tmp_path):
    code, out = run(isolated(tmp_path, "reviews", config_dir(tmp_path)))
    assert code == 0
    assert out["status"] == "found"
    assert any(t["name"] == "manual" for t in out["tools"])


def test_changed_files_capability_resolves(tmp_path):
    code, out = run(isolated(tmp_path, "changed-files", config_dir(tmp_path)))
    assert code == 0
    assert out["status"] == "found"
    assert any(t["name"] == "manual" for t in out["tools"])


def test_checkout_capability_resolves(tmp_path):
    code, out = run(isolated(tmp_path, "checkout", config_dir(tmp_path)))
    assert code == 0
    assert out["status"] == "found"
    # No skill dirs exist under the tmp root, so the harness tool is
    # unverifiable-but-available rather than absent.
    harness = next(t for t in out["tools"] if t["name"] == "git-worktree-inspector")
    assert "unverifiable" in harness["detail"]


def test_registry_covers_non_github_platforms(tmp_path):
    """GitLab, Azure DevOps, and Bitbucket tools exist in the bundled registry."""
    import yaml
    registry = yaml.safe_load((SCRIPT.parent / "capability-registry.yaml").read_text(encoding="utf-8"))
    names = {t["name"] for t in registry["capabilities"]["pr-source"]["tools"]}
    assert {"gitlab-mcp", "azure-devops-mcp", "bitbucket-mcp", "glab-cli", "gitlab-api"} <= names
    tracker = {t["name"] for t in registry["capabilities"]["issue-tracker-source"]["tools"]}
    assert {"github-issues-mcp", "azure-boards-mcp", "gitlab-mcp"} <= tracker


# ---------------------------------------------------------------------------
# MCP matching via keywords and identifiers
# ---------------------------------------------------------------------------

def test_mcp_keyword_matching(tmp_path):
    cfg = config_dir(tmp_path, {"mcpServers": {"github": {"command": "docker"}}})
    code, out = run(isolated(tmp_path, "pr-source", cfg))
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
    code, out = run(isolated(tmp_path, "reviews", cfg))
    assert code == 0
    matches = [t for t in out["tools"] if t["category"] == "mcp" and t["name"] == "github-mcp"]
    assert matches, "github-mcp should match on the identifier token"
    assert matches[0]["detail"] == "MCP identifiers github_get_pull_request_reviews matched"


def test_mcp_no_match_reports_neither_signal(tmp_path):
    cfg = config_dir(tmp_path, {"mcpServers": {"unrelated": {"command": "true"}}})
    code, out = run(isolated(tmp_path, "pr-source", cfg))
    assert code == 0
    assert all(t["category"] != "mcp" for t in out["tools"])


def test_project_scope_ignores_host_mcp_configs(tmp_path):
    """A real github MCP config outside the project must not leak in scope=project."""
    home_cfg = tmp_path / "home" / ".pi" / "agent"
    home_cfg.mkdir(parents=True)
    (home_cfg / "mcp.json").write_text(json.dumps({"mcpServers": {"github": {}}}), encoding="utf-8")
    cfg = config_dir(tmp_path, {"mcpServers": {"unrelated": {"command": "true"}}})
    code, out = run(isolated(tmp_path, "pr-source", cfg))
    assert code == 0
    assert all(t["category"] != "mcp" for t in out["tools"])


# ---------------------------------------------------------------------------
# platform detection
# ---------------------------------------------------------------------------

def _git(args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)


def test_platform_detected_from_origin_remote(tmp_path):
    if not shutil.which("git"):
        return  # git unavailable; nothing to assert
    repo = tmp_path / "repo"
    repo.mkdir()
    assert _git(["init"], repo).returncode == 0
    _git(["remote", "add", "origin", "https://github.com/owner/repo.git"], repo)
    cfg = config_dir(tmp_path)
    code, out = run(isolated(repo, "pr-source", cfg))
    assert code == 0
    assert out["platform"] == "github"


def test_platform_unknown_without_repo(tmp_path):
    code, out = run(isolated(tmp_path, "pr-source", config_dir(tmp_path)))
    assert code == 0
    assert out["platform"] in ("unknown", "github", "gitlab", "azure", "bitbucket")


# ---------------------------------------------------------------------------
# recipe cache operations
# ---------------------------------------------------------------------------

def test_cache_roundtrip_and_invalidate(tmp_path):
    cfg = config_dir(tmp_path)
    entry = {
        "tool": "github-mcp",
        "platform": "github",
        "derived_at": "2026-07-20T00:00:00Z",
        "validated": True,
        "coverage": "complete",
        "steps": [{"call": "github_get_pull_request", "yields": "metadata"}],
        "revalidate": "github_get_pull_request on the current PR",
    }
    code, out = run({"operation": "cache-put", "capability": "pr-source", "config_dir": str(cfg), "entry": entry})
    assert code == 0
    assert out["status"] == "written"

    code, out = run({"operation": "cache-get", "capability": "pr-source", "config_dir": str(cfg)})
    assert code == 0
    assert out["status"] == "found"
    assert out["entry"]["tool"] == "github-mcp"
    assert out["entry"]["steps"][0]["yields"] == "metadata"

    code, out = run({"operation": "cache-invalidate", "capability": "pr-source", "config_dir": str(cfg)})
    assert code == 0
    assert out["status"] == "invalidated"

    code, out = run({"operation": "cache-get", "capability": "pr-source", "config_dir": str(cfg)})
    assert code == 1
    assert out["status"] == "not_found"


def test_cache_get_missing_is_not_found(tmp_path):
    code, out = run({"operation": "cache-get", "capability": "ci-source", "config_dir": str(config_dir(tmp_path))})
    assert code == 1
    assert out["status"] == "not_found"


# ---------------------------------------------------------------------------
# input validation and exit codes
# ---------------------------------------------------------------------------

def test_unknown_capability_exit_1(tmp_path):
    code, out = run(isolated(tmp_path, "no-such-capability", config_dir(tmp_path)))
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
