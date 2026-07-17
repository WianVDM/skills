#!/usr/bin/env python3
"""
Tests for explore-code.py.

Regression guards:
- relative mentioned_files must resolve against project_root, not the
  process working directory.
- invalid JSON on stdin must print the standard error envelope and exit 2.

Run with:
    python -m pytest skills/blocks/project/explore-code/scripts/tests/
    python skills/blocks/project/explore-code/scripts/tests/test_explore_code.py
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "explore-code.py"


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


# ---------------------------------------------------------------------------
# mentioned_files resolution (regression: resolved against cwd, not project_root)
# ---------------------------------------------------------------------------

def test_relative_mentioned_file_resolves_against_project_root(tmp_path):
    project_root = tmp_path / "repo"
    (project_root / "src").mkdir(parents=True)
    (project_root / "src" / "auth.guard.ts").write_text(
        "export const marker = 1;\n", encoding="utf-8"
    )
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    code, out = run(
        {
            "ticket_summary": "zzz qqq",
            "mentioned_files": ["src/auth.guard.ts"],
            "project_root": str(project_root),
        },
        cwd=str(elsewhere),
    )
    assert code == 0
    assert out["missing_files"] == []
    paths = [f["path"] for f in out["relevant_files"]]
    assert any("auth.guard.ts" in p for p in paths)
    first = out["relevant_files"][0]
    assert first["relevance"] == "High"
    assert out["status"] == "complete"


def test_missing_mentioned_file_reported(tmp_path):
    project_root = tmp_path / "repo"
    project_root.mkdir()
    code, out = run(
        {
            "ticket_summary": "zzz qqq",
            "mentioned_files": ["src/nope.ts"],
            "project_root": str(project_root),
        },
        cwd=str(project_root),
    )
    assert code == 0
    assert "src/nope.ts" in out["missing_files"]
    assert out["status"] == "partial"


# ---------------------------------------------------------------------------
# keyword search
# ---------------------------------------------------------------------------

def test_keyword_search_ranks_hits(tmp_path):
    project_root = tmp_path / "repo"
    project_root.mkdir()
    (project_root / "hits.txt").write_text(
        "billing validation\n" * 10, encoding="utf-8"
    )
    (project_root / "sparse.txt").write_text("billing\n", encoding="utf-8")
    code, out = run(
        {
            "ticket_summary": "billing validation errors",
            "project_root": str(project_root),
        },
        cwd=str(tmp_path),
    )
    assert code == 0
    paths = [f["path"] for f in out["relevant_files"]]
    assert any("hits.txt" in p for p in paths)
    assert "hits.txt" in out["relevant_files"][0]["path"]
    if any("sparse.txt" in p for p in paths):
        hits_idx = next(i for i, p in enumerate(paths) if "hits.txt" in p)
        sparse_idx = next(i for i, p in enumerate(paths) if "sparse.txt" in p)
        assert hits_idx < sparse_idx


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
