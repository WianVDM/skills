#!/usr/bin/env python3
"""Find PRs related to a ticket or files.

Tries, in order:
    1. Search git log messages for PR references matching the ticket key.
    2. Search git log messages for the ticket key itself.
    3. If the `gh` CLI is available and GITHUB_TOKEN is set, query GitHub.

Outputs JSON:
    {
      "prs": [
        {
          "number": "#123",
          "title": "...",
          "status": "open|merged|closed",
          "commit": "abc1234",
          "url": "..."
        }
      ]
    }

If no PRs are found, returns {"prs": []}.

The script is read-only, deterministic, and safe to run in any project.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PR_RE = re.compile(r"#(\d+)")
MERGE_RE = re.compile(r"Merge pull request #(\d+) from .*/([^\s]+)")


def _run_git(args: list, cwd: Path, timeout: int = 10) -> str:
    """Run a git command and return stdout, or empty string on failure."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
        return result.stdout.strip()
    except (subprocess.SubprocessError, OSError, FileNotFoundError):
        return ""


def _find_prs_in_git_log(ticket: str, files: list, cwd: Path) -> list:
    """Search git log for PR references related to the ticket or files."""
    prs = {}

    # Build git log args
    log_args = ["log", "--oneline", "--all", "--grep", ticket]
    if files:
        log_args.extend(["--"] + files)

    log = _run_git(log_args, cwd)
    for line in log.splitlines():
        match = PR_RE.search(line)
        if match:
            pr_num = f"#{match.group(1)}"
            if pr_num not in prs:
                prs[pr_num] = {
                    "number": pr_num,
                    "title": line.split(" ", 1)[1] if " " in line else "",
                    "status": "unknown",
                    "commit": line.split(" ")[0] if " " in line else "",
                    "url": "",
                    "source": "git-log",
                }

    # Also look for merge commits that mention the ticket
    merge_log = _run_git(
        ["log", "--oneline", "--all", "--merges", "--grep", ticket],
        cwd,
    )
    for line in merge_log.splitlines():
        match = MERGE_RE.search(line)
        if match:
            pr_num = f"#{match.group(1)}"
            if pr_num not in prs:
                prs[pr_num] = {
                    "number": pr_num,
                    "title": line.split(" ", 1)[1] if " " in line else "",
                    "status": "merged",
                    "commit": line.split(" ")[0] if " " in line else "",
                    "url": "",
                    "source": "git-merge-commit",
                }
            else:
                prs[pr_num]["status"] = "merged"

    return list(prs.values())


def _find_prs_via_gh(repo: str, ticket: str, cwd: Path) -> list:
    """Try to query PRs using the gh CLI if available."""
    if not os.environ.get("GITHUB_TOKEN"):
        return []

    try:
        result = subprocess.run(
            ["gh", "pr", "list", "--repo", repo, "--search", ticket, "--state", "all", "--json", "number,title,state,url,headRefName"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )
        if result.returncode != 0:
            return []
        data = json.loads(result.stdout)
        return [
            {
                "number": f"#{pr['number']}",
                "title": pr.get("title", ""),
                "status": pr.get("state", "unknown").lower(),
                "commit": "",
                "url": pr.get("url", ""),
                "source": "gh-cli",
            }
            for pr in data
        ]
    except (subprocess.SubprocessError, OSError, FileNotFoundError, json.JSONDecodeError):
        return []


def find_related_prs(ticket: str, files: list = None, repo: str = None, cwd: Path = None) -> dict:
    """Return PRs related to the ticket or files."""
    if cwd is None:
        cwd = Path.cwd()

    if files is None:
        files = []

    prs = _find_prs_in_git_log(ticket, files, cwd)

    if repo:
        gh_prs = _find_prs_via_gh(repo, ticket, cwd)
        seen = {pr["number"] for pr in prs}
        for pr in gh_prs:
            if pr["number"] not in seen:
                prs.append(pr)

    return {"prs": prs}


def main():
    parser = argparse.ArgumentParser(
        description="Find PRs related to a ticket or files."
    )
    parser.add_argument("--ticket", required=True, help="Ticket key to search for.")
    parser.add_argument(
        "--files",
        help="Comma-separated list of files to scope the search.",
    )
    parser.add_argument(
        "--repo",
        help="GitHub repo in the form owner/repo. Used for gh CLI queries.",
    )
    parser.add_argument(
        "--cwd",
        help="Override the working directory. Default: current directory.",
    )
    args = parser.parse_args()

    files = [f.strip() for f in args.files.split(",")] if args.files else []
    cwd = Path(args.cwd).resolve() if args.cwd else Path.cwd()

    try:
        result = find_related_prs(
            ticket=args.ticket,
            files=files,
            repo=args.repo,
            cwd=cwd,
        )
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:  # pragma: no cover - safety net
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
