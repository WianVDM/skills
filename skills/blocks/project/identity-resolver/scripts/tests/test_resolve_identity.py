#!/usr/bin/env python3
"""
Tests for resolve-identity.py.

Regression guards:
- unmatched free text must return needs_input, never a fabricated branch.
- gitlab merge-request URLs must produce gitlab URLs in the output.
- unknown operations and invalid JSON must exit 2 with the error envelope.

Run with:
    python -m pytest skills/blocks/project/identity-resolver/scripts/tests/
    python skills/blocks/project/identity-resolver/scripts/tests/test_resolve_identity.py
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "resolve-identity.py"


def run(payload, cwd=None):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    try:
        return proc.returncode, json.loads(proc.stdout)
    except json.JSONDecodeError:
        return proc.returncode, {"_raw": proc.stdout + proc.stderr}


def git(*args, cwd=None):
    proc = subprocess.run(
        ["git"] + list(args),
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    assert proc.returncode == 0, proc.stderr
    return proc.stdout.strip()


# ---------------------------------------------------------------------------
# unmatched input (regression: any text resolved as type branch)
# ---------------------------------------------------------------------------

def test_unmatched_input_returns_needs_input(tmp_path):
    code, out = run(
        {"operation": "resolve", "user_input": "hello world", "cwd": str(tmp_path)}
    )
    assert code == 1
    assert out["status"] == "needs_input"
    assert out.get("type") != "branch"


def test_unmatched_branch_shaped_input_without_git_evidence(tmp_path):
    code, out = run(
        {"operation": "resolve", "user_input": "feature/nope", "cwd": str(tmp_path)}
    )
    assert code == 1
    assert out["status"] == "needs_input"


# ---------------------------------------------------------------------------
# PR URLs
# ---------------------------------------------------------------------------

def test_gitlab_merge_request_url(tmp_path):
    code, out = run(
        {
            "operation": "resolve",
            "user_input": "https://gitlab.com/owner/repo/-/merge_requests/7",
            "cwd": str(tmp_path),
        }
    )
    assert code == 0
    assert out["status"] == "found"
    assert out["type"] == "pr"
    assert out["key"] == "7@owner-repo"
    assert out["repo"] == "owner/repo"
    assert out["url"] == "https://gitlab.com/owner/repo/-/merge_requests/7"


def test_github_pr_url(tmp_path):
    code, out = run(
        {
            "operation": "resolve",
            "user_input": "https://github.com/owner/repo/pull/42",
            "cwd": str(tmp_path),
        }
    )
    assert code == 0
    assert out["status"] == "found"
    assert out["type"] == "pr"
    assert out["key"] == "42@owner-repo"
    assert out["repo"] == "owner/repo"
    assert out["url"] == "https://github.com/owner/repo/pull/42"


# ---------------------------------------------------------------------------
# ticket keys
# ---------------------------------------------------------------------------

def test_ticket_key_in_text(tmp_path):
    code, out = run(
        {"operation": "resolve", "user_input": "please fix OC-1234 soon", "cwd": str(tmp_path)}
    )
    assert code == 0
    assert out["status"] == "found"
    assert out["type"] == "ticket"
    assert out["key"] == "OC-1234"
    assert out["project"] == "OC"


# ---------------------------------------------------------------------------
# branch detection against a real git repo
# ---------------------------------------------------------------------------

def test_branch_detection_in_real_git_repo(tmp_path):
    if not shutil.which("git"):
        import pytest

        pytest.skip("git not available")
    repo = tmp_path / "repo"
    repo.mkdir()
    git("init", "-b", "main", cwd=repo)
    git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "--allow-empty", "-m", "init", cwd=repo)
    git("checkout", "-b", "feature/test", cwd=repo)

    # Branch-shaped input that exists in git resolves as branch.
    code, out = run(
        {"operation": "resolve", "user_input": "feature/test", "cwd": str(repo)}
    )
    assert code == 0
    assert out["status"] == "found"
    assert out["type"] == "branch"
    assert out["branch"] == "feature/test"
    assert out["commit"]

    # No input falls back to the current git branch.
    code, out = run({"operation": "resolve", "cwd": str(repo)})
    assert code == 0
    assert out["status"] == "found"
    assert out["type"] == "branch"
    assert out["branch"] == "feature/test"

    # Branch-shaped input that does not exist in git is not fabricated.
    code, out = run(
        {"operation": "resolve", "user_input": "feature/ghost", "cwd": str(repo)}
    )
    assert code == 1
    assert out["status"] == "needs_input"


# ---------------------------------------------------------------------------
# input validation and exit codes
# ---------------------------------------------------------------------------

def test_invalid_json_exit_2():
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        input="not json",
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2
    out = json.loads(proc.stdout)
    assert out["status"] == "error"
    assert isinstance(out["errors"], list) and out["errors"]


def test_unknown_operation_exit_2():
    code, out = run({"operation": "delete_everything"})
    assert code == 2
    assert out["status"] == "error"
    assert any("unknown operation" in e for e in out["errors"])


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        if "tmp_path" in test.__code__.co_varnames:
            with tempfile.TemporaryDirectory() as inner:
                test(Path(inner))
        else:
            test()
    print(f"All {len(tests)} tests passed.")


if __name__ == "__main__":
    main()
