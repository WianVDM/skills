#!/usr/bin/env python3
"""resolve-identity.py

Resolve a work item from user input.

Operations:
  resolve  Return a normalized identity for a work item.

Input JSON on stdin:
  {"operation": "resolve", "user_input": "42", "repo": "owner/repo", "branch": "feature/OC-1234"}

Output JSON to stdout:
  {"status": "found", "type": "pr", "key": "42@owner-repo", "repo": "owner/repo", ...}
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional


TICKET_RE = re.compile(r"[A-Z][A-Z0-9]*-\d+")
PR_URL_RE = re.compile(r"(?:https?://[^/]+/)?([^/]+)/([^/]+)/(?:pull|merge_requests)/(\d+)", re.IGNORECASE)
COMMIT_RE = re.compile(r"^[a-f0-9]{7,40}$", re.IGNORECASE)


def _help() -> str:
    return """resolve-identity.py — resolve a work item from user input

Input JSON (stdin):
  {"operation": "resolve", "user_input": "...", "repo": "owner/repo", "branch": "..."}

Output JSON (stdout):
  {"status": "found", "type": "pr", "key": "...", "repo": "...", ...}
"""


def _extract_ticket_keys(text: str) -> list[str]:
    """Return all unique ticket keys found in text, in order of appearance."""
    return list(dict.fromkeys(TICKET_RE.findall(text)))


def _run_git(args: list[str], cwd: Optional[Path] = None) -> tuple[int, str, str]:
    """Run a git command and return exit code, stdout, stderr."""
    try:
        proc = subprocess.run(
            ["git"] + args,
            cwd=str(cwd) if cwd else None,
            text=True,
            capture_output=True,
            check=False,
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except FileNotFoundError:
        return 1, "", "git not found"


def _detect_current_branch(cwd: Optional[Path] = None) -> Optional[str]:
    rc, out, _ = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd)
    if rc == 0 and out and out != "HEAD":
        return out
    return None


def _detect_repo_from_git(cwd: Optional[Path] = None) -> Optional[str]:
    """Detect owner/repo from the origin remote."""
    rc, out, _ = _run_git(["remote", "get-url", "origin"], cwd)
    if rc != 0:
        return None
    url = out.strip()
    # Handle https://github.com/owner/repo.git and git@github.com:owner/repo.git
    m = re.search(r"[:/]([^/]+)/([^/]+?)(?:\.git)?$", url)
    if m:
        return f"{m.group(1)}/{m.group(2)}"
    return None


def _detect_commit_for_branch(branch: str, cwd: Optional[Path] = None) -> Optional[str]:
    rc, out, _ = _run_git(["rev-parse", branch], cwd)
    if rc == 0:
        return out
    return None


def _normalize_repo(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    value = value.strip().lower()
    # Remove trailing .git and any URL prefix.
    value = re.sub(r"\.git$", "", value)
    value = re.sub(r"^https?://[^/]+/", "", value)
    value = re.sub(r"^git@[^:]+:", "", value)
    if re.match(r"^[a-z0-9_.-]+/[a-z0-9_.-]+$", value):
        return value
    return None


def _repo_slug(repo: str) -> str:
    """Return a filesystem-safe slug from owner/repo."""
    return repo.replace("/", "-").lower()


def _resolve_ticket(user_input: str, source: str) -> dict:
    keys = _extract_ticket_keys(user_input)
    key = keys[0]
    project = key.split("-", 1)[0]
    return {
        "status": "found",
        "type": "ticket",
        "key": key,
        "repo": None,
        "branch": None,
        "base": None,
        "commit": None,
        "url": None,
        "project": project,
        "source": source,
    }


def _resolve_pr_url(user_input: str) -> Optional[dict]:
    m = PR_URL_RE.search(user_input)
    if not m:
        return None
    owner, repo_name, number = m.groups()
    repo = f"{owner}/{repo_name}"
    return {
        "status": "found",
        "type": "pr",
        "key": f"{number}@{_repo_slug(repo)}",
        "repo": repo.lower(),
        "branch": None,
        "base": None,
        "commit": None,
        "url": f"https://github.com/{owner}/{repo_name}/pull/{number}",
        "project": None,
        "source": "url",
    }


def _resolve_pr_number(user_input: str, repo: Optional[str]) -> Optional[dict]:
    if not user_input.isdigit():
        return None
    repo = _normalize_repo(repo)
    if not repo:
        return None
    number = user_input
    owner, repo_name = repo.split("/", 1)
    return {
        "status": "found",
        "type": "pr",
        "key": f"{number}@{_repo_slug(repo)}",
        "repo": repo,
        "branch": None,
        "base": None,
        "commit": None,
        "url": f"https://github.com/{owner}/{repo_name}/pull/{number}",
        "project": None,
        "source": "user_input",
    }


def _resolve_commit(user_input: str, cwd: Optional[Path] = None) -> Optional[dict]:
    if not COMMIT_RE.match(user_input):
        return None
    # Validate with git if available.
    commit = user_input.lower()
    if cwd is not None:
        rc, out, _ = _run_git(["rev-parse", "--verify", commit], cwd)
        if rc == 0:
            commit = out
    return {
        "status": "found",
        "type": "commit",
        "key": commit,
        "repo": None,
        "branch": None,
        "base": None,
        "commit": commit,
        "url": None,
        "project": None,
        "source": "user_input",
    }


def _resolve_branch(branch: Optional[str], repo: Optional[str], cwd: Optional[Path] = None) -> Optional[dict]:
    if not branch:
        branch = _detect_current_branch(cwd)
    if not branch:
        return None
    repo = _normalize_repo(repo)
    commit = _detect_commit_for_branch(branch, cwd) if cwd else None
    keys = _extract_ticket_keys(branch)
    project = keys[0].split("-", 1)[0] if keys else None
    return {
        "status": "found",
        "type": "branch",
        "key": branch,
        "repo": repo,
        "branch": branch,
        "base": None,
        "commit": commit,
        "url": None,
        "project": project,
        "source": "branch",
    }


def _clean_output(result: dict) -> dict:
    """Remove null values from the output for readability, keeping required fields."""
    return {k: v for k, v in result.items() if v is not None or k in ("status", "type", "key")}


def _do_resolve(data: dict) -> dict:
    user_input = str(data.get("user_input", "")).strip()
    repo_hint = data.get("repo")
    branch_hint = data.get("branch")
    work_item_type = data.get("work_item_type")
    cwd = data.get("cwd")
    cwd_path = Path(cwd).resolve() if cwd else None

    # Resolve repo from git if not provided.
    repo = _normalize_repo(repo_hint) or _detect_repo_from_git(cwd_path)

    # 1. Explicit work-item type hint.
    if work_item_type == "ticket" and user_input:
        keys = _extract_ticket_keys(user_input)
        if keys:
            return _clean_output(_resolve_ticket(user_input, "user_input"))
    elif work_item_type == "pr" and user_input:
        pr = _resolve_pr_url(user_input) or _resolve_pr_number(user_input, repo)
        if pr:
            return _clean_output(pr)
    elif work_item_type == "branch":
        branch = _resolve_branch(branch_hint or user_input, repo, cwd_path)
        if branch:
            return _clean_output(branch)
    elif work_item_type == "commit" and user_input:
        commit = _resolve_commit(user_input, cwd_path)
        if commit:
            return _clean_output(commit)

    # 2. Ticket key in input.
    if user_input and TICKET_RE.search(user_input):
        return _clean_output(_resolve_ticket(user_input, "text"))

    # 3. PR URL.
    if user_input:
        pr = _resolve_pr_url(user_input)
        if pr:
            return _clean_output(pr)

    # 4. PR number.
    if user_input:
        pr = _resolve_pr_number(user_input, repo)
        if pr:
            return _clean_output(pr)

    # 5. Commit hash.
    if user_input:
        commit = _resolve_commit(user_input, cwd_path)
        if commit:
            return _clean_output(commit)

    # 6. Branch (provided or current).
    branch = _resolve_branch(branch_hint or user_input, repo, cwd_path)
    if branch:
        return _clean_output(branch)

    # 7. No match.
    return {
        "status": "needs_input",
        "reason": "could not resolve input to a known work item type",
        "input": user_input or None,
    }


def _run(data: dict) -> dict:
    operation = data.get("operation")
    if operation == "resolve":
        return _do_resolve(data)
    return {"status": "error", "errors": [f"unknown operation: {operation}"]}


def _main() -> int:
    if any(arg in ("-h", "--help") for arg in sys.argv[1:]):
        print(_help())
        return 0

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(
            json.dumps({"status": "error", "errors": [f"invalid JSON input: {exc}"]}),
            file=sys.stderr,
        )
        return 2

    result = _run(data)
    print(json.dumps(result, indent=2))
    return 0 if result.get("status") == "found" else 1


if __name__ == "__main__":
    sys.exit(_main())
