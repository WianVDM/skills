#!/usr/bin/env python3
"""
map-ticket-relationships.py

Deterministic helper that maps all relationships surrounding a ticket.

Reads a JSON envelope from stdin and writes a JSON relationship graph to stdout.
This script does not call tracker APIs; it consumes the normalized ticket data
produced by research-ticket and enriches it with local git inspection.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def _run_git(args: list[str], cwd: Path | None = None, check: bool = False) -> str:
    """Run a git command and return stdout; return empty string on failure."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=check,
        )
        if result.returncode != 0:
            return ""
        return result.stdout.strip()
    except Exception:  # noqa: BLE001
        return ""


def _git_available(cwd: Path | None = None) -> bool:
    return bool(_run_git(["rev-parse", "--git-dir"], cwd=cwd))


def _discover_branches(key: str, cwd: Path | None = None) -> list[str]:
    """Find local and remote branches whose names contain the ticket key."""
    if not _git_available(cwd):
        return []
    output = _run_git(["branch", "-a", "--list", f"*{key}*"], cwd=cwd)
    if not output:
        return []
    branches: list[str] = []
    for line in output.splitlines():
        branch = line.strip().lstrip("*").strip()
        # Normalize remotes/origin/ prefix for readability
        if branch.startswith("remotes/"):
            branch = branch[len("remotes/") :]
        if branch and branch not in branches:
            branches.append(branch)
    return branches


def _discover_commits(key: str, cwd: Path | None = None, limit: int = 50) -> list[str]:
    """Find commits whose messages mention the ticket key."""
    if not _git_available(cwd):
        return []
    output = _run_git(
        ["log", "--all", f"--grep={key}", f"--max-count={limit}", "--format=%H"],
        cwd=cwd,
    )
    if not output:
        return []
    commits = [line.strip() for line in output.splitlines() if line.strip()]
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for commit in commits:
        if commit not in seen:
            seen.add(commit)
            unique.append(commit)
    return unique


def _discover_prs_from_merge_commits(key: str, cwd: Path | None = None) -> list[str]:
    """Infer PR numbers from merge commits that mention the ticket key."""
    if not _git_available(cwd):
        return []
    output = _run_git(
        ["log", "--all", "--merges", f"--grep={key}", "--max-count=20", "--format=%s"],
        cwd=cwd,
    )
    if not output:
        return []
    prs: list[str] = []
    seen: set[str] = set()
    # Match "Merge pull request #123" or "... (#123)"
    merge_re = re.compile(r"(?:Merge pull request #|(\(#))(\d+)")
    trailer_re = re.compile(r"\(#(\d+)\)")
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        for match in merge_re.finditer(line):
            pr = f"#{match.group(2)}"
            if pr not in seen:
                seen.add(pr)
                prs.append(pr)
        for match in trailer_re.finditer(line):
            pr = f"#{match.group(1)}"
            if pr not in seen:
                seen.add(pr)
                prs.append(pr)
    return prs


def _extract_affected_files(text: str | None, cwd: Path | None = None) -> list[str]:
    """Extract likely file paths from ticket text and validate them.

    Candidates must look like a source file (contain a slash and, when no
    filesystem match is found, end with an extension) to reduce false positives
    from prose or markdown links. When a `cwd` is provided, the candidate must
    exist under that root to be included.
    """
    if not text:
        return []
    # Require at least one directory separator. The final segment may carry
    # multiple dot-separated extensions (e.g. auth.guard.ts, styles.module.css).
    # The lookahead allows a trailing sentence period but not a continuing path.
    path_re = re.compile(
        r"(?<![a-zA-Z0-9_\-./])"
        r"([a-zA-Z0-9_\-]+(?:/[a-zA-Z0-9_\-]+)*/[a-zA-Z0-9_\-]+(?:\.[a-zA-Z0-9_\-]+)*)"
        r"(?![a-zA-Z0-9_\-/])"
    )
    candidates = path_re.findall(text)
    affected: list[str] = []
    seen: set[str] = set()
    root = cwd if cwd else Path(".")
    for candidate in candidates:
        if candidate.startswith("http") or candidate.startswith("www"):
            continue
        clean = candidate.lstrip("./")
        if not clean:
            continue
        # Validate against the filesystem when possible.
        if root.exists():
            target = root / clean
            if not target.exists():
                continue
        elif "." not in clean.split("/")[-1]:
            # No filesystem access and no extension; skip ambiguous matches.
            continue
        if clean and clean not in seen:
            seen.add(clean)
            affected.append(clean)
    return affected


