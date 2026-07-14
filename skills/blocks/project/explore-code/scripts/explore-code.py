#!/usr/bin/env python3
"""
explore-code.py

Deterministic codebase exploration script for the explore-code skill.
Reads JSON from stdin, searches the codebase, and returns ranked evidence.

This script does not call LLMs. It uses ripgrep (rg), find, or Python's
built-in directory walk as a fallback. It is intended to be invoked by the
explore-code skill in a conductor workflow.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

DEFAULT_MAX_FILES = 20
DEFAULT_TIME_BOX = 5
DEFAULT_READ_LIMIT = 200
DEFAULT_MIN_RELEVANCE = "Low"

RELEVANCE_SCORES = {"High": 3, "Medium": 2, "Low": 1}

STOP_WORDS = {
    "the", "and", "for", "with", "from", "this", "that", "when", "where",
    "how", "what", "does", "is", "are", "to", "in", "of", "a", "an", "or",
    "as", "it", "be", "by", "on", "at", "during"
}


def extract_keywords(text: str) -> list[str]:
    """Extract meaningful keywords from the summary/question."""
    if not text:
        return []
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    words = cleaned.lower().split()
    keywords = []
    seen = set()
    for w in words:
        if len(w) > 2 and w not in STOP_WORDS and w not in seen:
            seen.add(w)
            keywords.append(w)
    return keywords


def run_cmd(cmd: list[str], cwd: str, timeout: int = 30) -> tuple[int, str, str]:
    """Run a subprocess command and return (returncode, stdout, stderr)."""
    try:
        proc = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout
        )
        return proc.returncode, proc.stdout, proc.stderr
    except Exception as e:
        return 1, "", str(e)


def tool_available(name: str) -> bool:
    """Check whether a CLI tool is available."""
    rc, _, _ = run_cmd(["where", name] if os.name == "nt" else ["which", name], os.getcwd())
    return rc == 0


def search_root(cwd: str, workspace: Optional[str], project_root: Optional[str]) -> str:
    """Determine the root directory to search, respecting workspace scoping."""
    root = project_root or cwd
    if workspace:
        # Prefer workspace relative to project root; fall back to cwd if not found there.
        ws_path = os.path.join(root, workspace)
        if not os.path.isdir(ws_path):
            ws_path = os.path.join(cwd, workspace)
        if os.path.isdir(ws_path):
            root = ws_path
    return root


def find_files_rg(keywords: list[str], cwd: str, workspace: Optional[str], project_root: Optional[str]) -> dict[str, int]:
    """Search for files matching keywords using ripgrep (rg)."""
    results: dict[str, int] = {}
    if not keywords or not tool_available("rg"):
        return results

    root = search_root(cwd, workspace, project_root)
    for kw in keywords:
        cmd = ["rg", "-l", "-i", "--no-heading", "--max-columns", "200", kw, root]
        rc, stdout, _ = run_cmd(cmd, cwd)
        if rc not in (0, 1):
            continue
        for line in stdout.splitlines():
            path = line.strip()
            if not path:
                continue
            abs_path = os.path.abspath(path)
            if os.path.isfile(abs_path):
                results[abs_path] = results.get(abs_path, 0) + 1
    return results


def find_files_python(keywords: list[str], cwd: str, workspace: Optional[str], project_root: Optional[str]) -> dict[str, int]:
    """Fallback file search using Python's os.walk and simple text matching."""
    results: dict[str, int] = {}
    if not keywords:
        return results

    root = search_root(cwd, workspace, project_root)
    exclude_dirs = {".git", "node_modules", ".venv", "venv", "__pycache__", ".pi"}

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        for filename in filenames:
            path = os.path.join(dirpath, filename)
            try:
                if os.path.getsize(path) > 2 * 1024 * 1024:
                    continue
            except OSError:
                continue
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().lower()
            except Exception:
                continue
            score = 0
            for kw in keywords:
                score += content.count(kw)
            if score > 0:
                results[path] = score
    return results


def find_files(keywords: list[str], cwd: str, workspace: Optional[str], project_root: Optional[str]) -> dict[str, int]:
    """Try rg first, then Python fallback."""
    results = find_files_rg(keywords, cwd, workspace, project_root)
    if not results:
        results = find_files_python(keywords, cwd, workspace, project_root)
    return results


