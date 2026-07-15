#!/usr/bin/env python3
"""inspect-worktree.py

Check out a branch or commit in a git worktree, inspect changed files, run scoped checks, and clean up.

Operations:
  inspect       Create a worktree, list changed files, run commands, reset changes, clean up.
  changed_files Create a worktree and list changed files.
  cleanup       Remove a worktree.

Input JSON on stdin.
Output JSON to stdout.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Optional


TIMEOUT = 300


def _help() -> str:
    return """inspect-worktree.py — check out a branch in a git worktree and run scoped checks

Input JSON (stdin):
  {"operation": "inspect", "repo": "/path/to/repo", "branch": "feature/x", "base": "main", "commands": [{"name": "lint", "cmd": ["npx", "eslint", "{files}"], "include_files": true}]}
  {"operation": "changed_files", "repo": "/path/to/repo", "branch": "feature/x", "base": "main"}
  {"operation": "cleanup", "worktree": "/path/to/worktree"}
"""


def _run_git(args: list[str], cwd: Path, check: bool = True) -> tuple[int, str, str]:
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
    if not (repo / ".git").exists() and not _is_git_dir(repo):
        # Check if repo itself is a git worktree or bare repo
        pass
    git_dir = _git_dir(repo)
    if not git_dir or not git_dir.exists():
        raise RuntimeError(f"repo is not a git repository: {repo}")


def _is_git_dir(path: Path) -> bool:
    return (path / "HEAD").exists() and (path / "config").exists()


def _git_dir(repo: Path) -> Optional[Path]:
    """Return the git directory for a repo."""
    try:
        rc, out, _ = _run_git(["rev-parse", "--git-dir"], repo, check=False)
        if rc != 0:
            return None
        git_dir = out.strip()
        if not git_dir:
            return None
        return Path(git_dir).resolve()
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
    """Create a git worktree and return its path."""
    suffix = Path(tempfile.mkdtemp(prefix="wti-", dir=str(repo.parent))).name
    worktree_name = f"{_sanitize_branch_name(branch)}-{suffix}"
    parent = repo.parent
    worktree_path = parent / worktree_name
    # If parent is not writable, fall back to system temp.
    try:
        worktree_path = Path(tempfile.mkdtemp(prefix=f"wti-{_sanitize_branch_name(branch)}-")).resolve()
    except Exception:
        pass
    # Use detached HEAD so the branch can be checked out even if it is already active elsewhere.
    _run_git(["worktree", "add", "--detach", str(worktree_path), branch], repo)
    return worktree_path


def _remove_worktree(repo: Path, worktree_path: Path) -> None:
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
            files.append(line[3:].strip())
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
        return {"status": "error", "errors": ["branch is required"]}
    base_name = _resolve_base_name(repo, data.get("base"))
    base_sha = _resolve_sha(repo, base_name)
    commands = data.get("commands", [])
    keep_worktree = data.get("keep_worktree", False)

    _validate_repo(repo)
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
        return {"status": "error", "errors": ["branch is required"]}
    base_name = _resolve_base_name(repo, data.get("base"))
    base_sha = _resolve_sha(repo, base_name)

    _validate_repo(repo)
    worktree = _create_worktree(repo, branch)
    try:
        files = _changed_files(worktree, base_sha)
        return {"status": "found", "base": base_name, "base_sha": base_sha, "changed_files": files}
    finally:
        _remove_worktree(repo, worktree)


def _do_cleanup(data: dict) -> dict:
    worktree_path = data.get("worktree")
    if not worktree_path:
        return {"status": "error", "errors": ["worktree is required for cleanup"]}
    worktree = Path(worktree_path).resolve()
    # Try to find the main repo from the worktree.
    repo = _find_main_repo(worktree)
    if repo:
        _remove_worktree(repo, worktree)
    else:
        if worktree.exists():
            shutil.rmtree(str(worktree), ignore_errors=True)
    return {"status": "removed", "worktree": str(worktree)}


def _find_main_repo(worktree: Path) -> Optional[Path]:
    """Try to find the main repo that owns a worktree."""
    git_dir = _git_dir(worktree)
    if not git_dir:
        return None
    # In a worktree, git-dir points to .git/worktrees/<name>; parent is .git; main repo is .git/..
    # But the worktree may not be inside the main repo. We can look for the gitdir file.
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
                if (main / ".git").exists() or _is_git_dir(main / ".git"):
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
    return {"status": "error", "errors": [f"unknown operation: {operation}"]}


def _main() -> int:
    if any(arg in ("-h", "--help") for arg in sys.argv[1:]):
        print(_help())
        return 0

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(json.dumps({"status": "error", "errors": [f"invalid JSON input: {exc}"]}), file=sys.stderr)
        return 2

    try:
        result = _run(data)
    except Exception as exc:
        result = {"status": "error", "errors": [str(exc)]}

    print(json.dumps(result, indent=2))
    return 0 if result.get("status") in ("complete", "found", "removed") else 1


if __name__ == "__main__":
    sys.exit(_main())