def _is_bug_ticket(ticket_data: dict) -> bool:
    """Heuristic: a ticket is a bug if its labels or type contain 'bug'."""
    labels = ticket_data.get("labels", []) or []
    issue_type = ticket_data.get("issue_type", "") or ""
    combined = " ".join(str(item) for item in labels).lower() + " " + str(issue_type).lower()
    return "bug" in combined


def _trace_original_feature(
    ticket_data: dict, key: str, cwd: Path | None = None
) -> dict[str, str | None]:
    """Trace the original feature for a bug ticket.

    This first version is conservative: it only reports evidence that is
    explicitly present in the description or git history. It does not assume
    a linked ticket is the original feature.
    """
    result: dict[str, str | None] = {"ticket": None, "commit": None, "pr": None}
    if not _is_bug_ticket(ticket_data):
        return result

    description = ticket_data.get("description") or ""

    # 1. Look for explicit original-feature references in the description
    #    e.g. "regression from OC-3000", "original feature: OC-3000"
    explicit_re = re.compile(
        r"(?:regression from|original feature|introduced in|feature ticket)[:\s]+([A-Z][A-Z0-9]*-\d+)",
        re.IGNORECASE,
    )
    match = explicit_re.search(description)
    if match:
        result["ticket"] = match.group(1).upper()

    # 2. Search git history for the earliest commit touching an affected file
    affected_files = _extract_affected_files(description, cwd)
    if affected_files and _git_available(cwd):
        for file_path in affected_files[:3]:
            output = _run_git(
                ["log", "--all", "--format=%H", "--reverse", "--", file_path],
                cwd=cwd,
            )
            if output:
                first_commit = output.splitlines()[0].strip()
                if first_commit:
                    result["commit"] = first_commit
                    break

    return result


class InputError(Exception):
    """Raised when caller input is invalid; maps to exit code 2."""


def _normalize_list(value: object | None) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return [v for v in value if v is not None]
    return []


