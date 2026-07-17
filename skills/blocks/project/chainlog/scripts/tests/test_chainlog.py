#!/usr/bin/env python3
"""
Tests for chainlog.py.

Round-trip tests are the regression guard for the parse-desync data loss:
empty-bodied entries and bodies containing '---' must survive append/query.

Run with:
    python -m pytest skills/blocks/project/chainlog/scripts/tests/
    python skills/blocks/project/chainlog/scripts/tests/test_chainlog.py
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "chainlog.py"


def run(payload: dict):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--json"],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )
    try:
        return proc.returncode, json.loads(proc.stdout)
    except json.JSONDecodeError:
        return proc.returncode, {"_raw": proc.stdout + proc.stderr}


def entry(**overrides):
    base = {
        "work_item_type": "pr",
        "work_item_key": "T-1",
        "capability": "pr-source",
        "source": "test",
        "collected_at": "2020-01-01T00:00:00Z",
        "payload": "an observation",
    }
    base.update(overrides)
    return base


def append(context_dir: Path, e: dict):
    return run({"operation": "append", "context_dir": str(context_dir), "entry": e})


def query_all(context_dir: Path, key: str = "T-1"):
    return run({
        "operation": "query_all", "context_dir": str(context_dir),
        "work_item_type": "pr", "work_item_key": key,
    })


# ---------------------------------------------------------------------------
# parse robustness (regression: silent entry loss)
# ---------------------------------------------------------------------------

def test_empty_bodied_tail_entry_survives(tmp_path):
    append(tmp_path, entry())
    code, out = run({
        "operation": "mark_stale", "context_dir": str(tmp_path),
        "work_item_type": "pr", "work_item_key": "T-1",
        "capability": "pr-source", "reason": "test",
    })
    assert out["status"] == "appended"
    _, all_out = query_all(tmp_path)
    assert all_out["count"] == 2


def test_stale_marker_visible_in_query_latest(tmp_path):
    append(tmp_path, entry())
    run({
        "operation": "mark_stale", "context_dir": str(tmp_path),
        "work_item_type": "pr", "work_item_key": "T-1",
        "capability": "pr-source", "reason": "test",
    })
    _, out = run({
        "operation": "query_latest", "context_dir": str(tmp_path),
        "work_item_type": "pr", "work_item_key": "T-1", "capability": "pr-source",
    })
    latest = out["entries"][0]["frontmatter"]
    assert latest.get("stale") is True


def test_body_with_separator_line_survives(tmp_path):
    tricky = "section one\n\n---\n\nsection two\n\n---\n\nsection three"
    append(tmp_path, entry(payload=tricky))
    append(tmp_path, entry(capability="ci-source", collected_at="2020-01-02T00:00:00Z"))
    _, out = query_all(tmp_path)
    assert out["count"] == 2
    first = [e for e in out["entries"] if e["frontmatter"]["capability"] == "pr-source"][0]
    assert "section one" in first["body"]
    assert "section three" in first["body"]


def test_empty_body_then_normal_entry(tmp_path):
    append(tmp_path, entry(payload=""))
    append(tmp_path, entry(capability="ci-source", collected_at="2020-01-02T00:00:00Z"))
    _, out = query_all(tmp_path)
    assert out["count"] == 2


# ---------------------------------------------------------------------------
# payload handling
# ---------------------------------------------------------------------------

def test_payload_not_duplicated_in_frontmatter(tmp_path):
    append(tmp_path, entry())
    chain = next(tmp_path.rglob("*.chain.md"))
    text = chain.read_text(encoding="utf-8")
    frontmatter_block = text.split("---\n")[1]
    assert "payload" not in frontmatter_block


def test_legacy_frontmatter_payload_normalized(tmp_path):
    chain_dir = tmp_path / "chainlog" / "pr"
    chain_dir.mkdir(parents=True)
    legacy = (
        "---\nwork_item_type: pr\nwork_item_key: T-1\ncapability: pr-source\n"
        "source: test\ncollected_at: '2020-01-01T00:00:00Z'\npayload: legacy body\n"
        "---\n\nlegacy body\n"
    )
    (chain_dir / "T-1.chain.md").write_text(legacy, encoding="utf-8")
    _, out = query_all(tmp_path)
    assert out["count"] == 1
    assert "payload" not in out["entries"][0]["frontmatter"]
    assert out["entries"][0]["body"] == "legacy body"


# ---------------------------------------------------------------------------
# query semantics
# ---------------------------------------------------------------------------

def test_query_latest_returns_max_collected_at(tmp_path):
    append(tmp_path, entry(collected_at="2020-01-01T00:00:00Z", payload="old"))
    append(tmp_path, entry(collected_at="2021-01-01T00:00:00Z", payload="new"))
    _, out = run({
        "operation": "query_latest", "context_dir": str(tmp_path),
        "work_item_type": "pr", "work_item_key": "T-1", "capability": "pr-source",
    })
    assert out["entries"][0]["body"] == "new"


def test_query_since_is_inclusive(tmp_path):
    append(tmp_path, entry(collected_at="2020-06-01T00:00:00Z"))
    _, out = run({
        "operation": "query_since", "context_dir": str(tmp_path),
        "work_item_type": "pr", "work_item_key": "T-1", "since": "2020-06-01T00:00:00Z",
    })
    assert out["count"] == 1


def test_query_missing_chain_not_found(tmp_path):
    code, out = query_all(tmp_path)
    assert out["status"] == "not_found"
    assert out["count"] == 0


def test_exists_reports_count(tmp_path):
    _, out = run({
        "operation": "exists", "context_dir": str(tmp_path),
        "work_item_type": "pr", "work_item_key": "ghost",
    })
    assert out["exists"] is False and out["count"] == 0
    append(tmp_path, entry())
    _, out = run({
        "operation": "exists", "context_dir": str(tmp_path),
        "work_item_type": "pr", "work_item_key": "T-1",
    })
    assert out["exists"] is True and out["count"] == 1


# ---------------------------------------------------------------------------
# input validation and exit codes
# ---------------------------------------------------------------------------

def test_invalid_json_exit_2():
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--json"],
        input="not json", capture_output=True, text=True,
    )
    assert proc.returncode == 2
    assert json.loads(proc.stdout)["status"] == "error"


def test_missing_work_item_fields_exit_2(tmp_path):
    code, out = run({"operation": "query_all", "context_dir": str(tmp_path)})
    assert code == 2
    assert "work_item_type" in out["errors"][0]


def test_unknown_operation_exit_2():
    code, out = run({"operation": "delete_everything"})
    assert code == 2
    assert "unknown operation" in out["errors"][0]


def test_append_missing_required_field(tmp_path):
    code, out = append(tmp_path, {"work_item_type": "pr", "work_item_key": "T-1"})
    assert code == 1
    assert out["status"] == "error"
    assert any("capability" in e for e in out["errors"])


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    with tempfile.TemporaryDirectory() as tmp:
        for test in tests:
            with tempfile.TemporaryDirectory() as inner:
                test(Path(inner))
        print(f"All {len(tests)} tests passed.")


if __name__ == "__main__":
    main()
