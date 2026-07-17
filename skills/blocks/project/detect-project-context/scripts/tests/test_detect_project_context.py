#!/usr/bin/env python3
"""
Tests for detect-project-context.py and resolve-standards-path.py.

Pure detection logic is imported directly (fast, monkeypatchable); CLI behavior
is tested via subprocess because exit codes and the error envelope are part of
the interface.

Run with:
    python -m pytest skills/blocks/project/detect-project-context/scripts/tests/
    python skills/blocks/project/detect-project-context/scripts/tests/test_detect_project_context.py
"""

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock

SCRIPT_DIR = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


dpc = _load("detect_project_context", SCRIPT_DIR / "detect-project-context.py")
rsp = _load("resolve_standards_path", SCRIPT_DIR / "resolve-standards-path.py")


def run_cli(script: Path, *cli):
    proc = subprocess.run(
        [sys.executable, str(script), *cli, "--json"],
        capture_output=True,
        text=True,
    )
    try:
        return proc.returncode, json.loads(proc.stdout)
    except json.JSONDecodeError:
        return proc.returncode, {"_raw": proc.stdout + proc.stderr}


# ---------------------------------------------------------------------------
# find_project_root / detect
# ---------------------------------------------------------------------------

def test_marker_at_start(tmp_path):
    (tmp_path / ".agents").mkdir()
    root, marker = dpc.find_project_root(tmp_path)
    assert root == tmp_path and marker == ".agents"


def test_nested_subdir_finds_root(tmp_path):
    (tmp_path / ".agents").mkdir()
    nested = tmp_path / "src" / "app"
    nested.mkdir(parents=True)
    root, marker = dpc.find_project_root(nested)
    assert root == tmp_path and marker == ".agents"


def test_layout_marker_priority(tmp_path):
    (tmp_path / ".pi").mkdir()
    (tmp_path / ".agents").mkdir()
    _, marker = dpc.find_project_root(tmp_path)
    assert marker == ".agents"


def test_vcs_ceiling_stops_at_repo(tmp_path):
    # .agents lives above the repo; the search must not escape the repo.
    (tmp_path / ".agents").mkdir()
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    nested = repo / "src"
    nested.mkdir()
    root, marker = dpc.find_project_root(nested)
    assert root == repo and marker is None


def test_marker_at_vcs_root_wins(tmp_path):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".agents").mkdir()
    root, marker = dpc.find_project_root(tmp_path)
    assert root == tmp_path and marker == ".agents"


def test_worktree_git_file_counts_as_vcs_root(tmp_path):
    (tmp_path / ".agents").mkdir()
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    (worktree / ".git").write_text("gitdir: /elsewhere\n", encoding="utf-8")
    root, marker = dpc.find_project_root(worktree)
    assert root == worktree and marker is None


def test_no_anchor_returns_none(tmp_path, monkeypatch):
    # Isolate from real ancestors: pretend tmp_path is the filesystem root.
    bare = tmp_path / "bare"
    bare.mkdir()
    monkeypatch.setattr(Path, "parents", property(lambda self: []))
    root, marker = dpc.find_project_root(bare)
    assert root is None and marker is None


def test_bare_agents_dir_is_not_a_marker(tmp_path):
    (tmp_path / "agents").mkdir()
    monkeypatch_root = tmp_path / "agents" / "sub"
    monkeypatch_root.mkdir()
    with mock.patch.object(Path, "home", return_value=tmp_path / "nowhere"):
        result = dpc.detect(monkeypatch_root)
    assert result["marker"] != "agents"


def test_home_cap_demotes_confidence(tmp_path):
    home = tmp_path / "home"
    (home / ".agents" / "skills").mkdir(parents=True)
    (home / ".agents" / "context").mkdir()
    start = home / "scratch"
    start.mkdir()
    with mock.patch.object(Path, "home", return_value=home):
        result = dpc.detect(start)
    assert result["project_root"] == str(home.resolve())
    assert result["confidence"] == "low"
    assert "home directory" in result["note"]


def test_harness_marker_uses_agents_candidates(tmp_path):
    (tmp_path / ".claude").mkdir()
    result = dpc.detect(tmp_path)
    assert result["marker"] == ".claude"
    assert result["recommended_skills_dir"].endswith(".agents\\skills") or \
        result["recommended_skills_dir"].endswith(".agents/skills")
    assert ".claude" not in result["recommended_skills_dir"]
    assert "Harness marker" in result["note"]


def test_vcs_fallback_confidence_low_with_note(tmp_path):
    (tmp_path / ".git").mkdir()
    result = dpc.detect(tmp_path)
    assert result["marker"] is None
    assert result["confidence"] == "low"
    assert "VCS root" in result["note"]


def test_confidence_levels(tmp_path):
    (tmp_path / ".agents" / "skills").mkdir(parents=True)
    (tmp_path / ".agents" / "context").mkdir()
    assert dpc.detect(tmp_path)["confidence"] == "high"
    (tmp_path / ".agents" / "skills").rename(tmp_path / ".agents" / "not-skills")
    assert dpc.detect(tmp_path)["confidence"] == "medium"


