#!/usr/bin/env python3
"""Capture the current git state for a working directory.

Reads JSON from stdin: {"cwd": "<path>"}
Writes JSON to stdout:
  {
    "status": "ready" | "no_repo" | "error",
    "repo_root": "...",
    "branch": "...",
    "commit": "...",
    "remote": "...",
    "remote_url": "...",
    "upstream": "...",
    "is_dirty": false
  }
"""

import json
import subprocess
import sys
from pathlib import Path


def _help() -> str:
    return """get-git-state.py — capture local git state

Input JSON (stdin):
  {"cwd": "<working-directory>"}

Output JSON (stdout):
  {"status": "ready"|"no_repo"|"error", "repo_root": "...", "branch": "...",
   "commit": "...", "remote": "...", "remote_url": "...", "upstream": "...", "is_dirty": false}
"""


def _run_git(cwd: Path, *args, check: bool = False) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if check and result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode, ["git", *args], output=result.stdout, stderr=result.stderr
            )
        return result
    except FileNotFoundError as exc:
        raise RuntimeError("git binary not found") from exc
    except subprocess.SubprocessError as exc:
        raise RuntimeError(f"git command failed: {exc}") from exc


def _first_remote(cwd: Path) -> str:
    result = _run_git(cwd, "remote")
    if result.returncode != 0:
        return ""
    for line in result.stdout.splitlines():
        line = line.strip()
        if line:
            return line
    return ""


def _tracked_remote(cwd: Path, branch: str) -> str:
    if branch and branch != "HEAD":
        result = _run_git(cwd, "config", f"branch.{branch}.remote")
        if result.returncode == 0:
            remote = result.stdout.strip()
            if remote:
                return remote
    return ""


def _remote_url(cwd: Path, remote: str) -> str:
    if not remote:
        return ""
    result = _run_git(cwd, "remote", "get-url", remote)
    if result.returncode == 0:
        return result.stdout.strip()
    return ""


def _upstream(cwd: Path, branch: str, remote: str) -> str:
    if branch and branch != "HEAD":
        result = _run_git(cwd, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
        if result.returncode == 0:
            return result.stdout.strip()
        # Fallback to branch.*.merge config
        merge_res = _run_git(cwd, "config", f"branch.{branch}.merge")
        if merge_res.returncode == 0 and merge_res.stdout.strip():
            ref = merge_res.stdout.strip()
            if remote:
                return f"{remote}/{ref.replace('refs/heads/', '')}"
            return ref.replace("refs/heads/", "")
    return ""


def _is_dirty(cwd: Path) -> bool:
    result = _run_git(cwd, "status", "--porcelain")
    if result.returncode != 0:
        return False
    return bool(result.stdout.strip())


def _run(data: dict) -> dict:
    cwd = data.get("cwd", str(Path.cwd()))
    cwd_path = Path(cwd).resolve()

    if not cwd_path.exists():
        return {
            "status": "error",
            "repo_root": "",
            "branch": "",
            "commit": "",
            "remote": "",
            "remote_url": "",
            "upstream": "",
            "is_dirty": False,
            "reason": f"cwd does not exist: {cwd}",
        }

    toplevel = _run_git(cwd_path, "rev-parse", "--show-toplevel")
    if toplevel.returncode != 0:
        return {
            "status": "no_repo",
            "repo_root": "",
            "branch": "",
            "commit": "",
            "remote": "",
            "remote_url": "",
            "upstream": "",
            "is_dirty": False,
        }

    repo_root = toplevel.stdout.strip()
    branch = _run_git(cwd_path, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    commit = _run_git(cwd_path, "rev-parse", "--short", "HEAD").stdout.strip()

    remote = _tracked_remote(cwd_path, branch) or _first_remote(cwd_path)
    remote_url = _remote_url(cwd_path, remote)
    upstream = _upstream(cwd_path, branch, remote)
    dirty = _is_dirty(cwd_path)

    return {
        "status": "ready",
        "repo_root": repo_root,
        "branch": branch,
        "commit": commit,
        "remote": remote,
        "remote_url": remote_url,
        "upstream": upstream,
        "is_dirty": dirty,
    }


if __name__ == "__main__":
    if any(arg in ("-h", "--help") for arg in sys.argv[1:]):
        print(_help())
        sys.exit(0)

    try:
        data = json.load(sys.stdin)
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "error",
                    "repo_root": "",
                    "branch": "",
                    "commit": "",
                    "remote": "",
                    "remote_url": "",
                    "upstream": "",
                    "is_dirty": False,
                    "reason": f"invalid JSON input: {exc}",
                }
            ),
            file=sys.stderr,
        )
        sys.exit(2)

    try:
        result = _run(data)
    except Exception as exc:
        result = {
            "status": "error",
            "repo_root": "",
            "branch": "",
            "commit": "",
            "remote": "",
            "remote_url": "",
            "upstream": "",
            "is_dirty": False,
            "reason": str(exc),
        }

    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] != "error" else 1)
