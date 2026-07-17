#!/usr/bin/env python3
"""inspect-worktree.py

Check out a branch or commit in a git worktree, inspect changed files, run scoped checks, and clean up.

Operations:
  inspect       Create a worktree, list changed files, run commands, reset changes, clean up.
  changed_files Create a worktree and list changed files.
  cleanup       Remove a registered worktree.

Input JSON on stdin.
Output JSON to stdout.

Safety: cleanup only removes directories registered in `git worktree list` of
their owning repo. It never deletes the main repo and never falls back to
recursive deletion of unverified paths.

Exit codes:
  0 — operation completed (status complete/found/removed).
  1 — runtime failure (git errors, missing repo, refused cleanup).
  2 — invalid input (missing required fields, unknown operation, bad JSON).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Optional


TIMEOUT = 300


class InputError(ValueError):
    """Invalid caller input; maps to exit code 2."""


def _help() -> str:
    return """inspect-worktree.py — check out a branch in a git worktree and run scoped checks

Input JSON (stdin):
  {"operation": "inspect", "repo": "/path/to/repo", "branch": "feature/x", "base": "main", "commands": [{"name": "lint", "cmd": ["npx", "eslint", "{files}"], "include_files": true}]}
  {"operation": "changed_files", "repo": "/path/to/repo", "branch": "feature/x", "base": "main"}
  {"operation": "cleanup", "worktree": "/path/to/worktree"}