def map_relationships(
    ticket_key: str,
    ticket_data: dict,
    git_state: dict | None,
    codebase_root: str,
    infer_by_file: bool,
) -> dict:
    """Build the relationship graph."""
    cwd = Path(codebase_root) if codebase_root else Path(".")
    if not cwd.exists():
        cwd = Path(".")

    related = ticket_data.get("related_tickets", {}) or {}
    dev_info = ticket_data.get("dev_info", {}) or {}
    attachments = ticket_data.get("attachments", []) or []
    description = ticket_data.get("description") or ""
    summary = ticket_data.get("summary") or ""

    # Base relationships from tracker data
    parent = related.get("parent")
    children = _normalize_list(related.get("children"))
    duplicates = _normalize_list(related.get("duplicates"))
    linked = _normalize_list(related.get("linked"))
    blocked_by = _normalize_list(related.get("blocked_by"))
    blocks = _normalize_list(related.get("blocks"))

    gaps: list[str] = []

    # Siblings are other children of the same parent. Use explicit tracker data if
    # available; otherwise this remains empty because we do not call tracker APIs in v1.
    siblings = _normalize_list(related.get("siblings"))
    if not siblings and parent:
        gaps.append("Sibling derivation requires fetching the parent ticket's children; not available in v1.")

    # Implementation artifacts from tracker data
    prs = _normalize_list(dev_info.get("prs", []))
    branches = _normalize_list(dev_info.get("branches", []))
    commits = _normalize_list(dev_info.get("commits", []))

    # Enrich with git discovery
    if _git_available(cwd):
        git_branches = _discover_branches(ticket_key, cwd)
        for branch in git_branches:
            if branch not in branches:
                branches.append(branch)

        git_commits = _discover_commits(ticket_key, cwd)
        for commit in git_commits:
            if commit not in commits:
                commits.append(commit)

        inferred_prs = _discover_prs_from_merge_commits(ticket_key, cwd)
        for pr in inferred_prs:
            if pr not in prs:
                prs.append(pr)
    else:
        gaps.append("Git not available; skipping local branch/commit/PR discovery.")

    # If git_state provided branch/commit is not already in the list, add it
    if git_state:
        current_branch = git_state.get("branch")
        current_commit = git_state.get("commit")
        if current_branch and current_branch not in branches:
            branches.append(current_branch)
        if current_commit and current_commit not in commits:
            commits.append(current_commit)

    # Affected files
    affected_files: list[str] = []
    if infer_by_file:
        text_to_scan = f"{summary}\n{description}"
        affected_files = _extract_affected_files(text_to_scan, cwd)

    # Original feature for bug tickets
    original_feature = _trace_original_feature(ticket_data, ticket_key, cwd)

    # Determine status
    has_tracker_data = any(
        [parent, children, duplicates, linked, blocked_by, blocks, prs, branches, commits]
    )
    has_git_data = bool(branches or commits)
    if not has_tracker_data and not has_git_data and not affected_files:
        status = "blocked"
        gaps.append("No tracker relationship data or git data available.")
    elif gaps:
        status = "partial"
    else:
        status = "complete"

    return {
        "status": status,
        "relationships": {
            "parent": parent,
            "children": children,
            "siblings": siblings,
            "duplicates": duplicates,
            "linked": linked,
            "blocked_by": blocked_by,
            "blocks": blocks,
            "original_feature": original_feature,
            "implementation": {
                "prs": prs,
                "branches": branches,
                "commits": commits,
            },
            "attachments": [
                {"filename": a.get("filename", ""), "summary": a.get("summary", "")}
                for a in attachments
                if isinstance(a, dict)
            ],
            "affected_files": affected_files,
        },
        "gaps": gaps,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Map ticket relationships from normalized ticket data and local git state."
    )
    parser.add_argument(
        "--help-contract",
        action="store_true",
        help="Print the JSON input/output contract and exit.",
    )
    args = parser.parse_args()

    if args.help_contract:
        contract = {
            "input": {
                "ticket_key": "OC-4644",
                "ticket_data": {
                    "key": "OC-4644",
                    "summary": "Auth guard race condition",
                    "description": "Fix in src/app/guards/auth.guard.ts",
                    "labels": ["bug"],
                    "related_tickets": {
                        "parent": "OC-4000",
                        "children": [],
                        "duplicates": [],
                        "linked": ["OC-4500"],
                        "blocked_by": [],
                        "blocks": [],
                    },
                    "dev_info": {"prs": [], "branches": [], "commits": []},
                    "attachments": [],
                },
                "git_state": {"branch": "feature/OC-4644", "commit": "abc1234", "remote": "origin"},
                "codebase_root": ".",
                "infer_by_file": True,
            },
            "output": {
                "status": "complete",
                "relationships": {
                    "parent": "OC-4000",
                    "children": [],
                    "siblings": [],
                    "duplicates": [],
                    "linked": ["OC-4500"],
                    "blocked_by": [],
                    "blocks": [],
                    "original_feature": {"ticket": None, "commit": None, "pr": None},
                    "implementation": {"prs": [], "branches": [], "commits": []},
                    "attachments": [],
                    "affected_files": ["src/app/guards/auth.guard.ts"],
                },
                "gaps": [],
            },
        }
        print(json.dumps(contract, indent=2))
        return

    raw_input = sys.stdin.read()
    if not raw_input.strip():
        raise InputError("No JSON input provided on stdin.")

    try:
        payload = json.loads(raw_input)
    except json.JSONDecodeError as exc:
        raise InputError(f"Invalid JSON input: {exc}")

    if not isinstance(payload, dict):
        raise InputError("Input must be a JSON object.")

    ticket_key = payload.get("ticket_key")
    if not ticket_key:
        raise InputError("ticket_key is required.")

    ticket_data = payload.get("ticket_data", {})
    git_state = payload.get("git_state")
    codebase_root = payload.get("codebase_root", ".")
    infer_by_file = payload.get("infer_by_file", False)

    result = map_relationships(
        ticket_key=ticket_key,
        ticket_data=ticket_data,
        git_state=git_state,
        codebase_root=codebase_root,
        infer_by_file=infer_by_file,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        main()
    except InputError as e:
        print(json.dumps({"status": "error", "errors": [str(e)]}, indent=2))
        sys.exit(2)
    except Exception as e:
        print(json.dumps({"status": "error", "errors": [f"unexpected error: {e}"]}, indent=2))
        sys.exit(1)
