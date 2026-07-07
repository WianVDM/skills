#!/usr/bin/env python3
"""Resolve the git scope for a baseline capture.

Accepts optional --scope and --branch arguments. If --branch is omitted, the
current git branch and commit are resolved. If --scope is omitted, the branch
name is used as the scope.

Outputs JSON:
    {
      "scope": "...",
      "branch": "...",
      "commit": "...",
      "dirty": true|false,
      "source": "..."
    }

If the working directory is not a git repository, outputs:
    {"error": "not a git repository"}

The script is read-only, deterministic, and safe to run in any project.
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def _run_git(args, cwd: Path):
    """Run a git command and return its CompletedProcess."""
    git = shutil.which("git")
    if not git:
        return None
    return subprocess.run(
        [git, *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def resolve_git_scope(scope: str = None, branch: str = None, cwd: Path = None):
    """Resolve branch, commit, dirty state, and scope."""
    if cwd is None:
        cwd = Path.cwd()

    git = shutil.which("git")
    if not git:
        raise RuntimeError("git not found in PATH")

    inside = _run_git(["rev-parse", "--is-inside-work-tree"], cwd)
    if inside is None or inside.returncode != 0 or inside.stdout.strip() != "true":
        raise RuntimeError("not a git repository")

    if branch:
        commit_proc = _run_git(["rev-parse", "--verify", branch], cwd)
        if commit_proc is None or commit_proc.returncode != 0:
            raise RuntimeError(f"branch not found: {branch}")
        resolved_branch = branch
        resolved_commit = commit_proc.stdout.strip()
        source = "command-line argument"
    else:
        branch_proc = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd)
        if branch_proc is None or branch_proc.returncode != 0:
            raise RuntimeError("could not resolve current branch")
        resolved_branch = branch_proc.stdout.strip()

        commit_proc = _run_git(["rev-parse", "HEAD"], cwd)
        if commit_proc is None or commit_proc.returncode != 0:
            raise RuntimeError("could not resolve current commit")
        resolved_commit = commit_proc.stdout.strip()

        source = "current branch" if resolved_branch != "HEAD" else "detached HEAD"

    status_proc = _run_git(["status", "--porcelain"], cwd)
    dirty = bool(status_proc.stdout.strip()) if status_proc and status_proc.returncode == 0 else False

    resolved_scope = scope if scope else resolved_branch

    return {
        "scope": resolved_scope,
        "branch": resolved_branch,
        "commit": resolved_commit,
        "dirty": dirty,
        "source": source,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Resolve the git scope for a baseline capture."
    )
    parser.add_argument(
        "--scope",
        help="Scope of the baseline (e.g. ticket key or feature name). Defaults to the branch name.",
    )
    parser.add_argument(
        "--branch",
        help="Target branch to baseline. Defaults to the current branch.",
    )
    parser.add_argument(
        "--cwd",
        help="Override the working directory. Default: current directory.",
    )
    args = parser.parse_args()

    cwd = Path(args.cwd).resolve() if args.cwd else Path.cwd()

    try:
        result = resolve_git_scope(
            scope=args.scope, branch=args.branch, cwd=cwd
        )
        print(json.dumps(result, indent=2))
        return 0
    except RuntimeError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