def test_note_absent_on_clean_detection(tmp_path):
    (tmp_path / ".agents" / "skills").mkdir(parents=True)
    (tmp_path / ".agents" / "context").mkdir()
    assert dpc.detect(tmp_path)["note"] is None


# ---------------------------------------------------------------------------
# CLI contract
# ---------------------------------------------------------------------------

def test_cli_invalid_start_exit_2(tmp_path):
    code, out = run_cli(SCRIPT_DIR / "detect-project-context.py", "--start", str(tmp_path / "nope"))
    assert code == 2
    assert out["status"] == "error"
    assert "does not exist" in out["errors"][0]


def test_cli_start_not_a_directory(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("x")
    code, out = run_cli(SCRIPT_DIR / "detect-project-context.py", "--start", str(f))
    assert code == 2
    assert "not a directory" in out["errors"][0]


def test_cli_success_exit_0(tmp_path):
    (tmp_path / ".agents").mkdir()
    code, out = run_cli(SCRIPT_DIR / "detect-project-context.py", "--start", str(tmp_path))
    assert code == 0
    assert out["marker"] == ".agents"


def test_resolve_cli_invalid_start_exit_2(tmp_path):
    code, out = run_cli(SCRIPT_DIR / "resolve-standards-path.py", "--start", str(tmp_path / "nope"))
    assert code == 2
    assert out["status"] == "error"


# ---------------------------------------------------------------------------
# resolve_standards_path
# ---------------------------------------------------------------------------

def _standards_tree(root: Path) -> Path:
    path = root / "docs" / "skill-standards"
    path.mkdir(parents=True)
    (path / "README.md").write_text("# standards\n", encoding="utf-8")
    return path


def test_resolve_cli_override_valid(tmp_path):
    standards = _standards_tree(tmp_path)
    result = rsp.resolve_standards_path(tmp_path, str(standards))
    assert result["status"] == "found"
    assert result["source"] == "cli"
    assert result["standards_path"] == str(standards)


def test_resolve_cli_override_invalid(tmp_path):
    result = rsp.resolve_standards_path(tmp_path, str(tmp_path / "nope"))
    assert result["status"] == "missing"
    assert result["degraded"] is True
    assert result["fallback_options"]


def test_resolve_project_root_default(tmp_path):
    (tmp_path / ".agents").mkdir()
    standards = _standards_tree(tmp_path)
    result = rsp.resolve_standards_path(tmp_path)
    assert result["status"] == "found"
    assert result["source"] == "project-root"
    assert Path(result["standards_path"]) == standards


def test_resolve_marker_standards(tmp_path):
    marker = tmp_path / ".agents"
    marker.mkdir()
    standards = marker / "docs" / "skill-standards"
    standards.mkdir(parents=True)
    (standards / "README.md").write_text("# standards\n", encoding="utf-8")
    result = rsp.resolve_standards_path(tmp_path)
    assert result["status"] == "found"
    assert result["source"] == "marker"


def test_resolve_bundle_fallback_regression(tmp_path):
    # From anywhere, the resolver must find the standards shipped in this repo.
    result = rsp.resolve_standards_path(tmp_path)
    assert result["status"] == "found"
    found = Path(result["standards_path"])
    assert found.is_dir() and (found / "README.md").is_file()
    assert result["source"] in ("bundle", "marker", "project-root", "project-root-agents", "project-root-pi")


def test_resolve_missing_when_nothing_found(tmp_path):
    bare = tmp_path / "bare"
    bare.mkdir()
    with mock.patch.object(rsp, "_bundle_default", return_value=None), \
         mock.patch.object(Path, "home", return_value=bare):
        result = rsp.resolve_standards_path(bare)
    assert result["status"] == "missing"
    assert result["degraded"] is True


def test_resolve_missing_standards_path_file_is_skipped(tmp_path):
    # A standards_path that fails validation falls through to other candidates.
    (tmp_path / ".agents").mkdir()
    fake = tmp_path / "not-standards"
    fake.mkdir()
    (tmp_path / ".agents" / "config").mkdir()
    (tmp_path / ".agents" / "config" / "write-a-skill.yaml").write_text(
        f"standards_path: {fake}\n", encoding="utf-8"
    )
    real = _standards_tree(tmp_path)
    result = rsp.resolve_standards_path(tmp_path)
    assert result["status"] == "found"
    assert Path(result["standards_path"]) == real


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    with tempfile.TemporaryDirectory() as tmp:
        for test in tests:
            with tempfile.TemporaryDirectory() as inner:
                # Mirror pytest's tmp_path; monkeypatch-using tests are skipped
                # in direct mode unless they manage their own patching.
                try:
                    test(Path(inner))
                except TypeError:
                    print(f"skipped (needs pytest fixtures): {test.__name__}")
        print("direct run complete (pytest runs all tests)")


if __name__ == "__main__":
    main()
