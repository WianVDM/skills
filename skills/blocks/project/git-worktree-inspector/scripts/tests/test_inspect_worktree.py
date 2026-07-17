#!/usr/bin/env python3
"""
Tests for inspect-worktree.py.

CLI behavior is tested via subprocess against real git repositories created in
temp dirs. The cleanup safety tests are the regression guard for the
arbitrary-delete hole: cleanup must refuse anything that is not a registered
git worktree.

Run with:
    python -m pytest skills/blocks/project/git-worktree-inspector/scripts/tests/
    python skills/blocks/project/git-worktree-inspector/scripts/tests/test_inspect_worktree.py
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "inspect-worktree.py"


def run(payload: dict, cwd: Path | None = None):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--json"],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    try:
        return proc.returncode, json.loads(proc.stdout)
    except json.JSONDecodeError:
        return proc.returncode, {"_raw": proc.stdout + proc.stderr}


def git(repo: Path, *args: str):
    proc = subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True
    )
    assert proc.returncode == 0, f"git {' '.join(args)}: {proc.stderr}"
    return proc.stdout.strip()


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "user.name", "Test")
    (repo / "base.txt").write_text("base\n", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "initial")
    git(repo, "checkout", "-b", "feature/x")
    (repo / "feature.txt").write_text("feature\n", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "feature work")
    git(repo, "checkout", "main")
    return repo


# ---------------------------------------------------------------------------
# cleanup safety (regression: arbitrary-delete hole)
# ---------------------------------------------------------------------------

def test_cleanup_refuses_unregistered_directory(tmp_path):
    innocent = tmp_path / "innocent"
    innocent.mkdir()
    (innocent / "important.txt").write_text("precious", encoding="utf-8")
    code, out = run({"operation": "cleanup", "worktree": str(innocent)})
    assert code == 1
    assert out["status"] == "error"
    assert "not a git worktree" in out["errors"][0]
    assert (innocent / "important.txt").exists()


def test_cleanup_refuses_nonexistent_path(tmp_path):
    code, out = run({"operation": "cleanup", "worktree": str(tmp_path / "nope")})
    assert code == 1
    assert out["status"] == "error"
    assert "does not exist" in out["errors"][0]


def test_cleanup_refuses_main_repo(tmp_path):
    repo = make_repo(tmp_path)
    code, out = run({"operation": "cleanup", "worktree": str(repo)})
    assert code == 1
    assert out["status"] == "error"
    assert "repository root" in out["errors"][0]
    assert (repo / ".git").exists()


def test_cleanup_removes_registered_worktree(tmp_path):
    repo = make_repo(tmp_path)
    worktree = tmp_path / "wt"
    git(repo, "worktree", "add", "--detach", str(worktree), "feature/x")
    code, out = run({"operation": "cleanup", "worktree": str(worktree)})
    assert code == 0
    assert out["status"] == "removed"
    assert not worktree.exists()


# ---------------------------------------------------------------------------
# input validation
# ---------------------------------------------------------------------------

def test_missing_branch_exit_2(tmp_path):
    repo = make_repo(tmp_path)
    code, out = run({"operation": "inspect", "repo": str(repo)})
    assert code == 2
    assert "branch is required" in out["errors"][0]


def test_unknown_operation_exit_2(tmp_path):
    code, out = run({"operation": "explode"})
    assert code == 2
    assert "unknown operation" in out["errors"][0]


def test_cleanup_missing_worktree_exit_2(tmp_path):
    code, out = run({"operation": "cleanup"})
    assert code == 2


def test_invalid_json_exit_2():
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--json"],
        input="not json",
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2
    assert json.loads(proc.stdout)["status"] == "error"


# ---------------------------------------------------------------------------
# inspect / changed_files flows
# ---------------------------------------------------------------------------

def test_changed_files_lists_branch_diff(tmp_path):
    repo = make_repo(tmp_path)
    code, out = run({"operation": "changed_files", "repo": str(repo), "branch": "feature/x", "base": "main"})
    assert code == 0
    assert out["status"] == "found"
    assert "feature.txt" in out["changed_files"]


def test_inspect_runs_commands_and_cleans_up(tmp_path):
    repo = make_repo(tmp_path)
    payload = {
        "operation": "inspect",
        "repo": str(repo),
        "branch": "feature/x",
        "base": "main",
        "commands": [
            {"name": "list", "cmd": ["git", "status", "--porcelain"]},
        ],
    }
    code, out = run(payload)
    assert code == 0
    assert out["status"] == "complete"
    assert "feature.txt" in out["changed_files"]
    assert out["results"][0]["returncode"] == 0
    # Worktree removed and no wti- leftovers beside the repo.
    assert not Path(out["worktree"]).exists()
    leftovers = [p for p in tmp_path.iterdir() if p.name.startswith("wti-")]
    assert leftovers == []


def test_inspect_keep_worktree(tmp_path):
    repo = make_repo(tmp_path)
    code, out = run({
        "operation": "inspect",
        "repo": str(repo),
        "branch": "feature/x",
        "base": "main",
        "keep_worktree": True,
    })
    assert code == 0
    worktree = Path(out["worktree"])
    assert worktree.exists()
    # Cleanup via the script still works on the kept worktree.
    code2, out2 = run({"operation": "cleanup", "worktree": str(worktree)})
    assert code2 == 0
    assert not worktree.exists()


def test_worktree_created_as_sibling(tmp_path):
    repo = make_repo(tmp_path)
    code, out = run({
        "operation": "inspect",
        "repo": str(repo),
        "branch": "feature/x",
        "base": "main",
        "keep_worktree": True,
    })
    worktree = Path(out["worktree"])
    assert worktree.parent == repo.parent
    run({"operation": "cleanup", "worktree": str(worktree)})


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    with tempfile.TemporaryDirectory() as tmp:
        for test in tests:
            with tempfile.TemporaryDirectory() as inner:
                test(Path(inner))
        print(f"All {len(tests)} tests passed.")


if __name__ == "__main__":
    main()