def summarize_file(path: str, limit: int = DEFAULT_READ_LIMIT) -> str:
    """Return a short content summary of the file."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()[:limit]
        content = " ".join(line.strip() for line in lines if line.strip())
        if len(content) > 300:
            content = content[:300] + "..."
        return content
    except Exception as e:
        return f"could not read: {e}"


def relevance_label(path: str, score: int, keywords: list[str], is_mentioned: bool) -> str:
    """Assign a relevance label based on mention, keyword density, and path."""
    posix_path = Path(path).as_posix().lower()
    if is_mentioned:
        return "High"
    if score >= 3 and any(kw in posix_path for kw in keywords):
        return "High"
    if score >= 2:
        if "/test" in posix_path or "/tests" in posix_path or "test." in posix_path:
            return "Medium"
        if "/adr" in posix_path or "/docs" in posix_path:
            return "Medium"
        return "Medium"
    return "Low"


def rank_score(label: str, score: int, is_mentioned: bool, is_test_doc: bool) -> int:
    """Produce a tie-break score for sorting."""
    tie = RELEVANCE_SCORES[label] * 100
    if is_mentioned:
        tie += 1000
    tie += min(score, 50)
    if is_test_doc:
        tie -= 5
    return tie


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="explore-code",
        description="Search the codebase for evidence related to a ticket or question."
    )
    parser.add_argument(
        "--input-file",
        "-i",
        type=str,
        default=None,
        help="Path to a JSON file containing input. If omitted, reads JSON from stdin."
    )
    return parser.parse_args()


def normalize_path(path: str, cwd: str) -> str:
    """Return a relative path using forward slashes."""
    try:
        rel = os.path.relpath(path, cwd)
        return rel.replace(os.sep, "/")
    except ValueError:
        return path.replace(os.sep, "/")


def main() -> None:
    args = parse_args()
    start = time.time()

    if args.input_file:
        with open(args.input_file, "r", encoding="utf-8") as f:
            input_data = json.load(f)
    else:
        input_data = json.load(sys.stdin)

    if not isinstance(input_data, dict):
        print(json.dumps({"status": "blocked", "error": "Input must be a JSON object"}, indent=2))
        sys.exit(1)

    ticket_summary = input_data.get("ticket_summary") or input_data.get("question") or ""
    mentioned_files = input_data.get("mentioned_files") or []
    task_type = input_data.get("task_type", "code")
    workspace = input_data.get("workspace") or None
    project_root = input_data.get("project_root") or None
    force = bool(input_data.get("force", False))
    time_box = input_data.get("time_box_minutes", DEFAULT_TIME_BOX)
    max_files = input_data.get("max_files", DEFAULT_MAX_FILES)
    min_relevance = input_data.get("min_relevance", DEFAULT_MIN_RELEVANCE)
    read_limit = input_data.get("read_limit_lines", DEFAULT_READ_LIMIT)

    if not ticket_summary:
        print(json.dumps({
            "status": "needs_input",
            "error": "ticket_summary or question is required"
        }, indent=2))
        sys.exit(0)

    if task_type == "process" and not force:
        print(json.dumps({
            "status": "complete",
            "relevant_files": [],
            "snippets": [],
            "missing_files": [],
            "note": "process tickets skipped by default; set force: true to override"
        }, indent=2))
        sys.exit(0)

    cwd = os.getcwd()
    project_root = project_root or cwd
    mentioned_abs: set[str] = set()
    for mf in mentioned_files:
        p = os.path.abspath(mf) if os.path.isabs(mf) else os.path.abspath(os.path.join(cwd, mf))
        mentioned_abs.add(p)

    keywords = extract_keywords(ticket_summary)
    missing: list[str] = []
    relevant: dict[str, dict] = {}

    # Process mentioned files first
    for mf in mentioned_files:
        p = os.path.abspath(mf) if os.path.isabs(mf) else os.path.abspath(os.path.join(cwd, mf))
        if os.path.isfile(p):
            rel = normalize_path(p, cwd)
            relevant[p] = {
                "path": rel,
                "score": 0,
                "mentioned": True,
                "reason": "explicitly mentioned in ticket",
            }
        else:
            missing.append(mf)

    # Search for keywords if time remains
    time_budget = time_box * 60
    if keywords and (time.time() - start) < time_budget:
        found = find_files(keywords, cwd, workspace, project_root)
        for path, score in found.items():
            if path in mentioned_abs:
                relevant[path]["score"] = max(relevant[path].get("score", 0), score)
                continue
            if path not in relevant:
                rel = normalize_path(path, cwd)
                relevant[path] = {
                    "path": rel,
                    "score": score,
                    "mentioned": False,
                    "reason": f"keyword overlap ({score} matches)",
                }

    # Build ranked list
    ranked = []
    for abs_path, data in relevant.items():
        is_mentioned = data["mentioned"]
        posix_path = Path(abs_path).as_posix()
        is_test_doc = "/test" in posix_path or "/tests" in posix_path or "test." in posix_path or "/adr" in posix_path or "/docs" in posix_path
        label = relevance_label(abs_path, data["score"], keywords, is_mentioned)
        tie = rank_score(label, data["score"], is_mentioned, is_test_doc)
        if RELEVANCE_SCORES[label] < RELEVANCE_SCORES[min_relevance]:
            continue
        ranked.append((label, tie, data["path"], data["reason"], abs_path))

    ranked.sort(key=lambda x: (RELEVANCE_SCORES[x[0]], x[1]), reverse=True)
    ranked = ranked[:max_files]

    relevant_files = [
        {"path": r[2], "relevance": r[0], "reason": r[3]} for r in ranked
    ]
    snippets = [
        {"path": r[2], "content_summary": summarize_file(r[4], limit=read_limit)}
        for r in ranked
    ]

    status = "complete"
    if missing:
        status = "partial"
    if not ranked and not missing:
        status = "partial"

    result = {
        "status": status,
        "relevant_files": relevant_files,
        "snippets": snippets,
        "missing_files": missing
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        main()
    except json.JSONDecodeError as e:
        print(json.dumps({"status": "blocked", "error": f"Invalid JSON input: {e}"}, indent=2))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"status": "blocked", "error": f"Unexpected error: {e}"}, indent=2))
        sys.exit(1)