cleanup only removes directories that are registered git worktrees.
"""


def _run_git(args: list[str], cwd: Path, check: bool = True) -> tuple[int, str, str]:
    if not cwd.exists():
        raise RuntimeError(f"directory does not exist: {cwd}")
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            text=True,
            capture_output=True,
            check=False,
            timeout=TIMEOUT,
        )
        if check and proc.returncode != 0:
            raise RuntimeError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except FileNotFoundError:
        raise RuntimeError("git is not installed or not on PATH")


def _validate_repo(repo: Path) -> None:
    if not repo.exists():
        raise RuntimeError(f"repo path does not exist: {repo}")
    git_dir = _git_dir(repo)
    if not git_dir or not git_dir.exists():
        raise RuntimeError(f"repo is not a git repository: {repo}")


def _git_dir(repo: Path) -> Optional[Path]:
    """Return the git directory for a repo."""
    try:
        rc, out, _ = _run_git(["rev-parse", "--git-dir"], repo, check=False)
        if rc != 0:
            return None
        git_dir = out.strip()
        if not git_dir:
            return None
        path = Path(git_dir)
        if not path.is_absolute():
            path = repo / path
        return path.resolve()
    except RuntimeError:
        return None


def _resolve_base_name(repo: Path, base: Optional[str]) -> str:
    """Resolve the base branch name, falling back to main/master."""
    if base:
        return base
    for candidate in ("main", "master"):
        rc, _, _ = _run_git(["rev-parse", "--verify", candidate], repo, check=False)
        if rc == 0:
            return candidate
    raise RuntimeError("could not resolve base branch; provide --base or ensure main/master exists")


def _resolve_sha(repo: Path, ref: str) -> str:
    """Resolve a ref to a commit SHA in the main repo."""
    rc, out, err = _run_git(["rev-parse", "--verify", ref], repo, check=False)
    if rc != 0:
        raise RuntimeError(f"could not resolve ref '{ref}' in main repo: {err}")
    return out.strip()


def _sanitize_branch_name(branch: str) -> str:
    """Make a branch name safe for use in a directory name."""
    return "".join(c if c.isalnum() or c in "_-" else "_" for c in branch).strip("_")[:50]


def _create_worktree(repo: Path, branch: str) -> Path:
    """Create a git worktree and return its path.

    Sibling of the main repo by default; system temp if the repo parent is not
    writable. git creates the target directory itself.
    """
    name = f"wti-{_sanitize_branch_name(branch)}-{int(time.time())}-{os.getpid()}"
    candidates = [repo.parent / name, Path(tempfile.gettempdir()) / name]
    last_error: Optional[Exception] = None
    for path in candidates:
        try:
            # Detached HEAD so the branch can be checked out even if it is already active elsewhere.
            _run_git(["worktree", "add", "--detach", str(path), branch], repo)
            return path.resolve()
        except RuntimeError as exc:
            last_error = exc
    raise RuntimeError(f"could not create worktree for '{branch}': {last_error}")


def _registered_worktrees(repo: Path) -> list[Path]:
    """All worktree paths registered with the repo (main repo included)."""
    rc, out, _ = _run_git(["worktree", "list", "--porcelain"], repo, check=False)
    paths = []
    for line in out.splitlines():
        if line.startswith("worktree "):
            paths.append(Path(line[len("worktree "):].strip()).resolve())
    return paths


def _remove_worktree(repo: Path, worktree_path: Path) -> None:
    """Remove a registered worktree. Never removes the main repo."""
    if worktree_path.resolve() == repo.resolve():
        raise RuntimeError(f"refusing to remove the main repo: {worktree_path}")
    _run_git(["worktree", "remove", "--force", str(worktree_path)], repo, check=False)
    if worktree_path.exists():
        shutil.rmtree(str(worktree_path), ignore_errors=True)


def _changed_files(worktree: Path, base: str) -> list[str]:
    rc, out, _ = _run_git(["diff", "--name-only", f"{base}..HEAD"], worktree, check=False)
    if rc != 0:
        # Try base as a single commit comparison.
        rc, out, _ = _run_git(["diff", "--name-only", base, "HEAD"], worktree, check=False)
    files = [line.strip() for line in out.splitlines() if line.strip()]
    return files


def _status_files(worktree: Path) -> list[str]:
    """Return list of files with modifications in the worktree working tree."""
    rc, out, _ = _run_git(["status", "--porcelain"], worktree, check=False)
    if rc != 0:
        return []
    files = []
    for line in out.splitlines():
        if len(line) >= 3 and line[:2] != "??":
            entry = line[3:].strip()
            # Porcelain renames look like "old -> new"; track the new path.
            if " -> " in entry:
                entry = entry.split(" -> ")[-1]
            files.append(entry)
    return files


def _reset_worktree(worktree: Path) -> None:
    _run_git(["checkout", "--", "."], worktree, check=False)


def _substitute_files(cmd: list[str], files: list[str], include_files: bool) -> list[str]:
    if not include_files or not files:
        # Remove any {files} placeholder if no files.
        return [arg for arg in cmd if arg != "{files}"]

    has_placeholder = any(arg == "{files}" for arg in cmd)
    if has_placeholder:
        result = []
        for arg in cmd:
            if arg == "{files}":
                result.extend(files)
            else:
                result.append(arg)
        return result
    # Append files if no placeholder but include_files is true.
    return cmd + files


def _run_command(name: str, cmd: list[str], cwd: Path) -> dict:
    start = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            text=True,
            capture_output=True,
            check=False,
            timeout=TIMEOUT,
        )
        return {
            "name": name,
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "duration_seconds": round(time.time() - start, 2),
        }
    except FileNotFoundError as exc:
        return {
            "name": name,
            "returncode": 127,
            "stdout": "",
            "stderr": f"command not found: {exc}",
            "duration_seconds": round(time.time() - start, 2),
        }
    except subprocess.TimeoutExpired:
        return {
            "name": name,
            "returncode": 124,
            "stdout": "",
            "stderr": f"command timed out after {TIMEOUT} seconds",
            "duration_seconds": round(time.time() - start, 2),
        }


def _do_inspect(data: dict) -> dict:
    repo = Path(data.get("repo", ".")).resolve()
    branch = data.get("branch")
    if not branch:
        raise InputError("branch is required")
    _validate_repo(repo)
    base_name = _resolve_base_name(repo, data.get("base"))
    base_sha = _resolve_sha(repo, base_name)
    commands = data.get("commands", [])
    keep_worktree = data.get("keep_worktree", False)

    worktree = _create_worktree(repo, branch)

    try:
        files = _changed_files(worktree, base_sha)

        results = []
        for item in commands:
            name = item.get("name", "unnamed")
            cmd = item.get("cmd", [])
            include_files = item.get("include_files", False)
            if not cmd:
                results.append({"name": name, "returncode": 2, "stdout": "", "stderr": "empty command", "duration_seconds": 0})
                continue
            substituted = _substitute_files(cmd, files, include_files)
            results.append(_run_command(name, substituted, worktree))

        reset_files = _status_files(worktree)
        if reset_files:
            _reset_worktree(worktree)

        clean = not _status_files(worktree)

        return {
            "status": "complete",
            "worktree": str(worktree),
            "base": base_name,
            "base_sha": base_sha,
            "changed_files": files,
            "results": results,
            "reset_files": reset_files,
            "clean": clean,
        }
    finally:
        if not keep_worktree:
            _remove_worktree(repo, worktree)


def _do_changed_files(data: dict) -> dict:
    repo = Path(data.get("repo", ".")).resolve()
    branch = data.get("branch")
    if not branch:
        raise InputError("branch is required")
    _validate_repo(repo)
    base_name = _resolve_base_name(repo, data.get("base"))
    base_sha = _resolve_sha(repo, base_name)

    worktree = _create_worktree(repo, branch)
    try:
        files = _changed_files(worktree, base_sha)
        return {"status": "found", "base": base_name, "base_sha": base_sha, "changed_files": files}
    finally:
        _remove_worktree(repo, worktree)


def _do_cleanup(data: dict) -> dict:
    worktree_path = data.get("worktree")
    if not worktree_path:
        raise InputError("worktree is required for cleanup")
    worktree = Path(worktree_path).resolve()
    if not worktree.exists():
        return {"status": "error", "errors": [f"worktree path does not exist: {worktree}"]}

    repo = _find_main_repo(worktree)
    if repo is None:
        if _git_dir(worktree) is not None:
            return {
                "status": "error",
                "errors": [
                    f"refusing to remove {worktree}: it is a repository root, "
                    "not a worktree. cleanup only removes registered worktrees."
                ],
            }
        return {
            "status": "error",
            "errors": [
                f"refusing to remove {worktree}: not a git worktree. "
                "cleanup only removes registered worktrees."
            ],
        }
    if worktree == repo.resolve():
        return {
            "status": "error",
            "errors": [f"refusing to remove the main repo: {worktree}"],
        }
    if worktree not in _registered_worktrees(repo):
        return {
            "status": "error",
            "errors": [
                f"refusing to remove {worktree}: not registered in `git worktree list` "
                f"of {repo}."
            ],
        }

    _remove_worktree(repo, worktree)
    return {"status": "removed", "worktree": str(worktree)}


def _find_main_repo(worktree: Path) -> Optional[Path]:
    """Try to find the main repo that owns a worktree."""
    gitdir_file = worktree / ".git"
    if gitdir_file.is_file():
        try:
            content = gitdir_file.read_text().strip()
            if content.startswith("gitdir:"):
                gitdir = Path(content[len("gitdir:"):].strip())
                if not gitdir.is_absolute():
                    gitdir = (worktree / gitdir).resolve()
                # gitdir is .../.git/worktrees/<name>. Main repo is ...
                main = gitdir.parent.parent.parent
                if _git_dir(main):
                    return main
        except OSError:
            pass
    return None


def _run(data: dict) -> dict:
    operation = data.get("operation")
    if operation == "inspect":
        return _do_inspect(data)
    if operation == "changed_files":
        return _do_changed_files(data)
    if operation == "cleanup":
        return _do_cleanup(data)
    raise InputError(f"unknown operation: {operation}")


def _main() -> int:
    if any(arg in ("-h", "--help") for arg in sys.argv[1:]):
        print(_help())
        return 0

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(json.dumps({"status": "error", "errors": [f"invalid JSON input: {exc}"]}))
        return 2

    try:
        result = _run(data)
        code = 0 if result.get("status") in ("complete", "found", "removed") else 1
    except InputError as exc:
        result = {"status": "error", "errors": [str(exc)]}
        code = 2
    except Exception as exc:
        result = {"status": "error", "errors": [str(exc)]}
        code = 1

    print(json.dumps(result, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(_main())
